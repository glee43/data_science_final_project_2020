import pandas as pd
from sklearn.cluster import KMeans


feature_columns = ["Population", "NumIncidents", "HousingPrice", "speechiness", "liveness"]

def read_data(path):
    """
    Reads the data at the provided files path. Performs some pre-processing
    - removes outliers (data points that are more than 3 stdev away along any
      feature column
    - removes duplicates

    :param path: path to dataset
    :return: raw data, raw music data (only numeric columns)
    """
    # Load the data set into a 2D numpy array
    with open(path) as data_file:
        data = pd.read_csv(data_file)[feature_columns].to_numpy()

    
    return data


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
    kmeans()