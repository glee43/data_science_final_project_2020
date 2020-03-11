# Stage 2: We augment each incident with additional fields.

from argparse import ArgumentParser, Namespace
import asyncio
from collections import defaultdict, namedtuple
import multiprocessing as mp
from multiprocessing import Pool, cpu_count
from typing import Dict, List, Optional, Tuple, Union, cast
import re
import sys
from time import sleep, time
from urllib.parse import parse_qs, urlparse

import selenium_utils

import numpy as np
import pandas as pd
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
# from selenium.webdriver import Chrome


SCHEMA = {
    'congressional_district': np.float64,
    'state_house_district': np.float64,
    'state_senate_district': np.float64,
    'n_guns_involved': np.float64,
}

ALL_FIELD_NAMES = sorted([
    'latitude',
    'longitude',
    'location_description',

    'participant_type',
    'participant_name',
    'participant_age',
    'participant_age_group',
    'participant_gender',
    'participant_status',
    'participant_relationship',

    'incident_characteristics',

    'notes',

    'n_guns_involved',
    'gun_type',
    'gun_stolen',

    'sources',

    'congressional_district',
    'state_senate_district',
    'state_house_district'
])

# —————
# Utility functions


IncidentContext = namedtuple('Context', ['address', 'city_or_county', 'state'])
Field = namedtuple('Field', ['name', 'value'])


def chunks(n, lst):
    """Yield successive n-sized chunks from lst."""
    for i in range(0, len(lst), n):
        yield lst[i:i + n]

# —————


def parse_args() -> Namespace:
    parser = ArgumentParser()

    # Required args

    parser.add_argument(
        'input_fname',
        metavar='INPUT',
        help='Path to input file.',
    )
    parser.add_argument(
        'output_fname',
        metavar='OUTPUT',
        help='Path to output file.',
    )

    # Optional args

    parser.add_argument(
        '-H', '--headless',
        help='Launch Chrome in headless mode, removing pop-up window and saving time',
        action='store_true',
        dest='should_use_headless',
    )

    args = parser.parse_args()
    return args


def load_input(args):
    return pd.read_csv(
        args.input_fname,
        dtype=SCHEMA,
        parse_dates=['date'],
        encoding='utf-8',
    )


def write_output(args, df) -> None:
    df.to_csv(
        args.output_fname,
        index=False,
        float_format='%g',
        encoding='utf-8',
    )


def _supplement_next_url(next_url: str, current_url: str) -> str:
    """
    Arguments:
        next_url — Must not have any query params.

    If current_url has any session tokens as query params, returns next_url with those session
    tokens included.
    """
    question_mark_idx = current_url.find('?')

    if question_mark_idx == -1:
        new_next_url = next_url
    else:
        new_next_url = next_url.replace('http://', 'https://') + current_url[question_mark_idx:]

    print(new_next_url)
    print()
    return new_next_url


def _snakify_key(key, prefix=''):
    """
    e.g. snakify_key('Age Group', prefix='participant_') -> 'participant_age_group'
    """
    return prefix + key.lower().replace(' ', '_')


def _stringify_list(lst, sep='||'):
    violation = next((item for item in lst if sep in item), None)
    assert violation is None, "List item {} contains the separator string {}".format(
        repr(violation), repr(sep))
    return sep.join(lst)


def _stringify_dict(d, dictsep='::', listsep='||'):
    """
    e.g. stringify_dict({ 'foo': 'bar', 0: 1 }) -> 'foo::bar||0::1'
    """
    keys, values = list(map(str, d.keys())), list(map(str, d.values()))
    key_violation = next((key for key in keys if dictsep in key or listsep in key), None)
    value_violation = next((val for val in values if dictsep in val or listsep in val), None)
    assert key_violation is None and value_violation is None, \
        "Key {} or value {} contains the separator string(s) {} or {}".format(
            repr(key_violation), repr(value_violation), repr(dictsep), repr(listsep))

    return listsep.join([dictsep.join([k, v]) for k, v in zip(keys, values)])


