import pandas as pd
import matplotlib.pyplot as plt


flags = [1, 2, 3, 4, 5]
columns = ['January_nasa_tmy', 'February_nasa_tmy',
               'March_nasa_tmy', 'April_nasa_tmy', 'May_nasa_tmy',
               'June_nasa_tmy', 'July_nasa_tmy', 'August_nasa_tmy',
               'September_nasa_tmy', 'October_nasa_tmy', 'November_nasa_tmy',
               'December_nasa_tmy']

raw_tmy = ["January_raws_tmy", "February_raws_tmy",
           "March_raws_tmy", "April_raws_tmy",
           "May_raws_tmy", "June_raws_tmy",
           "July_raws_tmy", "August_raws_tmy",
           "September_raws_tmy", "October_raws_tmy",
           "November_raws_tmy", "December_raws_tmy"]


def plot_by_flag_and_month_tmy_nasa(df):
    flag_name = {1: "North above 65 Latitude", 2: "West coastline", 3: "kenai peninsula",
                 4: "Southeast", 5: "Interior", 6: "Whole state"}

    averages = []
    for flag in flags:
        df_alaska = df[df["flag"] == flag]

        for month in columns:
            averages.append(df_alaska[month].mean())

    y_upper_limit = max(averages)
    y_lower_limit = min(averages)

    for flag in flags:
        df_alaska = df[df["flag"] == flag]
        averages = []
        std = []

        for month in columns:
            averages.append(df_alaska[month].mean())
            std.append(df_alaska[month].std())

        plt.ylim(y_lower_limit - 40, y_upper_limit + 40)
        plt.errorbar(columns, averages, std, barsabove=True)
        plt.title(flag_name[flag] + " nasa - tmy")
        plt.xlabel("Month")
        plt.xticks(rotation='vertical')
        plt.ylabel("kWh/m^2/month")
        plt.savefig("/home/nelson/PycharmProjects/TMY_NASA_RAWS Comparison"
                    "/Alaska_State_Comparison/state maps/average and std nasa - tmy/" + flag_name[flag] + ".png")
        plt.show()

    average = []
    standard_dev = []
    for month in columns:
        average.append(df[month].mean())
        standard_dev.append(df[month].std())

    plt.ylim(y_lower_limit - 40, y_upper_limit + 40)
    plt.errorbar(columns, average, standard_dev, barsabove=True)
    plt.title(flag_name[6]  + " nasa - tmy")
    plt.xlabel("Month")
    plt.xticks(rotation='vertical')
    plt.ylabel("kWh/m^2/month")
    plt.savefig("/home/nelson/PycharmProjects/TMY_NASA_RAWS Comparison"
                "/Alaska_State_Comparison/state maps/average and std nasa - tmy/" + flag_name[6] + ".png")
    plt.show()


def plot_by_flag_and_month_raws(df):
    flag_name = {1: "North above 65 Latitude", 2: "West coastline", 3: "kenai peninsula",
                 4: "Southeast", 5: "Interior", 6: "Whole state"}

    averages = []
    for flag in flags:
        df_alaska = df[df["flag"] == flag]

        for month in raw_tmy:
            averages.append(df_alaska[month].mean())

    y_upper_limit = max(averages)
    y_lower_limit = min(averages)

    for flag in flags:
        df_alaska = df[df["flag"] == flag]
        averages = []
        std = []

        for month in raw_tmy:
            averages.append(df_alaska[month].mean())
            std.append(df_alaska[month].std())

        plt.ylim(y_lower_limit - 40, y_upper_limit + 40)
        plt.errorbar(columns, averages, std, barsabove=True)
        plt.title(flag_name[flag] + " raws - tmy")
        plt.xlabel("Month")
        plt.xticks(rotation='vertical')
        plt.ylabel("kWh/m^2/month")
        plt.savefig("/home/nelson/PycharmProjects/TMY_NASA_RAWS Comparison"
                    "/Alaska_State_Comparison/state maps/average and std raws - tmy/" + flag_name[flag] + ".png")
        plt.show()

    average = []
    standard_dev = []
    for month in raw_tmy:
        average.append(df[month].mean())
        standard_dev.append(df[month].std())

    plt.ylim(y_lower_limit - 40, y_upper_limit + 40)
    plt.errorbar(raw_tmy, average, standard_dev, barsabove=True)
    plt.title(flag_name[6] + " raws - tmy")
    plt.xlabel("Month")
    plt.xticks(rotation='vertical')
    plt.ylabel("kWh/m^2/month")
    plt.savefig("/home/nelson/PycharmProjects/TMY_NASA_RAWS Comparison"
                "/Alaska_State_Comparison/state maps/average and std raws - tmy/" + flag_name[6] + ".png")
    plt.show()


if __name__ == "__main__":
    df_nasa = pd.read_csv("/home/nelson/PycharmProjects/"
                     "TMY_NASA_RAWS Comparison/Alaska_State_Comparison/tmy_nasa_comparison_hand_altered.csv")
    df_raws = pd.read_csv("/home/nelson/PycharmProjects/TMY_NASA_RAWS Comparison/"
                          "Alaska_State_Comparison/difference_data_alaska.csv", header=1)
    plot_by_flag_and_month_tmy_nasa(df_nasa)
    plot_by_flag_and_month_raws(df_raws)




