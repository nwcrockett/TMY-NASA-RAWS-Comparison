"""
remove shemya island from difference_data_alaska.csv

"""
import cartopy.feature as cfeature
import cartopy.crs as ccrs
import matplotlib.pyplot as plt
from pandas import read_csv
import pandas as pd
import numpy as np


df = read_csv("/home/nelson/PycharmProjects/TMY_NASA_RAWS Comparison/difference_data_alaska.csv", header=1)

lat = np.array(df["meso_lat"])
long = np.array(df["meso_long"])

fig = plt.figure()
ax = fig.add_subplot(1, 1, 1, projection=ccrs.PlateCarree())

alaska_west = -180
alaska_east = -130
alaska_south = 45
alaska_north = 75

ax.set_extent([alaska_west, alaska_east, alaska_south, alaska_north])

ax.stock_img()
ax.coastlines()
ax.scatter(long, lat)
plt.show()



