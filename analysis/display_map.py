import os

import numpy as np
import csv
import matplotlib.pyplot as plt
from matplotlib import cm
import random
import pandas as pd
import math 
import plotly.graph_objects as go
from scipy import stats

from mpl_toolkits.mplot3d import Axes3D 

cmap = cm.get_cmap('tab10', 10)


def standardized_state(s: str) -> str:
    '''
    :param s: State name or its 2-letter postal code.
    :return: The state's 2-letter postal code.
    '''
    d = {
        "al": "AL",
        "ak": "AK",
        "az": "AZ",
        "ar": "AR",
        "ca": "CA",
        "co": "CO",
        "ct": "CT",
        "de": "DE",
        "fl": "FL",
        "ga": "GA",
        "hi": "HI",
        "id": "ID",
        "il": "IL",
        "in": "IN",
        "ia": "IA",
        "ks": "KS",
        "ky": "KY",
        "la": "LA",
        "me": "ME",
        "md": "MD",
        "ma": "MA",
        "mi": "MI",
        "mn": "MN",
        "ms": "MS",
        "mo": "MO",
        "mt": "MT",
        "ne": "NE",
        "nv": "NV",
        "nh": "NH",
        "nj": "NJ",
        "nm": "NM",
        "ny": "NY",
        "nc": "NC",
        "nd": "ND",
        "oh": "OH",
        "ok": "OK",
        "or": "OR",
        "pa": "PA",
        "ri": "RI",
        "sc": "SC",
        "sd": "SD",
        "tn": "TN",
        "tx": "TX",
        "ut": "UT",
        "vt": "VT",
        "va": "VA",
        "wa": "WA",
        "wv": "WV",
        "wi": "WI",
        "wy": "WY",
        "pr": "PR",
        "dc": "DC"
    }
    return d[s]


def read_data(data, feature_columns):
    """
    Reads the data at the provided files path. 
    :param path: path to dataset
    :return: raw data
    """
    # Load the data set into a 2D numpy array
    grabbed_data = data[feature_columns]
    # drop values with nan
    grabbed_data = grabbed_data.dropna(axis=0)

    # # Calculate z-score for all data points (how many standard deviations away from mean) for each column
    # z = np.abs(stats.zscore(grabbed_data[:, 1]))
    
    # # Find all the rows where all values in each row have a z-score less than 3
    # ind = np.all((z < 3), axis=1)

    # only get data within 3 std
    data_subset = grabbed_data
    
    return data_subset


def visualize_pts(data, feature_columns=["",""]):
    """
    Visualizes the song data points and (optionally) the calculated k-means
    cluster centers.
    Points with the same color are considered to be in the same cluster.

    Optionally providing centroid locations and centroid indices will color the
    data points to match their respective cluster and plot the given centroids.
    Otherwise, only the raw data points will be plotted.

    :param data: 2D numpy array of song data
    :param centroids: 2D numpy array of centroid locations
    :param centroid_indices: 1D numpy array of centroid indices for each data point in data
    :return:
    """
    
    # x, y = np.hsplit(data, 2)
    
    x = data[feature_columns[0]]
    y = data[feature_columns[1]]

    fig = go.Figure(data=go.Choropleth(
        locations=x, # Spatial coordinates
        z=y, # Data to be color-coded
        locationmode = 'USA-states', # set of locations match entries in `locations`
        colorscale = 'Reds',
        colorbar_title = feature_columns[1],
    ))

    fig.update_layout(
        title_text = feature_columns[1],
        geo_scope='usa', # limite map scope to USA
    )

    
    
    plot_name = "/map" + "_" + feature_columns[1] 

    fig.write_image("output/maps" + plot_name + ".png")
    fig.show()
    


if __name__ == '__main__':
    data_path = "../data/joined_agg.csv" 
    
    with open(data_path) as data_file:
        data = pd.read_csv(data_file)

    # change state for the pyplt
    data.loc[:, "State"] = data.loc[:, "State"].apply(standardized_state)

    # aggragate data by state "Killed",  "Injured", "Population", "NumIncidents"
    raw_data = data.groupby('State')["Killed",  "Injured", "Population", "NumIncidents"].sum()
    raw_data['HousingPrice'] = data.groupby('State')["HousingPrice"].mean()
    raw_data['State'] = data.groupby('State').groups.keys()
    
    # add extra fields 
    raw_data['GVRate'] = raw_data['NumIncidents'] / raw_data['Population']
    
   
    feature_columns = ["State","HousingPrice"]
    data = read_data(raw_data, feature_columns)
    visualize_pts(data, feature_columns=feature_columns)