from pandas import read_csv
import pandas as pd
import numpy as np
import sys
import Comparison_graphs as cg


def difference_calculation(arry1, arry2):
    arry = arry1 - arry2
    a_min = np.amin(arry)
    a_max = np.amax(arry)

    return arry, a_min, a_max


def graph_by_month_over_year(df_tmy, df_nasa, df_raws):
    """

    :param df_tmy: tmy dataframe. Only covers one year
    :param df_nasa: Nasa dataframe.
    :param df_raws: RAWS station dataframe.
    :return:
    """
    unique_years_raws = np.unique(df_raws.Date_time.dt.year)
    unique_years_nasa = np.unique(df_nasa["YEAR"].values)
    month_dict = {"01": 'January', "02": 'February', "03": 'March', "04": 'April', "05": 'May', "06": 'June',
                  "07": 'July', "08": 'August', "09": 'September', "10": 'October',
                  "11": 'November', "12": 'December'}

    pd_months = []
    difference_months_raws_nasa = []
    difference_months_raws_tmy = []
    difference_months_nasa_tmy = []
    month_names = []
    pd_y_min = 0
    pd_y_max = 0
    d_y_min_raws_nasa = 0
    d_y_max_raws_nasa = 0
    d_y_min_raws_tmy = 0
    d_y_max_raws_tmy = 0
    d_y_min_nasa_tmy = 0
    d_y_max_nasa_tmy = 0
    years = []

    if not (bool(set(unique_years_raws).intersection(unique_years_nasa))):
        print(unique_years_raws)
        print(unique_years_nasa)
        print(type(unique_years_nasa[0]))
        print(type(unique_years_raws[0]))
        print("I do not have a year matchup")
        sys.exit(0)

    for m, mn in month_dict.items():
        print(mn)
        month_names.append(mn)

        df_nasa_month = df_nasa.loc[df_nasa["MO"] == int(m)]
        df_raws_month = df_raws.loc[df_raws.Date_time.dt.month == int(m)]
        df_tmy_month = df_tmy.loc[df_tmy.date.dt.month == int(m)]

        # raws data missing 2008 values for jan to may
        if mn == 'January' or mn == "February" or mn == 'March':
            df_nasa_month = df_nasa_month.loc[df_nasa_month["YEAR"] != 2006]

        if mn == "February":
            df_nasa_month = df_nasa_month.loc[df_nasa_month["YEAR"] != 2018]

        unique_years_raw = np.unique(df_raws_month.Date_time.dt.year.values)
        year_num = unique_years_raw.astype(np.int)
        years.append(year_num)
        unique_years_nasa = np.unique(df_nasa_month["YEAR"].values)

        raw_sum_by_year = df_raws_month.groupby(df_raws_month.Date_time.dt.year).sum()
        nasa_sum_by_year = df_nasa_month.groupby("YEAR")["ALLSKY_SFC_SW_DWN"].sum().values
        raw_show = df_raws_month
        nasa_show = df_nasa_month
        tmy_sum_by_year = df_tmy_month.groupby(df_tmy_month.date.dt.year).sum()
        tmy_value = tmy_sum_by_year.values[0][0]
        raw_sum_by_year = raw_sum_by_year.values.transpose()[0]

        cg.all_year_overview_single_month(
            year_num,
            raw_sum_by_year,
            nasa_sum_by_year[0:len(year_num)],
            tmy_value,
            mn + " Overview"
        )

        raw_sum_by_year = np.array(raw_sum_by_year)
        nasa_sum_by_year = np.array(nasa_sum_by_year)

        try:
            percent_difference = ((raw_sum_by_year - nasa_sum_by_year) /
                              ((raw_sum_by_year + nasa_sum_by_year) / 2)) * 100
        except:
            print(raw_show)
            print(nasa_show)

        pd_months.append(percent_difference)
        cg.percent_difference(
             year_num,
             percent_difference,
             mn + " percent difference",
             "year",
             "binned_by_months/percent_difference/")

        dif_min = np.amin(percent_difference)
        dif_max = np.amax(percent_difference)

        if dif_min < pd_y_min:
            pd_y_min = dif_min
        if dif_max > pd_y_max:
            pd_y_max = dif_max

        difference, dif_min, dif_max = difference_calculation(raw_sum_by_year, nasa_sum_by_year)
        difference_months_raws_nasa.append(difference)

        if dif_min < d_y_min_raws_nasa:
            d_y_min_raws_nasa = dif_min
        if dif_max > d_y_max_raws_nasa:
            d_y_max_raws_nasa = dif_max

        difference, dif_min, dif_max = difference_calculation(raw_sum_by_year, tmy_value)
        difference_months_raws_tmy.append(difference)

        if dif_min < d_y_min_raws_tmy:
            d_y_min_raws_tmy = dif_min
        if dif_max > d_y_max_raws_tmy:
            d_y_max_raws_tmy = dif_max

        difference, dif_min, dif_max = difference_calculation(nasa_sum_by_year, tmy_value)
        difference_months_nasa_tmy.append(difference)

        if dif_min < d_y_min_nasa_tmy:
            d_y_min_nasa_tmy = dif_min
        if dif_max > d_y_max_nasa_tmy:
            d_y_max_nasa_tmy = dif_max

        print("for loop complete\n")


    cg.all_month_over_years(
        d_y_min_raws_nasa,
        d_y_max_raws_nasa,
        difference_months_raws_nasa,
        month_names,
        years,
        "Difference of raws - nasa",
        "kWh/m2/year"
    )
    cg.all_month_over_years(
        d_y_min_raws_tmy,
        d_y_max_raws_tmy,
        difference_months_raws_tmy,
        month_names,
        years,
        "Difference of raws - tmy",
        "kWh/m2/year"
    )
    cg.all_month_over_years(
        d_y_min_nasa_tmy,
        d_y_max_nasa_tmy,
        difference_months_nasa_tmy,
        month_names,
        years,
        "Difference of nasa - tmy",
        "kWh/m2/year"
    )
    cg.all_month_over_years(pd_y_min, pd_y_max, pd_months,
                            month_names, years, "percent difference 12 months raws - nasa", "%")


