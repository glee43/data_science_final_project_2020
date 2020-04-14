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

MAX_CLUSTERS = 10
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

    # min max scaling
    x_min = np.min(data_subset, axis=0) #amin vs amax
    x_max = np.max(data_subset, axis=0)
    denom = (x_max - x_min)
    
    return (data_subset - x_min) / (denom), x_min, denom


def visualize_clusters(data, centroids=None, centroid_indices=None, feature_columns=["","",""]):
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
    def plot_pts(fig, color_map=None):
        x, y, z = np.hsplit(data, 3)
        fig.scatter(x, y, z, c=color_map)

    def plot_clusters(fig):
        x, y, z = np.hsplit(centroids, 3)
        fig.scatter(x, y, z, c="black", marker="x", alpha=1, s=200)

    # check if we are plotting centroids
    cluster_plot = centroids is not None and centroid_indices is not None

    # add centroids sub plot 
    ax = plt.figure().add_subplot(111, projection='3d')
    colors_s = None

    if cluster_plot:
        if max(centroid_indices) + 1 > MAX_CLUSTERS:
            print(f"Error: Too many clusters. Please limit to fewer than {MAX_CLUSTERS}.")
            exit(1)
        colors_s = [cmap(l / MAX_CLUSTERS) for l in centroid_indices]
        plot_clusters(ax)

    plot_pts(ax, colors_s)
    
    ax.set_xlabel(feature_columns[0])
    ax.set_ylabel(feature_columns[1])
    ax.set_zlabel(feature_columns[2])

    plot_name = "/Kmeans" + "_" + feature_columns[0] + "_" + feature_columns[1] + "_" + feature_columns[2]

    # Helps visualize clusters
    plt.gca().invert_xaxis()

    # add title
    if cluster_plot:
        plt.title(feature_columns[0] + " vs " + feature_columns[1] + " vs " + feature_columns[2] + " with K=" + str(len(centroids)))
    else:
        plt.title(feature_columns[0] + " vs " + feature_columns[1] + " vs " + feature_columns[2])
    
    plt.savefig("output/kmeans" + plot_name + ".png")
    plt.show()

def sk_learn_cluster(X, K):
    """
    Performs k-means clustering using library functions (scikit-learn). You can
    experiment with different initialization settings, but please initialize
    without any optional arguments (other than n_clusters) before submitting.

    :param X: 2D np array containing features of the songs
    :param K: number of clusters
    :return: a tuple of (cluster centroids, indices for each data point)
    """
    # TODO:
    kmeans = KMeans(n_clusters=K).fit(X)
    labels = kmeans.predict(X)
    
    return kmeans.cluster_centers_ , labels

if __name__ == '__main__':
    data_path = "../data/joined_agg.csv" 
    
    with open(data_path) as data_file:
        raw_data = pd.read_csv(data_file)
    
    # 5 states with the highest rates of gun violence
    raw_data = raw_data.loc[(raw_data['State'] == 'la') | (raw_data['State'] == 'al') | (raw_data['State'] == 'mo') | (raw_data['State'] == 'ms') | (raw_data['State'] == 'ok')]
    # 5 states with the lowest rates of gun violence
    # raw_data = raw_data.loc[(raw_data['State'] == 'ma') | (raw_data['State'] == 'ri') |(raw_data['State'] == 'ny') | (raw_data['State'] == 'nj') | (raw_data['State'] == 'ct')]

    # only get data where the population is greater than 10,000
    # raw_data = raw_data.loc[raw_data['Population']> 10000]
    raw_data = raw_data.loc[raw_data['NumIncidents']>10]

    # add extra fields 
    raw_data['GVRate'] = raw_data['NumIncidents'] / raw_data['Population']
    raw_data['HousingPrice over PopulationDensity'] = raw_data['HousingPrice'] / raw_data['PopDensity']
    raw_data['WaterPercent'] = raw_data['TotalArea'] - raw_data['LandArea'] / raw_data['TotalArea']
    

    # # options State, City, Killed, Injured, AvgKilled, AvgInjured, Population, Houses,TotalArea,LandArea,PopDensity,HouseDensity,HousingPrice,NumIncidents
    # feature_columns = ["Population", "HousingPrice", "NumIncidents"]
    # data, x_min, denom = read_data(raw_data, feature_columns)
    # centroids_sklearn, idx_sklearn = sk_learn_cluster(data, 5)
    # # un min max
    # centroids_sklearn = (centroids_sklearn * denom) + x_min
    # data = (data * denom) + x_min
    # visualize_clusters(data, centroids=centroids_sklearn, centroid_indices=idx_sklearn, feature_columns=feature_columns)

    # feature_columns = ["GVRate", "HousingPrice", "AvgKilled"]
    # data, x_min, denom = read_data(raw_data, feature_columns)
    # centroids_sklearn, idx_sklearn = sk_learn_cluster(data, 5)
    # # un min max
    # centroids_sklearn = (centroids_sklearn * denom) + x_min
    # data = (data * denom) + x_min
    # visualize_clusters(data, centroids=centroids_sklearn, centroid_indices=idx_sklearn, feature_columns=feature_columns)
   
    feature_columns = ['HousingPrice over PopulationDensity', "GVRate", "WaterPercent"]
    data, x_min, denom = read_data(raw_data, feature_columns)
    centroids_sklearn, idx_sklearn = sk_learn_cluster(data, 5)
    # un min max
    centroids_sklearn = (centroids_sklearn * denom) + x_min
    data = (data * denom) + x_min
    visualize_clusters(data, centroids=centroids_sklearn, centroid_indices=idx_sklearn, feature_columns=feature_columns)