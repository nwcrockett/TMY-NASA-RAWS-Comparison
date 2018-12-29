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

    nasa_direct = os.listdir(nasa_directory)
    nasa_direct.sort()
    nasa_direct = [item.split("$") for item in nasa_direct]

    tmy_index = 0
    tmy = []
    meso = []
    nasa = []
    for item in meso_direct:
        while tmy_direct[tmy_index][0] != item[0]:
            tmy_index += 1

        tmy.append(tmy_direct[tmy_index][0] + "." + tmy_direct[tmy_index][1])
        meso.append(item[0] + "$" + item[1])
        nasa.append(item[0] + "$" + item[1])

    return tmy, meso, nasa


def run_through_data_list(tmy_direct, tmy_path, meso_direct, meso_path, nasa_direct, nasa_path, time_df):
    """
    fixed this problem but I need to test

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
                        "year_difference_raws_tmy", "year_difference_nasa_tmy",
                        "year_difference_raws_nasa", "January_raws_tmy",
                        "February_raws_tmy", "March_raws_tmy",
                        "April_raws_tmy", "May_raws_tmy",
                        "June_raws_tmy", "July_raws_tmy",
                        "August_raws_tmy", "September_raws_tmy",
                        "October_raws_tmy", "November_raws_tmy",
                        "December_raws_tmy", "January_nasa_tmy",
                        "February_nasa_tmy", "March_nasa_tmy",
                        "April_nasa_tmy", "May_nasa_tmy",
                        "June_nasa_tmy", "July_nasa_tmy",
                        "August_nasa_tmy", "September_nasa_tmy",
                        "October_nasa_tmy", "November_nasa_tmy",
                        "December_nasa_tmy", "January_raws_nasa",
                        "February_raws_nasa", "March_raws_nasa",
                        "April_raws_nasa", "May_raws_nasa",
                        "June_raws_nasa", "July_raws_nasa",
                        "August_raws_nasa", "September_raws_nasa",
                        "October_raws_nasa", "November_raws_nasa",
                        "December_raws_nasa", "raws_data_problem_flag"]]

    for item in meso_direct:
        while tmy_match[tmy_index][0] != meso_match[meso_index][0]:
            tmy_index += 1
        meso_index += 1

        df_raws = read_csv(meso_path + "/" + item, header=6, skiprows=[7])
        df_tmy = read_csv(tmy_path + "/" + tmy_direct[tmy_index])
        df_nasa = read_csv(nasa_path + "/" + item, header=10)

        print(item)
        print(tmy_direct[tmy_index])

        temp = df_tmy['Date (MM/DD/YYYY)'].str.split("/")
        df_tmy[["month", "day", "year"]] = pd.DataFrame(temp.values.tolist(), index=df_tmy.index)

        df_raws.loc[df_raws["solar_radiation_set_1"] < 0, "solar_radiation_set_1"] = 0
        df_tmy.loc[df_tmy['GHI (W/m^2)'] < 0, 'GHI (W/m^2)'] = 0
        df_nasa.loc[df_nasa["ALLSKY_SFC_SW_DWN"] < 0, "ALLSKY_SFC_SW_DWN"] = 0

        df_raws, df_tmy = preprocess_raws_and_tmy_to_daily_sums(df_raws, df_tmy)

        y_diff_raws_tmy, y_diff_nasa_tmy, y_diff_raws_nasa = average_ghi_difference_by_year(df_tmy, df_nasa, df_raws)
        month_differences, raws_flag = average_ghi_difference_by_month(df_tmy, df_nasa, df_raws)

        print("year differences " + str(y_diff_raws_tmy))
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
                y_diff_raws_tmy, y_diff_nasa_tmy, y_diff_raws_nasa,
                month_differences[0][2], month_differences[1][2], month_differences[2][2],
                month_differences[3][2], month_differences[4][2], month_differences[5][2],
                month_differences[6][2], month_differences[7][2], month_differences[8][2],
                month_differences[9][2], month_differences[10][2], month_differences[11][2],
                month_differences[0][3], month_differences[1][3], month_differences[2][3],
                month_differences[3][3], month_differences[4][3], month_differences[5][3],
                month_differences[6][3], month_differences[7][3], month_differences[8][3],
                month_differences[9][3], month_differences[10][3], month_differences[11][3],
                month_differences[0][4], month_differences[1][4], month_differences[2][4],
                month_differences[3][4], month_differences[4][4], month_differences[5][4],
                month_differences[6][4], month_differences[7][4], month_differences[8][4],
                month_differences[9][4], month_differences[10][4], month_differences[11][4],
                raws_flag]
        difference_data.append(data)

    difference_data = pd.DataFrame(difference_data)
    difference_data.to_csv("/home/nelson/PycharmProjects/"
                           "TMY_NASA_RAWS Comparison/difference_data_alaska.csv")


def average_ghi_difference_by_year(df_tmy, df_nasa, df_raws):

    raws_yearly_sum = df_raws.groupby(df_raws.Date_time.dt.year)["solar"].sum()
    tmy_value = df_tmy["solar"].sum() / 1000
    nasa_yearly_sum = df_nasa.groupby("YEAR")["ALLSKY_SFC_SW_DWN"].sum()

    difference_raws_tmy = np.array(raws_yearly_sum) - float(tmy_value)
    difference_nasa_tmy = np.array(nasa_yearly_sum) - float(tmy_value)
    difference_raws_nasa = np.array(raws_yearly_sum) - np.array(nasa_yearly_sum)

    return np.average(difference_raws_tmy), np.average(difference_nasa_tmy), np.average(difference_raws_nasa)


def average_ghi_difference_by_month(df_tmy, df_nasa, df_raws):
    """
    Need to add two further filtering mechanisms into the raws data.
    When I added the nasa data comparison I ran into the problem that some of the
    raws data either had no solar data values at all or had a time frame of over a year but
    only had a month or two of data. Luckily when I select the months by year and cast the dataframe to
    an np array this shows up. The empty data cells as 0. While the missing data shows up as an empty array ex. [].
    So the below if statements are to handle these cases. While I've also added a flag that will indicate
    on the csv with all of the values when I have a problem with the raws data. Flag values are 1 for
    time frame problem. A 2 for the cells are empty. Flag value 3 is that the expected size of the raws
    array incorrect

    :param df_tmy:
    :param df_nasa:
    :param df_raws:
    :return:
    """
    month_dict = [["01", 'January'], ["02", 'February'], ["03", 'March'],
                  ["04", 'April'], ["05", 'May'], ["06", 'June'],
                  ["07", 'July'], ["08", 'August'], ["09", 'September'],
                  ["10", 'October'], ["11", 'November'], ["12", 'December']]

    differences_by_month = []
    flag = []

    for m in month_dict:
        df_raws_month = df_raws.loc[df_raws.Date_time.dt.month == int(m[0])]
        df_tmy_month = df_tmy.loc[df_tmy.date.dt.month == int(m[0])]
        df_nasa_month = df_nasa.loc[df_nasa["MO"] == int(m[0])]

        raw_sum_by_year = df_raws_month.groupby(df_raws_month.Date_time.dt.year).sum()
        nasa_sum_by_year = df_nasa_month.groupby("YEAR")["ALLSKY_SFC_SW_DWN"].sum().values
        tmy_sum_by_year = df_tmy_month.groupby(df_tmy_month.date.dt.year).sum()
        tmy_value = tmy_sum_by_year.values[0][0]
        raw_sum_by_year = raw_sum_by_year.values.transpose()[0]

        raw_sum_by_year = np.array(raw_sum_by_year)
        nasa_sum_by_year = np.array(nasa_sum_by_year)

        print("--------------------")
        print(m)
        print(raw_sum_by_year)
        print(nasa_sum_by_year)
        print("--------------------\n")

        if not raw_sum_by_year.size == 0:
            difference_nasa_tmy = np.average(nasa_sum_by_year - tmy_value)
            differences_by_month.append([m[0], m[1], "nan",
                                         difference_nasa_tmy, "nan"])
            flag.append(1)
        elif not raw_sum_by_year.any(0) and (raw_sum_by_year.size == nasa_sum_by_year.size):
            difference_raws_tmy = np.average(raw_sum_by_year - tmy_value)
            difference_nasa_tmy = np.average(nasa_sum_by_year - tmy_value)
            difference_raws_nasa = np.average(raw_sum_by_year - nasa_sum_by_year)
            differences_by_month.append([m[0], m[1], difference_raws_tmy,
                                         difference_nasa_tmy, difference_raws_nasa])
            flag.append(2)
        elif raw_sum_by_year.size != nasa_sum_by_year.size:
            difference_raws_tmy = np.average(raw_sum_by_year - tmy_value)
            difference_nasa_tmy = np.average(nasa_sum_by_year - tmy_value)
            differences_by_month.append([m[0], m[1], difference_raws_tmy,
                                         difference_nasa_tmy, "nan"])
            flag.append(3)
        else:
            difference_raws_tmy = np.average(raw_sum_by_year - tmy_value)
            difference_nasa_tmy = np.average(nasa_sum_by_year - tmy_value)
            difference_raws_nasa = np.average(raw_sum_by_year - nasa_sum_by_year)
            differences_by_month.append([m[0], m[1], difference_raws_tmy,
                                         difference_nasa_tmy, difference_raws_nasa])
            flag.append(0)

    return differences_by_month, flag


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

    tmy, meso, nasa = get_directory_lists(tmy_path, meso_path, nasa_path)

    time_df = read_csv("/home/nelson/PycharmProjects/TMY_NASA_RAWS Comparison/"
                       "Alaska_State_Comparison/Setup/tmy3_meso_matchup_with_time_scale_365_days.csv")

    run_through_data_list(tmy, tmy_path,
                          meso, meso_path,
                          nasa, nasa_path,
                          time_df)


