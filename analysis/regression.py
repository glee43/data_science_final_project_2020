'''
Performs polymonial regression on gunviolence data
and selects the best fit based on validation data
performance
'''

import numpy as np
import csv
import pandas as pd
import os
import matplotlib.pyplot as plt
import statsmodels.api as sm
from mpl_toolkits.mplot3d import Axes3D
from scipy import stats


def load_data(path, X_cols, y_col="GVRate", min_pop=10000, min_gvi=2):
    '''
    Loads in the cleaned gunviolence data and selects the 
    specified fields. Returns a set of independent variables
    and one specified dependent variable.
    Parameters:
    X_cols  - the columns of the dataset that are being used as
              independent variables
    y_col   - the column of the dataset being used as a dependent
              variable
    min_pop - the minimum population needed for a town to be 
              included in the output
    min_gvi - the minimum number of gun violence incidents needed
              for a town to be included in the output
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
    df["LogPop"] = np.log10(df["Population"])
    df["LogHousingPrice"] = np.log10(df["HousingPrice"])
    df["LogPopDensity"] = np.log10(df["PopDensity"])
    # enforce minimum values
    df = df.loc[df["Population"] >= min_pop,:]
    df = df.loc[df["NumIncidents"] >= min_gvi,:]
    # drop nans from results
    df = df.dropna(axis=0)
    all_cols = X_cols + [y_col]
    df = df[all_cols]
    # Calculate z-score for all data points (how many standard deviations away from mean) for each column
    z = np.abs(stats.zscore(df))
    # Find all the rows where all values in each row have a z-score less than 3
    ind = np.all((z < 3), axis=1)
    df = df[ind]
    X, y = df[X_cols].values, df[y_col].values
    return X, y

def regression(X, y, normalize=False):
    '''
    Performs ordinary least squares regression and 
    returns the rsquared value and coefficients.
    Parameters:
    X           - feature values for each point
    y           - Depedent field values for each point
    Results:
    rsquared    - the rsquared value for the fitted line
    intercept   - the constant coefficient
    coefficients- the coefficients for each feature in the 
                  fitted line
    results     - the results of the ols fitting
    norm_elts   - numbers needed for denormalization
    '''
    norm_elts = ()
    if normalize:
        y_min = np.min(y)
        y_denom = np.max(y)-y_min
        y = (y-y_min)/y_denom
        X_min = np.min(X, axis=0)
        X_denom = np.max(X, axis=0)-X_min
        norm_elts = (y_min, y_denom, X_min, X_denom)
    X = sm.add_constant(X)
    model = sm.OLS(y, X)
    results = model.fit()
    rsquared = results.rsquared
    coefficients = results.params
    intercept = coefficients[0]
    coefficients = coefficients[1:]
    return (rsquared, intercept, coefficients, results, norm_elts)





def viz_regression_3d(X_labels, y_label, X, y, model, res=20, norm_elts=(), denormalize=False):
    '''
    Allows for the visualization of 3d regression
    '''
    zs = y
    xs,ys = np.hsplit(X, 2)

    # create points for surface drawing
    surf_x = np.linspace(np.min(xs), np.max(xs), res)
    surf_y = np.linspace(np.min(ys), np.max(ys), res)
    surf_x, surf_y = np.meshgrid(surf_x, surf_y)
    flat_x = surf_x.flatten()
    flat_x = surf_y.flatten()
    # print(np.column_stack(surf_x,surf_y))
    surf_z = model.predict(np.column_stack((np.ones(res**2),flat_x, flat_x)))
    surf_z = surf_z.reshape(surf_x.shape)

    if denormalize:
        y_min, y_denom, X_min, X_denom = norm_elts
        norm_x = np.linspace(0,1,res)
        norm_y = np.linspace(0,1,res)
        norm_x, norm_y = np.meshgrid(norm_x, norm_y)
        flat_norm_x = norm_x.flatten()
        flat_norm_y = norm_y.flatten()
        surf_z = model.predict(np.column_stack((np.ones(res**2),flat_norm_x, flat_norm_x)))
        surf_z = (surf_z*y_denom) + y_min
        surf_z = surf_z.reshape(surf_x.shape)
        
    fig = plt.figure()
    ax = fig.add_subplot(111, projection='3d')
    
    ax.scatter(xs,ys,zs, c="#00cc00")
    # set axis labels
    ax.set_xlabel(X_labels[0])
    ax.set_ylabel(X_labels[1])
    ax.set_zlabel(y_label)

    ax.plot_surface(surf_x, surf_y, surf_z)

    title = f'Linear Regression of {y_label} on {X_labels[0]} and {X_labels[1]}'

    plt.title(title)
    plt.show()

def viz_regression_2d(X_labels, y_label, X, y, model, res=20, norm_elts=(), denormalize=False):
    '''
    Allows for the visualization of 2d regression
    '''
    ys = y
    xs = X

    # create points for linear trend drawing
    lin_x = np.linspace(np.min(xs), np.max(xs), res)
    lin_y = model.predict(np.column_stack((np.ones(res),lin_x)))
    lin_y = lin_y.reshape(lin_x.shape)

    if denormalize:
        y_min, y_denom, X_min, X_denom = norm_elts
        norm_x = np.linspace(0,1,res)
        lin_y = model.predict(np.column_stack((np.ones(res),lin_x)))
        lin_y = (lin_y*y_denom) + y_min
        lin_y = lin_y.reshape(lin_x.shape)
        
    fig = plt.figure()
    ax = fig.add_subplot(111)
    
    ax.scatter(xs,ys, c="#00cc00")
    # set axis labels
    ax.set_xlabel(X_labels[0])
    ax.set_ylabel(y_label)

    ax.plot(lin_x, lin_y)

    title = f'Linear Regression of {y_label} on {X_labels[0]}'

    plt.title(title)
    plt.show()

    

if __name__ == "__main__":
    # Columns Available
    # ['State', 'City', 'Killed', 'Injured', 'AvgKilled',
    #    'AvgInjured', 'Population', 'Houses', 'TotalArea', 'LandArea',
    #    'PopDensity', 'HouseDensity', 'HousingPrice', 'NumIncidents']
    path = "../data/joined_agg.csv"
    # use_vars = ["LandArea"]
    # use_vars = ['Killed', 'Injured', 'AvgKilled','AvgInjured', 'Population', 'Houses', 'TotalArea', 'LandArea','PopDensity', 'HouseDensity', 'HousingPrice', 'NumIncidents']
    # use_vars = ['AvgKilled','AvgInjured', 'Population', 'TotalArea', 'LandArea','PopDensity', 'HouseDensity', 'HousingPrice']
    # use_vars = ['Population', 'TotalArea', 'LandArea','PopDensity', 'HouseDensity', 'HousingPrice']
    use_vars = ['LogHousingPrice']
    pred_var = "GVRate"
    X,y = load_data(path, use_vars, y_col=pred_var, min_pop=100000,min_gvi=0)
    rsquared, intercept, coefficients, results, norm_elts = regression(X,y, normalize=True)
    print("=============Results==============")
    print(f'R-Squared: {rsquared}')
    var_cos = list(zip(use_vars, coefficients))
    print("Coefficients")
    for pair in var_cos:
        print(f'\t{pair[0]} : {pair[1]}')
    viz_regression_2d(use_vars, pred_var, X,y,results, norm_elts=norm_elts, denormalize=True)



