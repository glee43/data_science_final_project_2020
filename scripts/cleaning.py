'''
Helper functions used to clean data
'''

import sys
import re


def strip_special(s: str) -> str:
    '''
    used to make all town, city, and county names
    lower case and only a-z characters so that they
    are easier to match with dirty data
    '''
    s = s.lower()
    rex = re.compile(("[^a-z]"))
    stripped = str(re.sub(rex, "", s))
    return stripped


def correct_city_name(city_name: str) -> str:
    '''
    Fix typos and replace special strings with their proper city names.
    '''
    out = city_name

    # Correct typos
    out = out.replace('twnshp', 'township')
    out = out.replace('twp', 'township')

    # Simplify charter townships to townships
    out = out.replace('chartertownship', 'township')

    # Certain cities will have their 'township' suffix removed for uniformity
    townships_remove_suffix = ['redfordtownship']
    if out in townships_remove_suffix:
        out = out[0:-len('township')]

    # Certain names will be manually overwritten (neighborhoods -> cities, etc.)
    exception_dict = {
        'districtofcolumbia': 'washingtondc',
        'statenisland': 'newyorkcity',
        'coneyisland': 'newyorkcity',
        'jointbaseelmendorfrichardson': 'anchorage',
    }

    if out in exception_dict.keys():
        out = exception_dict[out]

    return out


# ———————————————————————————————————
# Housing Dataset


def clean_housing_city(s: str, col) -> str:
    '''
    Used to clean the RegionName into a usable city name.
    '''
    out = strip_special(s)

    # Format 'Town of' instances
    whitelist = ['townofpines']
    if out.startswith('townof') and out not in whitelist:
        out = out[6:]

    return correct_city_name(out)

# ———————————————————————————————————
# Population Dataset


def clean_pop_city_county(s: str) -> str:
    '''
    Extracts the city name from a field in theh population dataset.
    The column with the city data is formatted as either
    (city, county), or just (city), or just (county) and is 
    not consistent. 
    City names have either "town", "city", or "CDP" appended
    to their names depending on their designation

    :param s: String in example format 'Alabama - PLACE - Arab city - Marshall County (part)'
    :return: Formatted city name
    '''
    if s.find('PLACE') == -1:
        # It's a state; return 'POPSTATEDATA'.
        return 'POPSTATEDATA'

    # Remove prefix "<state> - PLACE - "
    place_idx = s.find('PLACE - ')
    place_next_idx = place_idx + len('PLACE - ')
    division_idx = s.find('DIVISION - ')
    division_next_idx = division_idx + len('DIVISION - ')

    s = s[division_next_idx:] if division_idx != -1 else s[place_next_idx:]

    # Remove suffix with county info
    raw_city = s
    if s.find(' - ') != -1:
        raw_city = s.split(' - ')[0]
    elif s.find(', ') != -1:
        raw_city = s.split(', ')[0]

    # Remove parenthetical suffix, if exists
    match = re.compile(r'([\w\s-]+) (\([\w\s-]+\))').match(raw_city)
    if match:
        # pass
        raw_city = match.group(1)

    suffix = raw_city.split(" ")[-1]
    suffix = strip_special(suffix)
    city = strip_special(raw_city)

    # If the suffix is one of these place designations, remove it.
    place_designations_crop = ['cdp', 'government', 'village', 'urbana', 'gore', 'corporation', 'town',
                               'plantation', 'city', 'grant', 'location', 'borough', 'comunidad', 'purchase', 'municipality']

    out = city
    if suffix is 'county' or suffix is 'countypart':
        out = 'POPCOUNTYDATA'
    elif suffix in place_designations_crop:
        out = city[:-len(suffix)]

    if out == 'aaronsburgcdpcentrecounty':
        print('!!')
        print(s)
        print(raw_city)
        print(city)
        print(suffix)
        print(out)

    return correct_city_name(out)


def clean_pop_int(i):
    '''
    Some population fields have additional info in 
    parentheses
    '''
    pop = int(i.split("(")[0])
    return pop


