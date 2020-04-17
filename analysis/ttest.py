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

    # 3. Partition into two categories:
    # (a) HousingPrice, separated on a price of $300k
    housing_300k_under = raw_data[raw_data['HousingPrice'] <= 300_000].dropna()['GVRate']
    housing_300k_over = raw_data[raw_data['HousingPrice'] > 300_000].dropna()['GVRate']

    # (b) PopDensity, separated on 3,000 people per sq mile
    pop_density_3k_under = raw_data[raw_data['PopDensity'] <= 3_000].dropna()['GVRate']
    pop_density_3k_over = raw_data[raw_data['PopDensity'] > 3_000].dropna()['GVRate']

    # 4. Z-Test
    # TODO
    print('Housing Price (over $300k v.s. under $300k):')
    perform_t_test(a=housing_300k_under, b=housing_300k_over, significance_level=0.05)

    print()
    print('Population Density (over 3k people/sq mi vs under 3k people/sq mi):')
    perform_t_test(a=pop_density_3k_under, b=pop_density_3k_over, significance_level=0.05)