def graph_by_year(df_tmy, df_nasa, df_raws):
    """

    :param df_tmy:
    :param df_nasa:
    :param df_raws:
    :return:
    """
    unique_years_nasa = np.unique(df_nasa["YEAR"].values)
    unique_years_raws = np.unique(df_raws.Date_time.dt.year)

    if not (bool(set(unique_years_raws).intersection(unique_years_nasa))):
        print(unique_years_raws)
        print(unique_years_nasa)
        print(type(unique_years_nasa[0]))
        print(type(unique_years_raws[0]))
        print("I do not have a year matchup")
        sys.exit(0)

    raws_yearly_sum = df_raws.groupby(df_raws.Date_time.dt.year)["solar"].sum()
    nasa_yearly_sum = df_nasa.groupby("YEAR")["ALLSKY_SFC_SW_DWN"].sum()
    tmy_value = df_tmy["solar"].sum()
    year_num = unique_years_raws.astype(np.int)

    cg.yearly_overview(
        year_num,
        raws_yearly_sum,
        nasa_yearly_sum,
        tmy_value,
        "Yearly overview"
    )

    for yr, yn in zip(unique_years_raws, unique_years_nasa):
        df_raws_month = df_raws.loc[df_raws.Date_time.dt.year == yr]
        raws_months = np.unique(df_raws_month.Date_time.dt.month)
        months_nasa = np.unique(df_nasa.loc[df_nasa["YEAR"] == yn, "MO"])

        if yr == 2005 or yr == 2006 or yr == 2018:
            continue

        if not (bool(set(raws_months).intersection(months_nasa))):
            # I know I will get a hit at 2008
            print(raws_months)
            print(months_nasa)
            print(type(raws_months[0]))
            print(type(months_nasa[0]))
            print("I do not have a month match up at year " + str(yr))
            continue

        df_year_nasa = df_nasa[(df_nasa["YEAR"] == yn)]
        raws_year_sum = df_raws_month.groupby(df_raws_month.Date_time.dt.month)["solar"].sum()
        nasa_monthly_sums = df_year_nasa.groupby("MO")["ALLSKY_SFC_SW_DWN"].sum()
        tmy_year_sums = df_tmy.groupby(df_tmy.date.dt.month)["solar"].sum()

        print(yr)
        print(raws_year_sum)
        print(nasa_monthly_sums)
        print(tmy_year_sums)

        cg.graph_of_one_year(
            raws_months,
            raws_year_sum,
            nasa_monthly_sums,
            tmy_year_sums,
            str(yr) + " graph of all months"
        )


def preprocess_raws_and_tmy_to_daily_sums(df_raws, df_tmy):
    """

    :param df_raws:
    :param df_tmy:
    :return:
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


if __name__ == "__main__":
    """
    requires running both nasa "nasa API connect to get new file.py" and
     "API request for stations data for given timeseries.py" 
     to obtain the required nasa data and RAWS station data to do the comparsions
    """
    df_nasa = read_csv("Fairbanks Nasa.csv", header=10)
    df_raws = read_csv("Fairbanks weather station.csv", header=6, skiprows=[7])
    df_tmy = read_csv("Fairbanks Airport tmy3.CSV", header=1)

    temp = df_tmy['Date (MM/DD/YYYY)'].str.split("/")
    df_tmy[["month", "day", "year"]] = pd.DataFrame(temp.values.tolist(), index=df_tmy.index)

    # possibly an unnecessary operation but avoids me having to check for negative values
    df_nasa.loc[df_nasa["ALLSKY_SFC_SW_DWN"] < 0, "ALLSKY_SFC_SW_DWN"] = 0
    df_raws.loc[df_raws["solar_radiation_set_1"] < 0, "solar_radiation_set_1"] = 0
    df_tmy.loc[df_tmy['GHI (W/m^2)'] < 0, 'GHI (W/m^2)'] = 0

    df_raws, df_tmy = preprocess_raws_and_tmy_to_daily_sums(df_raws, df_tmy)

    graph_by_month_over_year(df_tmy, df_nasa, df_raws)
    graph_by_year(df_tmy, df_nasa, df_raws)


