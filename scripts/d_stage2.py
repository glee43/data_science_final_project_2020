# Stage 2: We augment each incident with additional fields.

from argparse import ArgumentParser, Namespace
import asyncio
from collections import defaultdict, namedtuple
from multiprocessing import Pool, cpu_count
from typing import Dict, List, Optional, Tuple, Union, cast
import re
import sys
from time import sleep, time

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
    print(args.input_fname)
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


def _snakify_key(key, prefix=''):
    """
    e.g. snakify_key('Age Group', prefix='participant') -> 'participant_age_group'
    """
    return prefix + key.lower().replace(' ', '_')


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
    return fields


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
            kvpairs = [(_snakify_key(k), v) for k, v in kvpairs]
            for k, v in kvpairs:
                person_fields[k][i] = v

        for field_name, field_values in person_fields.items():
            yield Field(field_name, _stringify_dict(field_values))

        # print(person_fields)


def scrape_incidents(df, chrome_options):
    browser = webdriver.Chrome(options=chrome_options)

    for i in range(1):
        # Unpack the row.
        row = df.loc[i]
        context = IncidentContext(
            address=row['address'],
            city_or_county=row['city_or_county'],
            state=row['state'],
        )
        url = row['incident_url']

        print('Querying')
        browser.get(url)
        # 1. Wait until the page contains meaningful data.
        browser.find_element_or_wait(By.ID, 'block-system-main')

        # 2. Soupify and get incident fields.
        html = browser.page_source
        soup = BeautifulSoup(html, features='html5lib')
        block_system_main = soup.find(id='block-system-main')
        content_divs = [
            block for block in block_system_main.contents if block.name == 'div']

        def find_content_div(title):
            h2 = block_system_main.find('h2', string=title)
            return h2.parent if h2 else None

        location_fields = Scraper.extract_location_fields(find_content_div('Location'), context)
        participant_fields = Scraper.extract_participant_fields(find_content_div('Participants'))
        # for content_div in content_divs:
        #     if content_div.h2.text == 'District':
        #         print(content_div)

        all_fields = [
            *location_fields,
            *participant_fields,
        ]

        print(all_fields)

        # 3. Add incident fields to the row.
        # def field_name(lst):
        #     assert len(set([field.name for field in lst])) == 1
        #     return lst[0].name

        # def field_values(lst):
        #     return [field.value for field in lst]

        # subset = df if predicate is None else df.loc[predicate]
        # if len(subset) == 0:
        #     # No work to do
        #     return df

    sleep(30)
    pass


async def main():
    args = parse_args()

    df = load_input(args)
    print(df)

    options = webdriver.ChromeOptions()
    if args.should_use_headless:
        options.add_argument('--headless')

    scrape_incidents(df, options)

    write_output(args, df)


if __name__ == '__main__':
    print('Running')
    loop = asyncio.get_event_loop()
    try:
        loop.run_until_complete(main())
    finally:
        loop.close()
