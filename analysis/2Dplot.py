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
    grabbed_data = data[feature_columns]
    # drop values with nan
    grabbed_data = grabbed_data.dropna(axis=0)

    # Calculate z-score for all data points (how many standard deviations away from mean) for each column
    z = np.abs(stats.zscore(grabbed_data))
    
    # Find all the rows where all values in each row have a z-score less than 3
    ind = np.all((z < 3), axis=1)

    # only get data within 3 std
    data_subset = grabbed_data[ind].to_numpy()
    
    return data_subset


def visualize_pts(data, feature_columns=["","",""]):
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
    
    x, y = np.hsplit(data, 2)
    

    # create a new figure
    fig, ax = plt.subplots()
    
    # color the points based on the first feature
    colors_s = None

    #colors_s = [cmap(l / MAX_CLUSTERS) for i in x ]

    ax.scatter(x, y, c=colors_s)
    
    ax.set_xlabel(feature_columns[0])
    ax.set_ylabel(feature_columns[1])
    ax.grid(True)

    plot_name = "/2DScatter" + "_" + feature_columns[0] + "_" + feature_columns[1] 

    # add title
    plt.title(feature_columns[0] + " vs " + feature_columns[1] )
    plt.ylim(bottom=0, top=0.0125)
    plt.savefig("output/2DScatter" + plot_name + ".png")
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
    # raw_data = raw_data.loc[raw_data['Population']> 10000]
    # raw_data = raw_data.loc[raw_data['NumIncidents']>10]

    # add extra fields 
    raw_data['GVRate'] = raw_data['NumIncidents'] / raw_data['Population']
    raw_data['HousingPrice over PopulationDensity'] = raw_data['HousingPrice'] / raw_data['PopDensity']
    raw_data['WaterPercent'] = raw_data['TotalArea'] - raw_data['LandArea'] / raw_data['TotalArea']
    

    feature_columns = ['PopDensity', "GVRate"]
    data = read_data(raw_data, feature_columns)
    visualize_pts(data, feature_columns=feature_columns)