def clean_pop_float(i) -> float:
    '''
    Some population density fields are undefined because
    they have no land area, so their density info 
    appears as (X). This function will map non float
    values to -1.
    '''
    try:
        f = float(i)
        return f
    except ValueError:
        return -1.0

# ———————————————————————————————————
# GV Dataset


def clean_gv_city(s: str) -> str:
    '''
    Clean the city/county/borough data into a standardized city string.
    '''
    is_county_name = s.endswith("(county)") or (s.endswith(" County") and len(s) > 7)
    if is_county_name:
        return 'GZCOUNTYDATA'

    city = strip_special(s)
    out = city

    # Match for strings in the format "<city> (<neighborhood>)".
    neighborhood_match = re.compile(r'^([\w\s\.]+) \(([\w\s\.]+)\)$').match(s)
    if neighborhood_match:
        left, right = neighborhood_match.groups()

        # Usually, LEFT is the city name, but there are exceptions.
        especial_cities = ["Manchester", "Chincoteague"]
        if right in especial_cities:
            out = strip_special(right)
        else:
            out = strip_special(left)

    return correct_city_name(out)


def standardized_state(s: str) -> str:
    '''
    :param s: State name or its 2-letter postal code.
    :return: The state's 2-letter postal code.
    '''
    s = strip_special(s)
    d = {
        "alabama": "al",
        "alaska": "ak",
        "arizona": "az",
        "arkansas": "ar",
        "california": "ca",
        "colorado": "co",
        "connecticut": "ct",
        "delaware": "de",
        "florida": "fl",
        "georgia": "ga",
        "hawaii": "hi",
        "idaho": "id",
        "illinois": "il",
        "indiana": "in",
        "iowa": "ia",
        "kansas": "ks",
        "kentucky": "ky",
        "louisiana": "la",
        "maine": "me",
        "maryland": "md",
        "massachusetts": "ma",
        "michigan": "mi",
        "minnesota": "mn",
        "mississippi": "ms",
        "missouri": "mo",
        "montana": "mt",
        "nebraska": "ne",
        "nevada": "nv",
        "newhampshire": "nh",
        "newjersey": "nj",
        "newmexico": "nm",
        "newyork": "ny",
        "northcarolina": "nc",
        "northdakota": "nd",
        "ohio": "oh",
        "oklahoma": "ok",
        "oregon": "or",
        "pennsylvania": "pa",
        "rhodeisland": "ri",
        "southcarolina": "sc",
        "southdakota": "sd",
        "tennessee": "tn",
        "texas": "tx",
        "utah": "ut",
        "vermont": "vt",
        "virginia": "va",
        "washington": "wa",
        "westvirginia": "wv",
        "wisconsin": "wi",
        "wyoming": "wy",
        "puertorico": "pr",
        "districtofcolumbia": "dc",
        "southdakota": "sd",
        "tennessee": "tn",
        "texas": "tx",
        "utah": "ut",
        "vermont": "vt",
        "virginia": "va",
        "washington": "wa",
        "westvirginia": "wv",
        "wisconsin": "wi",
        "wyoming": "wy",
        "puertorico": "pr",
        "districtofcolumbia": "dc",
        "southdakota": "sd",
        "tennessee": "tn",
        "texas": "tx",
        "utah": "ut",
        "vermont": "vt",
        "virginia": "va",
        "washington": "wa",
        "westvirginia": "wv",
        "wisconsin": "wi",
        "wyoming": "wy",
        "puertorico": "pr",
        "districtofcolumbia": "dc",
        "southdakota": "sd",
        "tennessee": "tn",
        "texas": "tx",
        "utah": "ut",
        "vermont": "vt",
        "virginia": "va",
        "washington": "wa",
        "westvirginia": "wv",
        "wisconsin": "wi",
        "wyoming": "wy",
        "puertorico": "pr",
        "districtofcolumbia": "dc",
    }
    if len(s) == 2:
        return s
    else:
        try:
            abbr = d[s]
            return abbr
        except KeyError:
            return s
