import json
import math
import os

import pandas as pd

from stats


if __name__ == '__main__':
    # 1. Load data for which each row is a city
    datapath = '../data/joined_agg.csv'
    with open(datapath) as f:
        raw_data = pd.read_csv(datapath)

    # 2. Preprocess
    raw_data['GVRate'] = raw_data['NumIncidents'] / raw_data['Population']

    # 3. Partition into two categories: HousingPrice, with a separator at price of $300k
    housing_300k_under = raw_data[raw_data['HousingPrice'] <= 300_000]['GVRate']
    housing_300k_over = raw_data[raw_data['HousingPrice'] > 300_000]['GVRate']

    # 4. Z-Test
