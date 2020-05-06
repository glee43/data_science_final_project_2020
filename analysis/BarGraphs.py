import os

import numpy as np
import csv
import matplotlib.pyplot as plt
from matplotlib import cm
from sklearn.cluster import KMeans
import argparse
import json
import random
import pandas as pd
from scipy import stats
import math

from mpl_toolkits.mplot3d import Axes3D

cmap = cm.get_cmap('tab10', 10)


def read_data(data, feature_columns):
    """
    Reads the data at the provided files path. 
    :param path: path to dataset
    :return: raw data
    """
    # Load the data set into a 2D numpy array
    largest = data.nlargest(5, feature_columns[0])
    smallest = data.nsmallest(5, feature_columns[0])
    return pd.concat([largest, smallest])


def plt_top_5_and_bottom_5(data, feature_columns=["", "", ""]):
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

    x = np.arange(10)
    y = data[feature_columns[1]].values.tolist()

    x_label = []

    for row in data.iterrows():
        row_data = row[1]
        display_str = row_data['City'] + ", " + \
            row_data['State'] + "\n" + feature_columns[0] + \
            ":\n" + str(round(row_data[feature_columns[0]], 2))

        x_label.append(display_str)
    # print(data)
    # print(y)

    # create a new figure

    plt.figure(figsize=(20, 5))
    print(y)
    bargraph = plt.bar(x, y, align='center', alpha=0.5)

    for i in range(5, 10, 1):
        bargraph[i].set_color('r')

    plt.xticks(x, x_label)
    plt.ylabel(feature_columns[1])
    plt.grid(True)

    plot_name = "/Top_5_and_Bottom_5_BarGraph" + "_" + feature_columns[0] + "_" + feature_columns[1]

    # add title

    plt.title("Top 5 and Bottom 5 " + feature_columns[0] + " vs " + feature_columns[1])

    plt.savefig("output/BarGraph" + plot_name + ".png")
    plt.show()


if __name__ == '__main__':
    data_path = "../data/joined_agg.csv"

    with open(data_path) as data_file:
        raw_data = pd.read_csv(data_file)

    # 5 states with the highest rates of gun violence
    # raw_data = raw_data.loc[(raw_data['State'] == 'la') | (raw_data['State'] == 'al') | (raw_data['State'] == 'mo') | (raw_data['State'] == 'ms') | (raw_data['State'] == 'ok')]
    # 5 states with the lowest rates of gun violence
    # raw_data = raw_data.loc[(raw_data['State'] == 'ma') | (raw_data['State'] == 'ri') |(raw_data['State'] == 'ny') | (raw_data['State'] == 'nj') | (raw_data['State'] == 'ct')]

    # only get data where the population is greater than 10,000
    # raw_data = raw_data.loc[raw_data['Population'] > 100]
    raw_data = raw_data.loc[raw_data['NumIncidents'] > 10]

    # add extra fields
    raw_data['GVRate'] = raw_data['NumIncidents'] / raw_data['Population'] / 4.25
    raw_data['HousingPrice over PopulationDensity'] = raw_data['HousingPrice'] / raw_data['PopDensity']
    raw_data['WaterPercent'] = raw_data['TotalArea'] - raw_data['LandArea'] / raw_data['TotalArea']

    feature_columns = ['NumIncidents', "HousingPrice"]
    data = read_data(raw_data, feature_columns)
    plt_top_5_and_bottom_5(data, feature_columns=feature_columns)