def _normalize(fields: List[Field]) -> List[Field]:
    # Ensure that the fields are alphabetically ordered by field name.
    fields = sorted(fields, key=lambda f: f.name)

    # Validate field names.
    field_names_and_values = [field for field in zip(*fields)]
    field_names = set(field_names_and_values[0])

    unexpected_field_names = field_names - set(ALL_FIELD_NAMES)
    assert len(unexpected_field_names) == 0, f'Unexpected field names: {unexpected_field_names}'

    # Add dummy fields for missing field names.
    i = 0
    for name in ALL_FIELD_NAMES:
        if name not in field_names:
            dummy = Field(name, None)
            fields.insert(i, dummy)
        i += 1

    # Since `fields` has a known length, it's more appropriate to use a tuple.
    return tuple(fields)


class Scraper(object):
    """
    Static class.
    """

    @staticmethod
    def extract_location_fields(content_div: Union[BeautifulSoup, None], context: IncidentContext):
        if content_div is None:
            return

        def check_is_city_and_state(text):
            return ',' in text and text.endswith(context.state)

        def check_is_address(text):
            # The address on the incident page usually, but not always, matches the address on the query page.
            return text == context.address or \
                re.search(r'^[0-9]+[0-9a-z-]*\b', text, re.I) or \
                re.search(
                    r'\b(st|street|rd|road|dr|drive|blvd|boulevard|ave|avenue|hwy|highway)\.?$', text, re.I)

        for span in content_div.select('span'):
            text = span.text
            if not text:
                continue

            match = re.search(r'^Geolocation:\s+(.*),\s+(.*)$', text)
            if match:
                latitude, longitude = float(match.group(1)), float(match.group(2))
                yield Field('latitude', latitude)
                yield Field('longitude', longitude)
            elif check_is_city_and_state(text) or check_is_address(text):
                # Nothing to be done. City, state, & address fields were extracted already.
                pass
            else:
                yield Field('location_description', text)

    @staticmethod
    def extract_participant_fields(content_div: Union[BeautifulSoup, None]):
        if content_div is None:
            return

        linegroups = [[li.text for li in ul.select('li')] for ul in content_div.select('ul')]

        person_fields = defaultdict(dict)
        for i, linegroup in enumerate(linegroups):
            linegroup = linegroups[i]
            kvpairs = [line.split(':') for line in linegroup]
            kvpairs = [(k.strip(), v.strip()) for k, v in kvpairs]
            kvpairs = [(_snakify_key(k, prefix='participant_'), v) for k, v in kvpairs]
            for k, v in kvpairs:
                person_fields[k][i] = v

        for field_name, field_values in person_fields.items():
            yield Field(field_name, _stringify_dict(field_values))

    @staticmethod
    def extract_guns_involved_fields(div: Union[BeautifulSoup, None]):
        if div is None:
            return

        # n_guns_involved
        p_text = div.select_one('p').text
        match = re.search(r'^([0-9]+)\s+guns?\s+involved.$', p_text)
        assert match, "<p> text did not match expected pattern: {}".format(p_text)
        n_guns_involved = int(match.group(1))
        yield Field('n_guns_involved', n_guns_involved)

        # List attributes
        linegroups = [[li.text for li in ul.select('li')] for ul in div.select('ul')]
        gun_fields = defaultdict(dict)

        for i, linegroup in enumerate(linegroups):
            linegroup = linegroups[i]
            kvpairs = [line.split(':') for line in linegroup]
            kvpairs = [(k.strip(), v.strip()) for k, v in kvpairs]
            kvpairs = [(_snakify_key(k, prefix='gun_'), v) for k, v in kvpairs]
            for k, v in kvpairs:
                gun_fields[k][i] = v

        for field_name, field_values in gun_fields.items():
            yield Field(field_name, _stringify_dict(field_values))

    @staticmethod
    def extract_district_fields(div: Union[BeautifulSoup, None]):
        if div is None:
            return

        # The text we want to scrape is orphaned (no direct parent element), so we can't get at it directly.
        # Fortunately, each important line is followed by a <br> element, so we can use that to our advantage.
        # NB: The orphaned text elements are of type 'NavigableString'
        lines = [str(br.previousSibling).strip() for br in div.select('br')]
        for line in lines:
            kvpairs = line.split(':')
            k, v = (kvpairs[0].strip(), kvpairs[1].strip())
            k, v = (_snakify_key(k), v)
            yield Field(k, v)

    @staticmethod
    def extract_incident_characteristics(content_div: Union[BeautifulSoup, None]):
        if content_div is None:
            return
        return _stringify_list([li.text for li in content_div.select('li')])

    @staticmethod
    def extract_notes(div: Union[BeautifulSoup, None]):
        if div is None:
            return
        return div.select_one('p').text

    @staticmethod
    def extract_sources(div: Union[BeautifulSoup, None]):
        if div is None:
            return None

        anchors = [a for a in div.select('a') if a.text == a['href']]
        return _stringify_list([a['href'] for a in anchors])


