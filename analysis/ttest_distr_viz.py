import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
import os
from scipy.stats import norm

threshold = 200000
hard_housing = 200000
hard_pop = 1000
hard_thresh = False
drop_percentile = 100
pop = True
use_zeros = True

pop_low = 50000
pop_high = 500000

num_bins = 100


if __name__ == "__main__":
    df = pd.read_csv("./data/joined_agg.csv")
    df= df[["HousingPrice", "NumIncidents", "Population", "PopDensity"]]
    df["GVRate"] = (df["NumIncidents"] * 1000) / (df["Population"]*4.25)
    df = df.dropna(axis=0)

    df = df[df["Population"] > pop_low]
    df = df[df["Population"] < pop_high]

    med_pop = np.median(np.array(df["PopDensity"]))
    med_housing = np.median(np.array(df["HousingPrice"]))
    print(f"Median Housing Price - {med_housing}")
    print(f"Median Population Density - {med_pop}")

    if pop and not hard_thresh:
        threshold = med_pop
    elif not pop and not hard_thresh:
        threshold = med_housing
    elif pop and hard_thresh:
        threshold = hard_pop
    elif not pop and hard_thresh:
        threshold = hard_housing

    field = "PopDensity" if pop else "HousingPrice"


    low = df[df[field] < threshold]
    high = df[df[field] >= threshold]
    low_rates = np.array(low["GVRate"])
    high_rates = np.array(high["GVRate"])

    hist_range = (0, np.percentile(np.hstack((low_rates, high_rates)), drop_percentile))
    # update rates arrays to drop data outside of range
    low = low[low["GVRate"] < hist_range[1]]
    full_low = np.array(low["GVRate"])
    low = low[low["GVRate"] > 0]
    low_rates = np.array(low["GVRate"])
    high = high[high["GVRate"] < hist_range[1]]
    full_high = np.array(high["GVRate"])
    high = high[high["GVRate"] > 0]
    high_rates = np.array(high["GVRate"])
    
    # num_bins = int((low_rates.shape[0] + high_rates.shape[0]) / 200)

    field_title = "Population Density" if pop else "Housing Price"


    fig, ax = plt.subplots(figsize=(10,6))
    plt.xlim(hist_range)
    # ax.set_title(f'Distribution of Gun Violence Rates For Cities with Populations of {"{:,}".format(pop_low)}-{"{:,}".format(pop_high)} \n By High and Low {field_title}')
    ax.set_ylabel("Probability Density")
    ax.set_xlabel("Gun Violence Rates (Number of Incidents per 1,000 People per Year)")
    # ax.ylim()
    str_thresh = "{:,}".format(int(threshold))
    if use_zeros:
        to_plot = [(low_rates, "r", f'{field_title} < {str_thresh}', full_low), (high_rates, "b", f'{field_title} > {str_thresh}', full_high)]
    else:
        to_plot = [(low_rates, "r", f'{field_title} < {str_thresh}'), (high_rates, "b", f'{field_title} > {str_thresh}')]
    

    for i, x in enumerate(to_plot):
        rates = x[0]
        c = x[1]
        label = x[2]
        if use_zeros:
            full_rates = x[3]
        hist, bin_edges = np.histogram(rates, bins=num_bins, range=hist_range, density=False)

        if use_zeros:
            hist = hist/(full_rates.shape[0]*(bin_edges[1]-bin_edges[0]))
        else:
            hist = hist/(rates.shape[0]*(bin_edges[1]-bin_edges[0]))

        # gaussian distribution estimate
        norm_x = np.linspace(hist_range[0], hist_range[1], num=1000)
        if use_zeros:
            mu = np.mean(full_rates)
            sigma = np.std(full_rates)
        else:
            mu = np.mean(rates)
            sigma = np.std(rates)
        label += f"\nMean: {round(mu, 4)}\n Standard Deviation: {round(sigma, 4)}" 
        norm_y = norm.pdf(norm_x, mu, sigma)

        bar_width = (hist_range[1]-hist_range[0])/num_bins/2
        ax.bar(bin_edges[:-1]+bar_width*i, hist, color=c, alpha=0.5, width=bar_width)
        ax.plot(norm_x, norm_y, color=c, label=label)
    
    ax.legend()
    
    # plt.show()

    plt.savefig(f'./analysis/output/distribution/distribution_{"popdensity" if pop else "housing"}_{pop_low}_{pop_high}.png')




