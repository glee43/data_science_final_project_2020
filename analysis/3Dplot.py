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

MAX_VAL = 10
cmap = cm.get_cmap('tab10', MAX_VAL)


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


def visualize_pts(data, feature_columns=["","",""], additional_data=None):
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
    
    x, y, z = np.hsplit(data, 3)
    

    # create a new figure
    ax = plt.figure().add_subplot(111, projection='3d')
    
    # color the points based on the first feature
    colors_s = None

    # color the points based on population
    if(additional_data is not None):
        colors_s = []
        for d in additional_data:
            if d < 10000:
                #print("red")
                colors_s.append(cmap(0/MAX_VAL))
            elif d > 10000 and d < 100000:
                colors_s.append(cmap(2/MAX_VAL))
            else:
                colors_s.append(cmap(3/MAX_VAL))

    
    ax.scatter(x, y, z, c=colors_s)
    
    ax.set_xlabel(feature_columns[0])
    ax.set_ylabel(feature_columns[1])
    ax.set_zlabel(feature_columns[2])

    plot_name = "/3DScatter" + "_" + feature_columns[0] + "_" + feature_columns[1] + "_" + feature_columns[2]

    # Helps visualize clusters
    plt.gca().invert_xaxis()

    # add title
    plt.title(feature_columns[0] + " vs " + feature_columns[1] + " vs " + feature_columns[2])
    
    plt.savefig("output/3DScatter" + plot_name + ".png")
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
    

    feature_columns = ['HousingPrice', "PopDensity", "GVRate", 'Population']
    
    data = read_data(raw_data, feature_columns)

    x, y, z, a = np.hsplit(data, 4)
    data = np.column_stack((np.column_stack((x,y)),z))
    additional_data = np.ndarray.flatten(a)
    print({ 'additional data shape': additional_data.shape })

    visualize_pts(data, feature_columns=feature_columns, additional_data=additional_data)
