'''
Helper functions used to clean data
'''

import re

def stripSpecial(s):
    '''
    used to make all town,city, and county names
    lower case and only a-z characters so that they
    are easier to match with dirty data
    '''
    if s == None:
        return None
    s = s.lower()
    rex = re.compile(("[^a-z]"))
    stripped = re.sub(rex, "", s)
    return stripped

def

def standardizedState(s):
    '''
    Converts a state name to its postal code, or
    leaves it as is if it is already a postal code.
    '''
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
        "districtofcolumbia": "dc"
        }
    if len(s) == 2:
        return s
    else:
        try:
            abbr = d[s]
            return abbr
        except KeyError:
            return s