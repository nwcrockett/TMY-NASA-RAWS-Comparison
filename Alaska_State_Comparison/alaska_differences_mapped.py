from mpl_toolkits.basemap import Basemap
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np


def pull_month_data_from_my_current_mess(df):
    Jan = []
    Feb = []
    Mar = []
    Apr = []
    May = []
    Jun = []
    Jul = []
    Aug = []
    Sep = []
    Oct = []
    Nov = []
    Dec = []
    for index, rows in df.iterrows():
        temp = rows['month_differences'].split(" ")
        Jan.append(float(temp[2].strip("],")))
        Feb.append(float(temp[5].strip("],")))
        Mar.append(float(temp[8].strip("],")))
        Apr.append(float(temp[11].strip("],")))
        May.append(float(temp[14].strip("],")))
        Jun.append(float(temp[17].strip("],")))
        Jul.append(float(temp[20].strip("],")))
        Aug.append(float(temp[23].strip("],")))
        Sep.append(float(temp[26].strip("],")))
        Oct.append(float(temp[29].strip("],")))
        Nov.append(float(temp[32].strip("],")))
        Dec.append(float(temp[35].strip("],")))

    return [Jan, Feb, Mar, Apr, May, Jun, Jul, Aug, Sep, Oct, Nov, Dec]


def graph_all_the_months(months, x, y):
    month_dict = ['January', 'February', 'March',
                  'April', 'May', 'June',
                  'July', 'August', 'September',
                  'October', 'November', 'December']

    month_index = 0
    for mn in month_dict:
        values = months[month_index]

        plt.figure(figsize=(10, 10))
        m = Basemap(projection='cyl', llcrnrlat=50, urcrnrlat=75,
                    llcrnrlon=-180, urcrnrlon=-130, resolution='c')

        m.etopo()

        m.scatter(x, y, c=values, cmap=plt.get_cmap("gist_ncar"))
        plt.colorbar()
        plt.title(mn)
        plt.savefig("/home/nelson/PycharmProjects/TMY_NASA_RAWS Comparison/"
                    "Alaska_State_Comparison/state maps/Meso maps/" + mn + ".png")
        plt.show()
        month_index += 1


if __name__ == "__main__":
    df = pd.read_csv("/home/nelson/PycharmProjects/TMY_NASA_RAWS Comparison/difference_data_alaska.csv", header=1)

    plt.figure(figsize=(10,10))
    m = Basemap(projection='cyl',llcrnrlat=50,urcrnrlat=75,
                llcrnrlon=-180,urcrnrlon=-130,resolution='c')

    m.etopo()
    lat = np.array(df["meso_lat"])
    long = np.array(df["meso_long"])
    vals = np.array(df["year_difference"])
    x, y = m(long, lat)

    m.scatter(x, y, c=vals, cmap=plt.get_cmap("gist_ncar"))
    plt.colorbar()
    plt.savefig("/home/nelson/PycharmProjects/TMY_NASA_RAWS Comparison/"
                "Alaska_State_Comparison/state maps/Meso maps/year difference.png")
    plt.show()

    months = pull_month_data_from_my_current_mess(df)
    graph_all_the_months(months, x, y)





