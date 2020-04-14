'''
Performs polymonial regression on gunviolence data
and selects the best fit based on validation data
performance
'''

import numpy
import csv
import pandas as pd
import os
import matplotlib.pyplot as plt
import statsmodels.api as sm


def load_data(path, X_cols, y_col="GVRate", min_pop=10000):
    '''
    Loads in the cleaned gunviolence data and selects the 
    specified fields. Returns a set of independent variables
    and one specified dependent variable.
    Inputs:
    X_cols  - the columns of the dataset that are being used as
              independent variables
    y_col   - the column of the dataset being used as a dependent
              variable
    min_pop - the minimum population needed for a town to be 
              included in the output
    Returns:
    X       - numpy array with the data from the selected rows 
              and columns
    y       - numpy array with the data from the specified row
              and columns
    '''
    df = pd.read_csv(path)

    # add cols
    # calc gv as proportion of population
    df["GVRate"] = df["NumIncidents"]/df["Population"]
    df = df.loc[df["Population"] >= min_pop,:]
    X, y = df[X_cols].values, df[y_col].values
    print(y[:10])
    print(X[:5,:5])

def regression(y_cols, X_cols):
    pass





def viz_regression(X_labels, X_coefficients, y_label):
    pass




if __name__ == "__main__":
    path = "../data/joined_agg.csv"
    load_data(path, ["HousingPrice", "Population"])


