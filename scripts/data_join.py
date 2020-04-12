'''
Module used for joining population, house pricing, and gun violence datasets
together. 
'''

import math
import pandas as pd
import argparse
import cleaning
import numpy as np
import csv


def load_housing(path):
    '''
    Loads the housing data csv.
    :returns: DataFrame with columns ["State", "City", "Year", "Month", "HousingPrice"]
    '''
    housing = pd.read_csv(housing_path, header=0)

    # Clean data into new_rows
    new_rows = []
    for i, col in housing.iterrows():
        city = ""
        state = ""
        # Iterate over each column in each row
        for y, x in enumerate(col):
            # The second column ('RegionName') contains the city name
            if y == 1:
                # lowercase the city name and make it a-z chars
                city = cleaning.clean_housing_city(x, col)
            if y == 2:
                state = cleaning.standardized_state(x)
            # After column six we get into the monthly price data (starting with 1996-04)
            if y > 5 and not math.isnan(x):
                # calculate the month based on the column
                month = (y-3) % 12 + 1
                # calculate the year based on the column
                year = (y-3) // 12 + 1994
                # add row to new dataframe
                row = [city, state, year, month, int(x)]
                new_rows.append(row)

    # Load new_rows into df
    new_housing = pd.DataFrame(
        new_rows, columns=["City", "State", "Year", "Month", "HousingPrice"])
    new_housing = new_housing[new_housing["Year"] > 2013]
    new_housing = new_housing[(new_housing["Year"] < 2018) | ((new_housing["Month"] < 4) & (new_housing["Year"] == 2018))]


    cols = ["State", "City", "Year", "Month", "HousingPrice"]
    new_housing = new_housing[cols]

    return new_housing


def load_population(path):
    '''
    Loads the population data csv.
    :returns: DataFrame with columns ["State", "City", "Population", "Houses", "TotalArea", "LandArea", "PopDensity", "HouseDensity"]
    '''
    raw_data = pd.read_csv(population_path, header=1)
    cols = ["State", "City", "Population", "Houses",
            "TotalArea", "LandArea", "PopDensity", "HouseDensity"]
    # extract important columns
    data = raw_data.iloc[:, [2, 5, 7, 8, 9, 11, 12, 13]]
    data.columns = cols
    # clean all the columns
    data.loc[:, "State"] = data.loc[:, "State"].apply(
        cleaning.standardized_state)
    data.loc[:, "City"] = data.loc[:, "City"].apply(
        cleaning.clean_pop_city_county)
    for i in ["Population", "Houses"]:
        data.loc[:, i] = data.loc[:, i].apply(cleaning.clean_pop_int)
    for i in ["TotalArea", "LandArea", "PopDensity", "HouseDensity"]:
        data.loc[:, i] = data.loc[:, i].apply(cleaning.clean_pop_float)
    # discard areas of no land
    data = data.loc[data["LandArea"] > 0]

    return data


def load_gun_violence(path):
    '''
    Loads the gunviolence data csv.
    :returns: DataFrame
    '''
    raw_data = pd.read_csv(gun_violence_path, header=0)
    data = raw_data.loc[:, ["date", "state",
                            "city_or_county", "n_killed", "n_injured"]]
    cols = ["Year", "State", "City", "Killed", "Injured"]
    data.columns = cols
    data["Month"] = data["Year"]
    # clean the columns
    data.loc[:, "State"] = data.loc[:, "State"].apply(
        cleaning.standardized_state)
    data.loc[:, "City"] = data.loc[:, "City"].apply(cleaning.clean_gv_city)
    for i in ["Killed", "Injured"]:
        data.loc[:, i] = data.loc[:, i].apply(lambda x: int(x))
    # discard county data
    data = data.loc[data["City"] != "COUNTYDATA"]
    # break data into month, year fields
    data.loc[:, "Month"] = data.loc[:, "Month"].apply(
        lambda x: int(x.split("-")[1]))
    data.loc[:, "Year"] = data.loc[:, "Year"].apply(
        lambda x: int(x.split("-")[0]))

    # reorder cols
    cols = ["State", "City", "Year", "Month", "Killed", "Injured"]
    data = data[cols]
    data = data.loc[data["Year"] > 2013]

    return data


