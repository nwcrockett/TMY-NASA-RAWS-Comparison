"""
Nelson Crockett
Setup for using the Meso West weather station data,
NASA POWER satellite data, and the TMY3 Modeled data
To create a data comparison based on total daily sum of
GHI solar energy that hits the earth in the given locations

"""

import pandas as pd
import csv
import os
import geopy.distance
import Meso_station_download as msd
import download_nasa_file as dnf


def rename_all_tmy3_files(tmy3_original_path, tmy3_storage_path, setup_path):
    """

    TMY3 files are originally stored as unique identifying numbers. This is not
    useful when I need to view specific files to check locations. So this function
    renames all of the TMY3 files to the site name that corresponds to the stations
    latitude and longitude.

    This process also creates a DataFrame that is output to a csv which contains
    the site name, latitude and longitude for each station. Which is then used for
    downloading Meso West and NASA POWER data Meso Comp

    :param tmy3_original_path: Path to the original TMY3 files
    :param tmy3_storage_path: Path to the renamed TMY3 files
    :param setup_path: Path the the setup directory
    :return: Nothing. changes the names of all TMY3 file. Creates new Meta data file

    """

    os.chdir(tmy3_original_path)
    directory = os.listdir()

    tmy3_name_lat_long = [["Site_name", "Latitude", "Longitude"]]

    for item in directory:
        with open(item) as f:
            mycsv = csv.reader(f)
            mycsv = list(mycsv)
            name = mycsv[0][1]
            name = name.strip(".")  # another part of the process splits all name on "." to separate out the .csv

            if "/" in name:  # avoid path name mix ups
                temp = name
                temp[temp.index("/")] = "_"
                name = "".join(temp)

            lat = mycsv[0][4]
            long = mycsv[0][5]
        f.close()
        tmy_df = pd.read_csv(item, header=1)
        tmy_df.to_csv(tmy3_storage_path
                      + name + ".csv")
        tmy3_name_lat_long.append([name, lat, long])

    meta_data = pd.DataFrame(tmy3_name_lat_long)
    os.chdir(setup_path)
    meta_data.to_csv("tmy3_name_lat_long.csv")


def find_tmy3_meso_station_matchups(meso_df, tmy3_meta_df, distance=5.0):
    """
    Finds the matchups between a TMY3 site and Meso station.
    Within a given distance in miles and outputs that data as a csv

    :param meso_df: Meso West DataFrame with the solar metadata for the entire state of Alaska
    :param tmy3_meta_df: TMY3 DataFrame with site name Latitude and Longitude
    :param distance: The distance in miles for which stations are selected for a match up (Default: 5 miles)

    :return: returns nothing. Outputs a csv with the match ups between a TMY3 and Meso West weather stations
    """

    tmy3_meso_matchup = [["TMY3_site_name", "Meso_site_name",
                          "tmy_lat", "tmy_long", "meso_lat",
                          "meso_long", "meso_start", "meso_end",
                          "meso_id"]]
    missing_data = [["TMY3_site_name", "tmy_lat", "tmy_long"]]

    for index, row in tmy3_meta_df.iterrows():
        for i, r in meso_df.iterrows():
            if geopy.distance.distance((r["LATITUDE"], r["LONGITUDE"]), (row["Latitude"], row["Longitude"])) < distance:
                time_split = r["solar_radiation"].split(" ")
                if len(time_split) != 8:
                    print(row["Site_name"])
                    print(time_split)
                    print()
                    continue
                start_time = time_split[5]
                start_time = start_time.strip("'',")
                end_time = time_split[7]
                end_time = end_time.strip("''}")
                tmy3_meso_matchup.append([row["Site_name"].strip("."), r["NAME"].strip("."),
                                         row["Latitude"], row["Longitude"],
                                         r["LATITUDE"], r["LONGITUDE"],
                                         start_time, end_time,
                                         r["STID"]])

    tmy_meso_df = pd.DataFrame(tmy3_meso_matchup)
    tmy_meso_df.to_csv("TMY3_Meso_station_matchup.csv")
    missing_data = pd.DataFrame(missing_data)
    missing_data.to_csv("TMY3 with no Meso Stations.csv")  # Ease of use tracker for TMY3 stations with no match ups


def filter_based_on_time_scale(tmy3_meso_df, days):
    """
    Filters the Match up csv/DataFrame with the TMY3 and Meso West station that are in
    a predetermine distance of each other. To select out stations that only have a timescale that
    is equal to or greater that the amount of days in the days parameter.

    :param tmy3_meso_df: csv/DataFrame with TMY3 and Meso West stations within a certain distance
    :param days: time scale wanted in days. Recommended in timescales of at least a month
    :return: Nothing. Outputs a csv file with weather station match ups with timescales greater than or equal to
        days parameter
    """

    tmy3_meso_df = tmy3_meso_df.loc[tmy3_meso_df["meso_start"] != "None"]
    tmy3_meso_df["meso_start"] = pd.to_datetime(tmy3_meso_df["meso_start"], format="%Y-%m-%dT%H:%M:%SZ")
    tmy3_meso_df["meso_end"] = pd.to_datetime(tmy3_meso_df["meso_end"], format="%Y-%m-%dT%H:%M:%SZ")
    time_scale = tmy3_meso_df.loc[
        (tmy3_meso_df["meso_end"] - tmy3_meso_df["meso_start"]).dt.days >= days]
    time_scale = time_scale.reset_index(drop=True)
    time_scale = time_scale.drop(columns=["0"])
    time_scale["meso_end"] = time_scale["meso_end"].dt.strftime("%Y%m%d%H%m")
    time_scale["meso_start"] = time_scale["meso_start"].dt.strftime("%Y%m%d%H%m")
    time_scale.to_csv("tmy3_meso_matchup_with_time_scale_" + str(days) + "_days.csv")


