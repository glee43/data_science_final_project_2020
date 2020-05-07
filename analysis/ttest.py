import json
import math
import os

import numpy as np
import pandas as pd
import scipy.stats as stats


def perform_t_test(a: pd.Series, b: pd.Series, significance_level: float = 0.05) -> None:
    '''
    Performs a one-tailed two-sample T-test.
    :param a: The first sample.
    :param b: The second sample.
    :param significance_level: The threshold for the p-value at which we reject the null hypothesis
    :prints: Whether or not the null hypothesis (there is no statistical difference in the values
    between the two samples) can be rejected for the alternate hypothesis (there is a statistical
    difference in the values between the two samples.)
    '''

    def calc_degrees_of_freedom(a, b):
        s_1 = np.var(a)
        s_2 = np.var(b)
        n_1 = np.shape(a)[0]
        n_2 = np.shape(b)[0]

        nr = ((s_1/n_1) + (s_2/n_2))**2
        dr = (((s_1/n_1)**2)/(n_1 - 1)) + (((s_2/n_2)**2)/(n_2 - 1))
        return nr / dr

    test_statistic, p_value = stats.ttest_ind(a=a, b=b, equal_var=False)
    degrees_of_freedom = calc_degrees_of_freedom(a=a, b=b)
    lower_crit_val = stats.t.ppf(significance_level / 2, degrees_of_freedom)
    upper_crit_val = stats.t.ppf(1 - significance_level / 2, degrees_of_freedom)

    print(
        f"test_statistic={test_statistic:.5f}. critical values: {lower_crit_val:.5f} and {upper_crit_val:.5f}")
    if lower_crit_val <= test_statistic <= upper_crit_val:
        print("We therefore fail to reject the null hypothesis and cannot accept the alternate hypothesis.")
    else:
        print("We therefore reject the null hypothesis and accept the alternate hypothesis.")

    return None


if __name__ == '__main__':
    # 1. Load data for which each row is a city
    datapath = '../data/joined_agg.csv'
    with open(datapath) as f:
        raw_data = pd.read_csv(datapath)

    # 2. Preprocess
    raw_data['GVRate'] = raw_data['NumIncidents'] / raw_data['Population']
    mean_h = int(raw_data.dropna()['HousingPrice'].mean())
    mean_d = int(raw_data.dropna()['PopDensity'].mean())
    print(f'Mean Housing Price: ${mean_h}')
    print(f'Mean Pop Density: {mean_d} people / sq mi\n\n')

    cutoff_h = mean_h
    cutoff_d = mean_d
    # cutoff_h = 300_000
    # cutoff_d = 3_000

    # 3. Partition into two categories:
    # (a) HousingPrice, below/above cutoff_h
    h_under_mean: pd.Series = raw_data[raw_data['HousingPrice'] <= cutoff_h].dropna()['GVRate']
    h_over_mean: pd.Series = raw_data[raw_data['HousingPrice'] > cutoff_h].dropna()['GVRate']

    # (b) PopDensity, below_above cutoff_d
    d_under_mean: pd.Series = raw_data[raw_data['PopDensity'] <= cutoff_d].dropna()['GVRate']
    d_over_mean: pd.Series = raw_data[raw_data['PopDensity'] > cutoff_d].dropna()['GVRate']

    # 4. Z-Test
    # TODO
    print(f'Housing Price (over ${cutoff_h // 1000}k v.s. under ${cutoff_h // 1000}k):')
    perform_t_test(a=h_under_mean, b=h_over_mean, significance_level=0.05)
    print()

    mean_gvrate_under_h_mean = h_under_mean.mean()
    mean_gvrate_over_h_mean = h_over_mean.mean()
    print(
        f'Housing price under ${cutoff_h // 1000}k, GV incidents per 1,000 ppl per year: {mean_gvrate_under_h_mean * 1_000:6.5f}  ({h_under_mean.count()} cities)')
    print(
        f'Housing price over ${cutoff_h // 1000}k, GV incidents per 1,000 ppl per year:  {mean_gvrate_over_h_mean * 1_000:6.5f}  ({h_over_mean.count()} cities)')
    print('\n')

    print(f'Population Density (over {cutoff_d} people/sq mi vs under {cutoff_d} people/sq mi):')
    perform_t_test(a=d_under_mean, b=d_over_mean, significance_level=0.05)
    print()

    mean_gvrate_under_d_mean = d_under_mean.mean()
    mean_gvrate_over_d_mean = d_over_mean.mean()
    print(
        f'Population density under {cutoff_d}, GV incidents per 1,000 ppl per year: {mean_gvrate_under_d_mean * 1_000:6.5f}  ({d_under_mean.count()} cities)')
    print(
        f'Population density over {cutoff_d}, GV incidents per 1,000 ppl per year:  {mean_gvrate_over_d_mean * 1_000:6.5f}  ({d_over_mean.count()} cities)')
