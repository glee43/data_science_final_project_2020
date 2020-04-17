import json
import math
import os

import numpy as np
import pandas as pd
import scipy.stats as stats

if __name__ == '__main__':
    # 1. Load data for which each row is a city
    datapath = '../data/joined_agg.csv'
    with open(datapath) as f:
        raw_data = pd.read_csv(datapath)

    # 2. Preprocess
    raw_data['GVRate'] = raw_data['NumIncidents'] / raw_data['Population']

    # 3. Partition into two categories: HousingPrice, with a separator at price of $300k
    housing_300k_under = raw_data[raw_data['HousingPrice'] <= 300_000].dropna()['GVRate']
    housing_300k_over = raw_data[raw_data['HousingPrice'] > 300_000].dropna()['GVRate']

    # 4. Z-Test
    # TODO

    def calc_degrees_of_freedom(a, b):
        s_1 = np.var(a)
        s_2 = np.var(b)
        n_1 = np.shape(a)[0]
        n_2 = np.shape(b)[0]

        nr = ((s_1/n_1) + (s_2/n_2))**2
        dr = (((s_1/n_1)**2)/(n_1 - 1)) + (((s_2/n_2)**2)/(n_2 - 1))
        return nr / dr

    def reject_or_not(test_statistic, lower_crit_val, upper_crit_val):
        print(
            f"test_statistic={test_statistic:.5f}, lower_critical_value={lower_crit_val:.5f}, upper_critical_value={upper_crit_val:.5f}")
        if lower_crit_val <= test_statistic <= upper_crit_val:
            print("We therefore fail to reject the null hypothesis and cannot accept the alternate hypothesis.")
        else:
            print("We therefore reject the null hypothesis and accept the alternate hypothesis.")

    degrees_of_freedom = calc_degrees_of_freedom(a=housing_300k_under, b=housing_300k_over)

    test_statistic, p_value = stats.ttest_ind(
        a=housing_300k_under, b=housing_300k_over, equal_var=False)
    print({'test_statistic': test_statistic, 'p_value': p_value})

    lower_crit_val, upper_crit_val = stats.t.ppf(
        0.025, degrees_of_freedom), stats.t.ppf(0.975, degrees_of_freedom)

    reject_or_not(test_statistic, lower_crit_val, upper_crit_val)
