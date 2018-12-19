import pandas as pd
import csv
import os
import Meso_station_download as msd
import download_nasa_file as dnf


def rename_all_tmy3_files():
    """
    renames all of the TMY3 files to the site name rather than a number
    also gets the site name, lat, and long from the tmy3 files for
    each file. Then outputs into a DataFrame that can then be used as a source
    for download meso raws station data and NASA data

    :return: Nothing. changes the names of all TMY3 file. Creates new Meta data file
    """
    os.chdir("/home/nelson/PycharmProjects/TMY_NASA_RAWS Comparison/Alaska_State_Comparison/TMY3 Alaska Original")
    directory = os.listdir()

    tmy3_name_lat_long = [["Site_name", "Latitude", "Longitude"]]

    for item in directory:
        with open(item) as f:
            mycsv = csv.reader(f)
            mycsv = list(mycsv)
            name = mycsv[0][1]
            if name == "ANCHORAGE/ELMENDORF":
                name = "ANCHORAGE_ELMENDORF"
            elif name == "FAIRBANKS/EIELSON A":
                name = "FAIRBANKS_EIELSON A"
            lat = mycsv[0][4]
            long = mycsv[0][5]
        f.close()
        tmy_df = pd.read_csv(item, header=1)
        tmy_df.to_csv("/home/nelson/PycharmProjects/TMY_NASA_RAWS Comparison/Alaska_State_Comparison/TMY3 Alaska/"
                      + name + ".csv")
        tmy3_name_lat_long.append([name, lat, long])

    meta_data = pd.DataFrame(tmy3_name_lat_long)
    os.chdir("/home/nelson/PycharmProjects/TMY_NASA_RAWS Comparison/Alaska_State_Comparison/Setup")
    meta_data.to_csv("tmy3_name_lat_long.csv")


def find_tmy3_meso_station_matchups(meso_df, tmy3_meta_df):
    """
    Finds the matchups between a TMY3 site and Meso station
    within 1 degree of longitude or latitude and outputs that data as a csv

    :param meso_df: Meso csv/dataframe with the solar metadata for the entire state of Alaska
    :param tmy3_meta_df: TMY3 csv with site name lat and lond
    :return: returns nothing just outputs a csv with the matchups between a TMY3 and Meso stations
    """
    tmy3_meso_matchup = [["TMY3_site_name", "Meso_site_name",
                          "tmy_lat", "tmy_long", "meso_lat",
                          "meso_long", "meso_start", "meso_end",
                          "meso_id"]]
    missing_data = [["TMY3_site_name", "tmy_lat", "tmy_long"]]
    for index, row in tmy3_meta_df.iterrows():
        temp = meso_df.loc[(meso_df["LATITUDE"].round() == round(row["Latitude"]))
                           & (meso_df["LONGITUDE"].round() == round(row["Longitude"]))]
        if len(temp.index) == 0:
            missing_data.append([row["Site_name"], row["Latitude"], row["Longitude"]])
            continue
        for i, r in temp.iterrows():
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
            tmy3_meso_matchup.append([row["Site_name"], r["NAME"],
                                     row["Latitude"], row["Longitude"],
                                     r["LATITUDE"], r["LONGITUDE"],
                                     start_time, end_time,
                                     r["STID"]])

    tmy_meso_df = pd.DataFrame(tmy3_meso_matchup)
    tmy_meso_df.to_csv("TMY3_Meso_station_matchup.csv")
    missing_data = pd.DataFrame(missing_data)
    missing_data.to_csv("TMY3 with no Meso Stations.csv")


def filter_for_meso_stations_for_time_scale(tmy3_meso_df, days):
    """
    Filters the csv/dataframe with the TMY3 and Meso station matchups to a dataframe/csv result
    over a time scale. Recommend timescales of at least a month or more since many stations in the
    Meso API have timescales of just one day

    hand altered data for files in meso west with names FT. YUKON, MT. WHITTER, MT. NOAH
    removed periods for both file tmy3_meso_matchup_with_time_scale_365_days.csv and in directory
    Meso Station Data

    need to remove periods in code

    :param tmy3_meso_df:
    :param days: time scale wanted in days. Recommended in timescales of at least a month
    :return: Nothing. Outputs a csv file with
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


def download_meso_data(time_scale, token_for_meso_api):
    count = 0
    for index, rows in time_scale.iterrows():
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


def download_nasa_data(station_df):
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
                                     "Alaska_State_Comparison/NASA POWER data/" +
                                     rows["TMY3_site_name"] + "$" +
                                     rows["Meso_site_name"] + ".csv",
                                     csv_url)


if __name__ == "__main__":
    # tmy3_meta_df = pd.read_csv("tmy3_name_lat_long.csv", header=1)
    # meso_df = pd.read_csv("Alaska Station MetaData All Solar.csv")
    # find_tmy3_meso_station_matchups(meso_df, tmy3_meta_df)
    # tmy3_meso_matchup_df = pd.read_csv("TMY3_Meso_station_matchup.csv", header=1)
    os.chdir("/home/nelson/PycharmProjects/TMY_NASA_RAWS Comparison/Alaska_State_Comparison/Setup")

    # tmy_df = pd.read_csv("TMY3_Meso_station_matchup.csv", header=1)
    # filter_for_meso_stations_for_time_scale(tmy_df, 365)

    time_df = pd.read_csv("tmy3_meso_matchup_with_time_scale_365_days.csv")
    # download_meso_data(time_df, "c03f5b124163456898c2a963fa365747")

    # download_nasa_data(time_df)



