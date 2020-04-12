'''
Helper functions used to clean data
'''

import re


def strip_special(s: str) -> str:
    '''
    used to make all town, city, and county names
    lower case and only a-z characters so that they
    are easier to match with dirty data
    '''
    s = s.lower()
    rex = re.compile(("[^a-z]"))
    stripped = re.sub(rex, "", s)
    return str(stripped)

# ———————————————————————————————————
# Housing Dataset


def clean_housing_region(s: str, col) -> str:
    '''
    Used to clean the RegionName into a usable city name.
    '''
    out = strip_special(s)

    # Format 'Town of' instances
    whitelist = ['townofpines']
    if out.startswith('townof') and out not in whitelist:
        out = out[6:]

    return out

# ———————————————————————————————————
# Population Dataset


def clean_pop_city_county(s):
    '''
    Extracts the city name from the population dataset.
    The column with the city data is formatted as either
    (city, county), or just (city), or just (county) and is 
    not consistent. 
    City names have either "town", "city", or "CDP" appended
    to their names depending on their designation
    '''
    city = s.split(",")[0]
    suffix = city.split(" ")[-1]
    suffix = strip_special(suffix)
    city = strip_special(city)

    # If the suffix is one of these place designations, remove it.
    place_designations_crop = ['cdp', 'government', 'village', 'urbana', 'gore', 'corporation', 'town',
                               'plantation', 'city', 'grant', 'location', 'borough', 'comunidad', 'purchase', 'municipality']

    out = city
    if suffix is 'county' or suffix is 'countypart':
        out = 'POPCOUNTYDATA'
    elif suffix in place_designations_crop:
        out = city[:-len(suffix)]

    if out == 'autaugacountypart':
        print(s)
        print(city)
        print(suffix)

    return out


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
    is_county_name = s.endswith("(county)") or (
        len(s) > 7 and s.endswith(" County"))
    if is_county_name:
        return 'GZCOUNTYDATA'

    city = strip_special(s)
    out = city
    redlist = ['plaintownship', 'argentinetownship', 'statenisland', 'sunsetharbor', 'thornebay', 'kendallpark', 'larimer', 'pottsgrove', 'newcaney',
               'orangemound', 'searingtown', 'baypoint', 'jamescity', 'virgie', 'eastamherst', 'canandaigua', 'sandoval', 'meally', 'daltontownship', 'hamptonbeach']

    neighborhood_match = re.compile(r'^([\w\s\.]+) \(([\w\s\.]+)\)$').match(s)
    if neighborhood_match:
        left, right = neighborhood_match.groups()
        # print(f'left: "{left}", right: "{right}"')

        # Usually, LEFT is the city name, and RIGHT is the inner neighborhood.
        # There are some explicit exceptions that will be recognized here:
        especial_cities = ["Manchester", "Chincoteague"]
        if right in especial_cities:
            out = strip_special(right)
        else:
            out = strip_special(left)

    # Certain values will be manually overwritten (boroughs -> cities, etc.)
    exception_dict = {
        'statenisland': 'newyorkcity'
    }
    if out in exception_dict.keys():
        out = exception_dict[out]

    # if out in redlist:
    #     print('REDLIST')
    #     print(f'{s} | {out} | {bool(neighborhood_match)}')

        # if city in redlist:
        #     print(f'original string: {s}')
        #     if neighborhood_match:
        #         left, right = neighborhood_match.groups()
        #         print(f'left: "{left}", right: "{right}"')

        #         # Usually, LEFT is the city name, and RIGHT is the inner neighborhood.
        #         # There are some explicit exceptions that will be recognized here:
        #         especial_cities = ["Manchester"]
        #         if right in especial_cities:
        #             out = strip_special(right)
        #         else:
        #             out = strip_special(left)
        #     print(f'out: "{out}"')
        #     print('—————')

        # city = strip_special(s)
        # redlist = ['orchardpark', 'louisvillesaintmatthews', 'minneapolisedina',
        #     'chevak', 'brattleboroguilford', 'hopevalley', 'mckeesportportvue',
        #     'saintmarysstmarys', 'greenvilleadamsville', 'alpharettajohnscreek',
        #     'junedale', 'upperstclair', 'ballwinmanchester', 'redwoodestates',
        #     'mountjulietmtjuliet', 'birminghamensley', 'zunizunipueblo', 'portercorners',
        #     'sixmilerun', 'lakewoodjointbaselewismcchord']
        # if city in redlist:
        #     print(s, city)

    return out


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
