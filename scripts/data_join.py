'''
Module used for joining population, house pricing, and gun violence datasets
together. 
'''

import math
import pandas as pd
import argparse
from cleaning import stripSpecial, standardizedState

def load_housing(path):
    housing = pd.read_csv(housing_path, header=0)
    new_rows = []

    for i, j in housing.iterrows():
        city = ""
        state = ""
        # iterate over each column in each row
        for y, x in enumerate(j):
            # The second column contains the city name
            if y == 1:
                # lowercase the city name and make it a-z chars
                city = stripSpecial(x)
            if y == 2:
                state = standardizedState(stripSpecial(y))
            # After column six we get into the monthly price data (starting with 1996-04)
            if y > 5 and not math.isnan(x):
                #calculate the month based on the column
                month = (y-3)%12 + 1
                #calculate the year based on the column
                year = (y-3)//12 + 1994 
                # add row to new dataframe
                row = [city, state, year, month, int(x)]
                new_rows.append(row)
    new_housing = pd.DataFrame(new_rows, columns=["City", "State", "Year", "Month", "HousingPrice"])
    
    return new_housing


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Join multiple datasets")
    
    # paths to data
    housing_path = "../data/housing_city_monthly.csv"
    population_path = "../data/population.csv"
    gun_violence_path = "../data/stage3.csv"

    # load csvs into dataframes
    housing = load_housing(housing_path)
    print(housing.head(20))
    print(housing.index)
    population = pd.read_csv(population_path, header=0)
    gun_violence = pd.read_csv(gun_violence_path, header=0)