def analyze_david(housing, population, gun_violence) -> None:
    """
    Random fns
    """
    hoc = set(housing['City'].tolist())
    ppc = set(population['City'].tolist())
    gvc = set(gun_violence['City'].tolist())

    # Also worth thinking about: cities that have same names as counties and vice versa?

    dropped_h_gv_from_gv = sorted(gvc.difference(hoc))
    dropped_h_gv_from_h = sorted(hoc.difference(gvc))

    dropped_h_p_from_p = sorted(ppc.difference(hoc))
    dropped_h_p_from_h = sorted(hoc.difference(ppc))

    # Write to txt file.
    with open('david_analysis.txt', 'w+') as f:
        f.write(f"""
=== Numbers ===
City counts: h: {len(hoc)}, p: {len(ppc)}, gv: {len(gvc)}
(This obscures instances where different states have the same city name)

=== Numbers: Set Intersection ===
Total intersection: {len(hoc.intersection(ppc).intersection(gvc))}
h/gv: {len(hoc.intersection(gvc))}
h/p: {len(hoc.intersection(ppc))}
p/gv: {len(ppc.intersection(gvc))}

dropped_h_gv_from_gv: {len(dropped_h_gv_from_gv)}
dropped_h_gv_from_h: {len(dropped_h_gv_from_h)}

dropped_h_p_from_p: {len(dropped_h_p_from_p)}
dropped_h_p_from_h: {len(dropped_h_p_from_h)}

=== Samples: Set Differences ===

H/GV difference in GV: {list(dropped_h_gv_from_gv)[1 :: len(dropped_h_gv_from_gv) // 25]}

H/GV difference in H: {list(dropped_h_gv_from_h)[1 :: len(dropped_h_gv_from_h) // 25]}

———

H/P difference in P: {list(dropped_h_p_from_p)[1 :: len(dropped_h_p_from_p) // 25]}

H/P difference in H: {list(dropped_h_p_from_h)[1 :: len(dropped_h_p_from_h) // 25]}

=== Raw data ===

——— dropped_h_gv_from_gv ---
{' '.join(list(dropped_h_gv_from_gv))}

---dropped_h_gv_from_h ---
{' '.join(list(dropped_h_gv_from_h))}
        """)

        # f.write('=== Numbers ===')
        # f.write(f'City counts: h: {len(hoc)}, p: {len(ppc)}, gv: {len(gvc)}')
        # f.write(
        #     f'(This obscures instances where different states have the same city name)')
        # f.write('\n')
        # f.write('=== Numbers: Set Intersection ===')
        # f.write(
        #     f'Total intersection: {len(hoc.intersection(ppc).intersection(gvc))}')
        # f.write(f'h/gv: {len(hoc.intersection(gvc))}')
        # f.write(f'h/p: {len(hoc.intersection(ppc))}')
        # f.write(f'p/gv: {len(ppc.intersection(gvc))}')
        # f.write('\n')

    pass


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Join multiple datasets")
    parser.add_argument("--monthly", help="Compile the data with a monthly resolution",
                        action="store_true")
    parser.add_argument("--yearly", help="Compile the data with a yearly resoultion",
                        action="store_true")
    args = parser.parse_args()

    # paths to data
    housing_path = "../data/housing_city_monthly.csv"
    population_path = "../data/population.csv"
    gun_violence_path = "../data/stage3.csv"
    save_path = "../data/joined"
    if args.monthly:
        save_path += "_monthly.csv"
    elif args.yearly:
        save_path += "_yearly.csv"
    else:
        save_path += "_agg.csv"

    # load csv's into dataframes
    housing = load_housing(housing_path)
    population = load_population(population_path)
    gun_violence = load_gun_violence(gun_violence_path)

    # David's Analysis
    analyze_david(housing, population, gun_violence)

    # joining housing and gv on ["State", "City", "Month", "Year"] resulting in table ["State", "City", "Year", "Month", "HousingPrice", "Killed", "Injured"]
    housing_gv_joined = housing.merge(gun_violence, left_on=["State", "City", "Month", "Year"], right_on=[
                                      "State", "City", "Month", "Year"], how="left")

    # joining housing_gv_joined and population on  ["State", "City"]
    housing_gv_population_joined = housing_gv_joined.merge(
        population, left_on=["State", "City"], right_on=["State", "City"], how="inner")

    group_on = ["State", "City"]
    if args.monthly:
        group_on.append("Year")
        group_on.append("Month")
    elif args.yearly:
        group_on.append("Year")

    condensed_dataset = pd.DataFrame()

    # compute the columns that are sums
    condensed_dataset_sums = housing_gv_population_joined.groupby(group_on)[
        "Killed", "Injured"].sum()
    # compute the columns that are means
    condensed_dataset_avgs = housing_gv_population_joined.groupby(
        group_on)["Killed", "Injured", "Population", "Houses", "TotalArea", "LandArea"].mean()
    condensed_dataset_avgs.rename(
        columns={"Killed": "AvgKilled", "Injured": "AvgInjured"}, inplace=True)
    # join sums an dmeans
    condensed_data = condensed_dataset_sums.merge(condensed_dataset_avgs, on=group_on, how="inner")
    condensed_data.reset_index()
    # compute the columns that are counts
    condensed_dataset_counts = housing_gv_population_joined.groupby(group_on, as_index=False)[ "Killed"].count()
    condensed_dataset_counts.rename(columns = {"Killed":"NumIncidents"}, inplace=True)
