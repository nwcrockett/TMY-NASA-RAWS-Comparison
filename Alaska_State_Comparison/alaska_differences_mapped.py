"""
for some crazy reason Basemap works at least only in the console when
import pandas as pd
import geopandas
from shapely.geometry import Point
import matplotlib.pyplot as plt

has all been imported
Doesn't make any sense but I'm not going to bother looking into further at this time

"""
import pandas as pd
import geopandas
from shapely.geometry import Point
import matplotlib.pyplot as plt
from mpl_toolkits.basemap import Basemap
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np


raw_tmy = ["January_raws_tmy", "February_raws_tmy",
           "March_raws_tmy", "April_raws_tmy",
           "May_raws_tmy", "June_raws_tmy",
           "July_raws_tmy", "August_raws_tmy",
           "September_raws_tmy", "October_raws_tmy",
           "November_raws_tmy", "December_raws_tmy"]

nasa_tmy = ["January_nasa_tmy", "February_nasa_tmy",
            "March_nasa_tmy", "April_nasa_tmy",
            "May_nasa_tmy", "June_nasa_tmy",
            "July_nasa_tmy", "August_nasa_tmy",
            "September_nasa_tmy", "October_nasa_tmy",
            "November_nasa_tmy", "December_nasa_tmy"]

raw_nasa = ["January_raws_nasa", "February_raws_nasa",
            "March_raws_nasa", "April_raws_nasa",
            "May_raws_nasa", "June_raws_nasa",
            "July_raws_nasa", "August_raws_nasa",
            "September_raws_nasa", "October_raws_nasa",
            "November_raws_nasa", "December_raws_nasa"]

raw_tmy_path = "/home/nelson/PycharmProjects/TMY_NASA_RAWS Comparison/" \
                   "Alaska_State_Comparison/state maps/Raws - tmy maps"
nasa_tmy_path = "/home/nelson/PycharmProjects/TMY_NASA_RAWS Comparison/" \
                "Alaska_State_Comparison/state maps/Nasa - tmy maps"
raw_nasa_path = "/home/nelson/PycharmProjects/TMY_NASA_RAWS Comparison/" \
                    "Alaska_State_Comparison/state maps/Raws - Nasa maps"


def graph_alaska(x, y, values, name, mini, path, show=False):
    plt.figure(figsize=(10, 10))
    m = Basemap(projection='merc', llcrnrlat=50, urcrnrlat=75,
                llcrnrlon=-180, urcrnrlon=-130, resolution='c')

    m.etopo()

    m.scatter(x, y, c=values, cmap=plt.get_cmap("RdBu"), vmin=mini, vmax=np.abs(mini))
    cbar = plt.colorbar()
    cbar.set_label("kWH/m2/month")
    plt.title(name)
    plt.savefig(path + "/" + name + ".png")
    if show:
        plt.show()


def graph_months_cleaned_dataframe(df, x, y, show=False):
    month_dict = ['January', 'February', 'March',
                  'April', 'May', 'June',
                  'July', 'August', 'September',
                  'October', 'November', 'December']

    for mn, r_t, n_t, r_n in zip(month_dict, raw_tmy, nasa_tmy, raw_nasa):
        value = np.array(df[r_t])
        value[np.isnan(value)] = 0
        min = np.min(value)
        graph_alaska(x, y, value, mn, min, raw_tmy_path, show=show)

        value = np.array(df[n_t])
        value[np.isnan(value)] = 0
        min = np.min(value)
        graph_alaska(x, y, value, mn, min, nasa_tmy_path, show=show)

        value = np.array(df[r_n])
        value[np.isnan(value)] = 0
        min = np.min(value)
        graph_alaska(x, y, value, mn, min, raw_nasa_path, show=show)


def graph_year(x, y, values, path, show=False):
    plt.figure(figsize=(10, 10))
    m = Basemap(projection='merc', llcrnrlat=50, urcrnrlat=75,
                llcrnrlon=-180, urcrnrlon=-130, resolution='c')

    m.etopo()

    m.scatter(x, y, c=values, cmap=plt.get_cmap("gist_ncar"))
    cbar = plt.colorbar()
    cbar.set_label("kWH/m2/year")
    plt.title("Year Differences")
    plt.savefig(path + "/" + "year difference.png")
    if show:
        plt.show()


def plot_year_differences(df, x, y, show=False):
    years = ['year_difference_raws_tmy', 'year_difference_nasa_tmy',
             'year_difference_raws_nasa']

    vals = np.array(df[years[0]])
    graph_year(x, y, vals, raw_tmy_path, show=show)

    vals = np.array(df[years[1]])
    graph_year(x, y, vals, nasa_tmy_path, show=show)

    vals = np.array(df[years[2]])
    graph_year(x, y, vals, raw_nasa_path, show=show)


if __name__ == "__main__":
    df = pd.read_csv("/home/nelson/PycharmProjects/TMY_NASA_RAWS Comparison/"
                     "Alaska_State_Comparison/difference_data_alaska.csv", header=1)
    m = Basemap(projection='merc', llcrnrlat=50, urcrnrlat=75,
                llcrnrlon=-180, urcrnrlon=-130, resolution='c')

    m.etopo()

    lat = np.array(df["meso_lat"])
    long = np.array(df["meso_long"])
    x, y = m(long, lat)

    plot_year_differences(df, x, y, show=True)

    graph_months_cleaned_dataframe(df, x, y, show=True)