def download_meso_data(station_df, token_for_meso_api):
    """
    Downloads the Meso West station data for all the stations in station_df DataFrame.
    Over the time period in time_scale

    :param station_df: DataFrame with the stations to be downloaded over a timescale
    :param token_for_meso_api: Token that is required for Meso West
    :return: Nothing. Downloads Meso West weather station files.
    """

    count = 0
    for index, rows in station_df.iterrows():
        count += 1
        print(rows["meso_id"])
        print(rows["meso_start"])
        print(rows["meso_end"])
        print(token_for_meso_api)
        print()
        msd.download_new_csv_for_a_station(rows["meso_id"], rows["meso_start"],
                                           rows["meso_end"], token_for_meso_api,
                                           "/home/nelson/PycharmProjects/"
                                           "TMY_NASA_RAWS Comparison/"
                                           "Alaska_State_Comparison/Meso Station Data/" +
                                           rows["TMY3_site_name"] + "$" +
                                           rows["Meso_site_name"] + ".csv")
        print(count)


def download_nasa_data_for_meso_comparison(station_df):
    """
    Downloads the NASA POWER Latitude and Longitude combinations
     data for all the locations in station_df.
    Over the time period in station_df.

    :param station_df: DataFrame with the Latitude and Longitude combinations to be downloaded over a timescale
    :return: Nothing. Downloads NASA POWER GHI solar files.
    """

    count = 0
    for index, rows in station_df.iterrows():
        count += 1
        print(count)
        print(rows["Meso_site_name"])
        print(rows["meso_id"])
        print(str(rows["meso_start"])[0:8])
        print(str(rows["meso_end"])[0:8])
        print()

        csv_url = dnf.get_the_csv_url(str(rows["meso_lat"]),
                                      rows["meso_long"],
                                      str(rows["meso_start"])[0:8],
                                      str(rows["meso_end"])[0:8])
        dnf.output_new_nasa_csv_file("/home/nelson/PycharmProjects/"
                                     "TMY_NASA_RAWS Comparison/"
                                     "Alaska_State_Comparison/NASA POWER data Meso Comp/" +
                                     rows["TMY3_site_name"] + "$" +
                                     rows["Meso_site_name"] + ".csv",
                                     csv_url)


def download_nasa_data_for_tmy3_comparison(station_df, time_start, time_end):
    """
    Outputs are different for both the file name and Location.
    This data is also going to be used for the 68 TMY3 stations rather than the
    more limited station match up that exists for stations where there is a nearby Meso West weather station

    Downloads the NASA POWER Latitude and Longitude combinations
     data for all the locations in station_df.
    Over the time period in station_df.

    :param station_df: DataFrame with the Latitude and Longitude combinations to be downloaded over a timescale
    :return: Nothing. Downloads NASA POWER GHI solar files.
    """

    count = 0
    for index, rows in station_df.iterrows():
        count += 1
        if count < 59:
            continue
        print(count)
        print(rows["Site_name"])
        print()

        csv_url = dnf.get_the_csv_url(str(rows["Latitude"]),
                                      rows["Longitude"],
                                      time_start,
                                      time_end)
        print(csv_url)
        dnf.output_new_nasa_csv_file("/home/nelson/PycharmProjects/"
                                     "TMY_NASA_RAWS Comparison/"
                                     "Alaska_State_Comparison/NASA POWER for TMY3/" +
                                     rows["Site_name"] + ".csv",
                                     csv_url)


if __name__ == "__main__":

    # Only needed if I have new TMY3 files that need to be renamed
    
    rename_all_tmy3_files(
        "/home/nelson/PycharmProjects/TMY_NASA_RAWS Comparison/Alaska_State_Comparison/TMY3 Alaska Original",
        "/home/nelson/PycharmProjects/TMY_NASA_RAWS Comparison/Alaska_State_Comparison/TMY3 Alaska/",
        "/home/nelson/PycharmProjects/TMY_NASA_RAWS Comparison/Alaska_State_Comparison/Setup")

    tmy3_meta_df = pd.read_csv("/home/nelson/PycharmProjects/TMY_NASA_RAWS Comparison/"
                               "Alaska_State_Comparison/Setup/tmy3_name_lat_long.csv", header=1)
    download_nasa_data_for_tmy3_comparison(tmy3_meta_df, "19910101", "20051230")

    meso_df = pd.read_csv("Alaska Station MetaData All Solar.csv")
    find_tmy3_meso_station_matchups(meso_df, tmy3_meta_df)
    tmy3_meso_matchup_df = pd.read_csv("TMY3_Meso_station_matchup.csv", header=1)
    os.chdir("/home/nelson/PycharmProjects/TMY_NASA_RAWS Comparison/Alaska_State_Comparison/Setup")

    tmy_df = pd.read_csv("TMY3_Meso_station_matchup.csv", header=1)
    filter_based_on_time_scale(tmy_df, 365)

    time_df = pd.read_csv("tmy3_meso_matchup_with_time_scale_365_days.csv")
    download_meso_data(time_df, "c03f5b124163456898c2a963fa365747")

    download_nasa_data_for_meso_comparison(time_df)





