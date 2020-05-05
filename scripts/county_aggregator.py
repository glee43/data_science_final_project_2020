import numpy as np
import pandas as pd
import re

city_county_path = "./data/city_county.csv"
gv_path = "./data/joined_agg.csv"

city_county = pd.read_csv(city_county_path)
gv_data = pd.read_csv(gv_path)

def cleaner(col):
    return lambda x: re.sub(r'[^a-z]*', "", x.split("|")[col].lower())

city_county["City"] = city_county.iloc[:,0].map(cleaner(4))
city_county["State"] = city_county.iloc[:,0].map(cleaner(1))
city_county["County"] = city_county.iloc[:,0].map(cleaner(3))

city_county.drop(city_county.columns[0], axis=1)
city_county["City-State"] = city_county.apply(lambda row: row["State"] + "-" + row["City"], axis=1)
city_county["County-State"] = city_county.apply(lambda row: row["State"] + "-" + row["County"], axis=1)

# make a dictionary to map cities to counties
county_mapper = dict(zip(city_county["City-State"], city_county["County-State"]))

# restructure the city data by county
county_data = {}
col_i = {"State":0, "County":1, "Killed": 2, "Injured": 3, "AvgKilled": 4, "AvgInjured": 5, 'Population': 6, "Houses": 7, "LandArea": 8, "PopDensity":9, "HousingPrice":10, "NumIncidents": 11, "NumCities": 12}

for county in set(city_county["County-State"]):
    county_data[county] = [county.split("-")[0],county.split("-")[1],0,0,0,0,0,0,0,0,0,0,0] # there are 13 columns to populate

total_cities = 0
not_found = 0

for i, row in gv_data.iterrows():
    total_cities += 1
    row_city_state = row["State"] + "-" + row["City"]

    # check if it's in the dictionary, then add to the county fields
    if row_city_state in county_mapper:
        row_county_state = county_mapper[row_city_state]
        cols_to_add = ["Killed", "Injured", "Population", "Houses", "LandArea", "PopDensity", "NumIncidents"]
        for col in cols_to_add:
            county_data[row_county_state][col_i[col]] += row[col]
        #add total house value and divided by # houses at the end 
        county_data[row_county_state][col_i["HousingPrice"]] += row["HousingPrice"]*row["Houses"]
        county_data[row_county_state][col_i["NumCities"]] += 1
    else: 
        not_found += 1
        # print(row_city_state)

cityless_counties = 0
counties = 0

# iterate through again to calculate the other columns
for k in list(county_data.keys()):
    counties += 1
    if county_data[k][col_i["NumIncidents"]] > 0:
        county_data[k][col_i["AvgKilled"]] = county_data[k][col_i["Killed"]] / county_data[k][col_i["NumIncidents"]]
        county_data[k][col_i["AvgInjured"]] = county_data[k][col_i["Injured"]] / county_data[k][col_i["NumIncidents"]]
    else:
        county_data[k][col_i["AvgInjured"]] = np.nan
        county_data[k][col_i["AvgKilled"]] = np.nan
    if county_data[k][col_i["LandArea"]] > 0:
        county_data[k][col_i["PopDensity"]] = county_data[k][col_i["Population"]] / county_data[k][col_i["LandArea"]]
    else:
        county_data[k][col_i["PopDensity"]] = np.nan
    if county_data[k][col_i["Houses"]] > 0:
        county_data[k][col_i["HousingPrice"]] = county_data[k][col_i["HousingPrice"]] / county_data[k][col_i["Houses"]]
    else: 
        county_data[k][col_i["HousingPrice"]] = np.nan

    # set to nan if no cities were included in the county
    cols_to_add = ["Killed", "Injured", "Population", "Houses", "LandArea", "PopDensity", "NumIncidents"]
    if county_data[k][col_i["NumCities"]] == 0:
        # print(k)
        county_data.pop(k)
        cityless_counties += 1
        # This code includes as nans instead of deleting
        # for col in cols_to_add:
        #     county_data[k][col_i[col]] = np.nan

print(f'Unable to find a county {not_found}/{total_cities} cities')
print(f'{cityless_counties}/{counties} counties had no cities found and were dropped')


county_df = pd.DataFrame.from_dict(county_data, orient="index", columns=list(col_i.keys()))
county_df.to_csv("./data/county_agg.csv")
