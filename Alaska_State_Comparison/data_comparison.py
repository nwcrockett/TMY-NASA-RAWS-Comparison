from pandas import read_csv
import pandas as pd
import numpy as np
import sys
import os


def preprocess_raws_and_tmy_to_daily_sums(df_raws, df_tmy):
    """
    Gets the raws and tmy datasets into a form that can be more easily used to sort and search data.

    Transforms the raws Date_time column from string to datetime objects.
    Then puts the hourly GHI solar values into a daily sum.

    The tmy data has it's GHI solar column put into sum for a day.
    Then has it's date column transformed to a datetime object

    :param df_raws: Initial Raws dataset
    :param df_tmy: Initial TMY data set
    :return: both a tmy and raws solar dataset with daily solar sums indexed by a datetime.
    """
    # done to change string type of "Date_Time" to datetime object for further operations
    df_raws["Date_Time"] = pd.to_datetime(df_raws["Date_Time"])
    raws_solar = df_raws.groupby(df_raws.Date_Time.dt.date)['solar_radiation_set_1'].sum() / 1000
    date = pd.to_datetime(raws_solar.index)
    d = {"Date_time": date, "solar": raws_solar}
    df_raws_out = pd.DataFrame(data=d)

    tmy_solar_sums_by_day = df_tmy.groupby(["year", "month", "day"])["GHI (W/m^2)"].sum() / 1000
    date = []
    for item in tmy_solar_sums_by_day.index:
        year = str(item[0]) + "-"
        month = str(item[1]) + "-"
        day = str(item[2])
        date.append(year + month + day)
    d = {"solar": tmy_solar_sums_by_day.values, "date": date}
    tmy_solar_out = pd.DataFrame(data=d)
    tmy_solar_out["date"] = pd.to_datetime(tmy_solar_out["date"])

    return df_raws_out, tmy_solar_out


def get_directory_lists(tmy_directory, meso_directory, nasa_directory):
    tmy_direct = os.listdir(tmy_directory)
    tmy_direct.sort()
    tmy_direct = [item.split(".") for item in tmy_direct]

    meso_direct = os.listdir(meso_directory)
    meso_direct.sort()
    meso_direct = [item.split("$") for item in meso_direct]

    tmy_index = 0
    tmy = []
    meso = []
    for item in meso_direct:
        while tmy_direct[tmy_index][0] != item[0]:
            tmy_index += 1

        tmy.append(tmy_direct[tmy_index][0] + "." + tmy_direct[tmy_index][1])
        meso.append(item[0] + "$" + item[1])

    return tmy, meso


def run_through_data_list(tmy_direct, tmy_path, meso_direct, meso_path, nasa_direct, nasa_path, time_df):
    """
    hand altered data for files in meso west with names FT. YUKON, MT. WHITTER, MT. NOAH
    removed periods for both file tmy3_meso_matchup_with_time_scale_365_days.csv and in directory
    Meso Station Data



    :param tmy_direct:
    :param tmy_path:
    :param meso_direct:
    :param meso_path:
    :param nasa_direct:
    :param nasa_path:
    :param time_df:
    :return:
    """
    tmy_match = [item.split(".") for item in tmy_direct]
    meso_match = [item.split("$") for item in meso_direct]

    tmy_index = 0
    meso_index = 0

    difference_data = [["meso_site_name", "tmy_site_name", "combined_site_name",
                        "meso_lat", "meso_long", "tmy_lat", "tmy_long",
                        "year_difference", "month_differences"]]

    for item in meso_direct:
        while tmy_match[tmy_index][0] != meso_match[meso_index][0]:
            tmy_index += 1
        meso_index += 1

        df_raws = read_csv(meso_path + "/" + item, header=6, skiprows=[7])
        df_tmy = read_csv(tmy_path + "/" + tmy_direct[tmy_index])
        print(item)
        print(tmy_direct[tmy_index])

        temp = df_tmy['Date (MM/DD/YYYY)'].str.split("/")
        df_tmy[["month", "day", "year"]] = pd.DataFrame(temp.values.tolist(), index=df_tmy.index)

        df_raws.loc[df_raws["solar_radiation_set_1"] < 0, "solar_radiation_set_1"] = 0
        df_tmy.loc[df_tmy['GHI (W/m^2)'] < 0, 'GHI (W/m^2)'] = 0

        df_raws, df_tmy = preprocess_raws_and_tmy_to_daily_sums(df_raws, df_tmy)

        year_diff = average_ghi_difference_by_year(df_tmy, "", df_raws)
        month_differences = average_ghi_difference_by_month(df_tmy, "", df_raws)

        print("year differences " + str(year_diff))
        print("month differences")
        print(month_differences)
        print()

        meso_lat = time_df.loc[time_df["Meso_site_name"] ==
                               meso_match[meso_index - 1][1].split(".")[0], ["meso_lat"]]
        meso_lat = meso_lat.iloc[0][0]
        meso_long = time_df.loc[time_df["Meso_site_name"] ==
                                meso_match[meso_index - 1][1].split(".")[0], ["meso_long"]]
        meso_long = meso_long.iloc[0][0]

        tmy_lat = time_df.loc[time_df["Meso_site_name"] ==
                              meso_match[meso_index -1][1].split(".")[0], ["tmy_lat"]]
        tmy_lat = tmy_lat.iloc[0][0]
        tmy_long = time_df.loc[time_df["Meso_site_name"] ==
                               meso_match[meso_index - 1][1].split(".")[0], ["tmy_long"]]
        tmy_long = tmy_long.iloc[0][0]
        meso_site_name = meso_match[meso_index - 1][1].split(".")[0]
        tmy_site_name = tmy_match[tmy_index][0]
        combined_site_name = item
        data = [meso_site_name, tmy_site_name, combined_site_name,
                meso_lat, meso_long, tmy_lat, tmy_long,
                year_diff, month_differences]
        difference_data.append(data)

    difference_data = pd.DataFrame(difference_data)
    difference_data.to_csv("/home/nelson/PycharmProjects/"
                           "TMY_NASA_RAWS Comparison/difference_data_alaska.csv")


