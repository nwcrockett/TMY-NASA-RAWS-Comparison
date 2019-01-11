"""
Nelson Crockett
Difference data calculation script that is used to find the differences by both year and months
between TMY and NASA POWER data sets

"""

from pandas import read_csv
import pandas as pd
import numpy as np
import os


def preprocess_data(df_tmy, df_nasa):
    """
    Used in tmy_nasa_comparison()

    Splits df_tmy date column into separate month, day year columns for indexing based on month and year.
    Ensures that no 0 or less than 0 values are in either of the DataFrames. Takes the
    solar values which are put into kWh/m^2/day and a datetime column is created name "date". This is the
    DataFrame that is used for the data analysis.


    :param df_tmy:
    :param df_nasa:
    :return:
    """
    temp = df_tmy['Date (MM/DD/YYYY)'].str.split("/")
    df_tmy[["month", "day", "year"]] = pd.DataFrame(temp.values.tolist(), index=df_tmy.index)

    df_tmy.loc[df_tmy['GHI (W/m^2)'] < 0, 'GHI (W/m^2)'] = 0
    df_nasa.loc[df_nasa["ALLSKY_SFC_SW_DWN"] < 0, "ALLSKY_SFC_SW_DWN"] = 0

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

    return tmy_solar_out, df_nasa


def monthly_differences(df_tmy, df_nasa):
    """
    Used in tmy_nasa_comparison()

    Calculates the average differences per month between the NASA and TMY3 data. These differences are
    a single value for TMY3 since the data only covers one year. For NASA it is an numpy array covering
    the amount of years in the DataFrame. The average value of difference array that results from the nasa
    array being subtracted by the tmy value is what is returned.

    :param df_tmy: TMY3 DataFrame
    :param df_nasa: NASA POWER DataFrame
    :return: The average differences between the NASA POWER and TMY3 for all 12 months in a year
    """
    month_dict = [["01", 'January'], ["02", 'February'], ["03", 'March'],
                  ["04", 'April'], ["05", 'May'], ["06", 'June'],
                  ["07", 'July'], ["08", 'August'], ["09", 'September'],
                  ["10", 'October'], ["11", 'November'], ["12", 'December']]

    differences_by_month = []

    for m in month_dict:
        df_tmy_month = df_tmy.loc[df_tmy.date.dt.month == int(m[0])]
        df_nasa_month = df_nasa.loc[df_nasa["MO"] == int(m[0])]

        nasa_sum_by_year = df_nasa_month.groupby("YEAR")["ALLSKY_SFC_SW_DWN"].sum().values
        tmy_sum_by_year = df_tmy_month.groupby(df_tmy_month.date.dt.year).sum()
        tmy_value = tmy_sum_by_year.values[0][0]

        nasa_sum_by_year = np.array(nasa_sum_by_year)

        print("--------------------")
        print(m)
        print(tmy_value)
        print(nasa_sum_by_year)
        print("--------------------\n")

        difference_nasa_tmy = np.average(nasa_sum_by_year - tmy_value)
        differences_by_month.append([m[0], m[1], difference_nasa_tmy])

    return differences_by_month


def tmy_nasa_comparison(nasa_path, tmy_path, df_tmy_meta_data):
    """
    This Function will take in the path names and lists of file names for all of the tmy and nasa
    solar files. It will then calculate the average difference between tmy and nasa power by year.
    Following that the average difference between the datasets by each of the months in a year.
    The results of this are outputted to a DataFrame that is then written to a csv file.

    :param nasa_path: path to the nasa files
    :param tmy_path: path to the tmy files
    :param df_tmy_meta_data: Meta data DataFrame with latitude and longitude values
    :return: can be setup to output a DataFrame. Currently returns nothing. Writes a csv file with difference data
    """
    file_names = os.listdir(tmy_path)
    file_names.sort()

    difference_data = [["Site_Name", "tmy_lat", "tmy_long",
                        "year_difference_nasa_tmy", "January_nasa_tmy",
                        "February_nasa_tmy", "March_nasa_tmy",
                        "April_nasa_tmy", "May_nasa_tmy",
                        "June_nasa_tmy", "July_nasa_tmy",
                        "August_nasa_tmy", "September_nasa_tmy",
                        "October_nasa_tmy", "November_nasa_tmy",
                        "December_nasa_tmy"]]

    for file in file_names:
        name = file.split(".")[0]

        df_tmy = read_csv(tmy_path + "/" + file)
        df_nasa = read_csv(nasa_path + "/" + file, header=10)

        print(file)

        df_tmy, df_nasa = preprocess_data(df_tmy, df_nasa)

        # Calculation for yearly differences. Units in kWh/m^2/year
        tmy_value = df_tmy["solar"].sum() / 1000
        nasa_yearly_sum = df_nasa.groupby("YEAR")["ALLSKY_SFC_SW_DWN"].sum()
        difference_nasa_tmy = np.array(nasa_yearly_sum) - float(tmy_value)
        yearly_difference_average = np.average(difference_nasa_tmy)
        month_differences = monthly_differences(df_tmy, df_nasa)

        print(name)
        tmy_lat = df_tmy_meta_data.loc[df_tmy_meta_data["Site_name"] == name, "Latitude"].values[0]
        tmy_long = df_tmy_meta_data.loc[df_tmy_meta_data["Site_name"] == name, "Longitude"].values[0]

        data = [name, tmy_lat, tmy_long,
                yearly_difference_average,
                month_differences[0][2], month_differences[1][2], month_differences[2][2],
                month_differences[3][2], month_differences[4][2], month_differences[5][2],
                month_differences[6][2], month_differences[7][2], month_differences[8][2],
                month_differences[9][2], month_differences[10][2], month_differences[11][2]]
        difference_data.append(data)

    difference_data = pd.DataFrame(difference_data)
    difference_data.to_csv("/home/nelson/PycharmProjects/TMY_NASA_RAWS Comparison"
                           "/Alaska_State_Comparison/tmy_nasa_comparison.csv")


if __name__ == "__main__":

    tmy_meta_data_comp = read_csv("/home/nelson/PycharmProjects/TMY_NASA_RAWS Comparison/"
                                  "Alaska_State_Comparison/Setup/tmy3_name_lat_long.csv", header=1)
    tmy_file_path = "/home/nelson/PycharmProjects/TMY_NASA_RAWS Comparison/Alaska_State_Comparison/TMY3 Alaska"
    nasa_file_path = "/home/nelson/PycharmProjects/TMY_NASA_RAWS Comparison/Alaska_State_Comparison/NASA POWER for TMY3"

    tmy_nasa_comparison(
        nasa_file_path,
        tmy_file_path,
        tmy_meta_data_comp)



