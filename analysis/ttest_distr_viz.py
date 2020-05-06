import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
import os
from scipy.stats import norm


if __name__ == "__main__":
    df = pd.read_csv("../data/joined_agg.csv")
    df= df[""]
    df = df.dropna(axis=0)

    df = df.loc[df["DATE"].map(dateInRange)]

    temps = np.array(df["TAVG"])
    # print(temps)

    num_samples = temps.shape[0]
    num_bins = int(np.max(temps) - np.min(temps) + 1)

    hist, bin_edges = np.histogram(temps, bins=num_bins)
    # normalize
    hist = hist/num_samples

    # gaussian distribution estimate
    norm_x = np.linspace(np.min(temps), np.max(temps), num=1000)
    mu = np.mean(temps)
    sigma = np.std(temps)
    norm_y = norm.pdf(norm_x, mu, sigma)

    ax = plt.subplot(111)
    ax.bar(bin_edges[:-1], hist)
    ax.plot(norm_x, norm_y, color="g")
    ax.set_title("Probability Distribution of Average Daily Temperature in Burlington, VT")
    ax.set_ylabel("Probability Density")
    ax.set_xlabel("Temperature (Fahrenheit)")
    plt.savefig("btv_temp_distr.png")


    # create shifted vars
    shift = 10
    s_norm_x = np.linspace(np.min(temps), np.max(temps)+shift, num=1100)
    s_mu = mu + shift
    s_norm_y = norm.pdf(s_norm_x, s_mu, sigma)

    s_bin_edges = bin_edges + shift


    ax.cla()
    ax.bar(s_bin_edges[:-1], hist)
    ax.plot(s_norm_x, s_norm_y, color="g")
    ax.set_title(f"PDF of Average Daily Temperature in Burlington, VT (Shifted {shift} Degrees)")
    ax.set_ylabel("Probability Density")
    ax.set_xlabel("Temperature (Fahrenheit)")
    plt.savefig("btv_temp_distr_shift.png")