def average_ghi_difference_by_year(df_tmy, df_nasa, df_raws):
    unique_years_raws = np.unique(df_raws.Date_time.dt.year)

    raws_yearly_sum = df_raws.groupby(df_raws.Date_time.dt.year)["solar"].sum()
    tmy_value = df_tmy["solar"].sum() / 1000
    year_num = unique_years_raws.astype(np.int)

    difference = np.array(raws_yearly_sum) - float(tmy_value)

    return np.average(difference)


def average_ghi_difference_by_month(df_tmy, df_nasa, df_raws):
    month_dict = [["01", 'January'], ["02", 'February'], ["03", 'March'],
                  ["04", 'April'], ["05", 'May'], ["06", 'June'],
                  ["07", 'July'], ["08", 'August'], ["09", 'September'],
                    ["10", 'October'], ["11", 'November'], ["12", 'December']]

    unique_years_raws = np.unique(df_raws.Date_time.dt.year)

    differences_by_month = []

    for m in month_dict:
        df_raws_month = df_raws.loc[df_raws.Date_time.dt.month == int(m[0])]
        df_tmy_month = df_tmy.loc[df_tmy.date.dt.month == int(m[0])]

        raw_sum_by_year = df_raws_month.groupby(df_raws_month.Date_time.dt.year).sum()
        # nasa_sum_by_year = df_nasa_month.groupby("YEAR")["ALLSKY_SFC_SW_DWN"].sum().values
        raw_show = df_raws_month
        # nasa_show = df_nasa_month
        tmy_sum_by_year = df_tmy_month.groupby(df_tmy_month.date.dt.year).sum()
        tmy_value = tmy_sum_by_year.values[0][0]
        raw_sum_by_year = raw_sum_by_year.values.transpose()[0]

        raw_sum_by_year = np.array(raw_sum_by_year)
        # nasa_sum_by_year = np.array(nasa_sum_by_year)

        difference = np.average(raw_sum_by_year - tmy_value)
        differences_by_month.append([m[0], m[1], difference])

    return differences_by_month


if __name__ == "__main__":
    """
    
    
    
    how to read each file
    
    df_nasa = read_csv("Fairbanks Nasa.csv", header=10)
    df_raws = read_csv("Fairbanks weather station.csv", header=6, skiprows=[7])
    df_tmy = read_csv("Fairbanks Airport tmy3.CSV")
    """
    tmy_path = "/home/nelson/PycharmProjects/TMY_NASA_RAWS Comparison/Alaska_State_Comparison/TMY3 Alaska"
    nasa_path = "/home/nelson/PycharmProjects/TMY_NASA_RAWS Comparison/Alaska_State_Comparison/NASA POWER data"
    meso_path = "/home/nelson/PycharmProjects/TMY_NASA_RAWS Comparison/Alaska_State_Comparison/Meso Station Data"

    tmy, meso = get_directory_lists(tmy_path, meso_path, nasa_path)
    nasa = []

    time_df = read_csv("/home/nelson/PycharmProjects/TMY_NASA_RAWS Comparison/Alaska_State_Comparison/Setup/tmy3_meso_matchup_with_time_scale_365_days.csv")