def scrape_incidents(df, chrome_options):
    """
    Cracks open a new Chrome browser to extract incident data based on the URL in every field in 
    the dataframe.
    """
    browser = webdriver.Chrome(options=chrome_options)

    new_df = pd.DataFrame([], columns=[*df.columns, *ALL_FIELD_NAMES])
    print(new_df)

    for i in df.index.values:
        sleep(2)
        # Unpack the row.
        row = df.loc[i]
        context = IncidentContext(
            address=row['address'],
            city_or_county=row['city_or_county'],
            state=row['state'],
        )

        # Get incident URL.
        url = row['incident_url']
        if browser.current_url.find('http') != -1:
            url = _supplement_next_url(url, browser.current_url)

        print('Querying')
        browser.get(url)
        # 1. Wait until the page contains meaningful data.
        browser.find_element_or_wait(By.ID, 'block-system-main')

        # 2. Soupify and get incident fields.
        html = browser.page_source
        soup = BeautifulSoup(html, features='html5lib')
        block_system_main = soup.find(id='block-system-main')

        def find_content_div(title):
            h2 = block_system_main.find('h2', string=title)
            return h2.parent if h2 else None

        location_fields = Scraper.extract_location_fields(find_content_div('Location'), context)
        participant_fields = Scraper.extract_participant_fields(
            find_content_div('Participants'))
        guns_involved_fields = Scraper.extract_guns_involved_fields(
            find_content_div('Guns Involved')
        )
        district_fields = Scraper.extract_district_fields(
            find_content_div('District')
        )

        incident_characteristics = Scraper.extract_incident_characteristics(
            find_content_div('Incident Characteristics')
        )
        notes = Scraper.extract_notes(find_content_div('Notes'))
        sources = Scraper.extract_sources(find_content_div('Sources'))

        all_fields = [
            *location_fields,
            *participant_fields,
            *guns_involved_fields,
            *district_fields,
            Field('incident_characteristics', incident_characteristics),
            Field('notes', notes),
            Field('sources', sources),
        ]

        # 3. Add incident fields to the row.
        fields = _normalize(all_fields)

        # Temporarily suppress Pandas' SettingWithCopyWarning
        pd.options.mode.chained_assignment = None
        try:
            for field_name, field_values in fields:
                row[field_name] = field_values

            new_df = new_df.append(row)
        finally:
            pd.options.mode.chained_assignment = 'warn'

    sleep(3)
    return new_df


def main():
    args = parse_args()

    df = load_input(args)

    options = webdriver.ChromeOptions()
    if args.should_use_headless:
        options.add_argument('--headless')

    # new_df = scrape_incidents(df, options)

    def split(a, n):
        k, m = divmod(len(a), n)
        return (a[i * k + min(i, m):(i + 1) * k + min(i + 1, m)] for i in range(n))

    # print(list(split(df, mp.cpu_count() - 1)))

    # num_threads = mp.cpu_count() - 1
    num_threads = 3
    df = df[:num_threads * 4]
    dfs = list(split(df, num_threads))
    args_list = [(df, options) for df in dfs]

    # with mp.Pool(num_threads) as pool:
    with mp.Pool(num_threads) as pool:
        result = pool.starmap(scrape_incidents, args_list)

    print('Done scraping. Now writing.')

    new_df = pd.concat(result)
    write_output(args, new_df)
    print('Wrote.')


if __name__ == '__main__':
    print('Running')
    main()
    # loop = asyncio.get_event_loop()
    # try:
    #     loop.run_until_complete(main())
    # finally:
    #     loop.close()
