import matplotlib.pyplot as plt


def all_month_over_years(y_min, y_max, differences_by_month, month_names, years, title, ylabel):
    plt.figure(figsize=(12, 12))
    plt.xlabel("Years")
    plt.ylabel(ylabel)
    plt.title(title)
    plt.ylim(y_min, y_max)
    for dif, name, y in zip(differences_by_month, month_names, years):
        plt.plot(y, dif, label=name)
    plt.legend(prop={'size': 16})
    plt.savefig("binned_by_months/" + title)
    plt.show()


def percent_difference(x, y, title, x_label, location):
    plt.plot(x, y)
    plt.xlabel(x_label)
    plt.ylabel("%")
    plt.title(title)
    plt.savefig(location + title)
    plt.show()


def all_year_overview_single_month(year, raws_values, nasa_values, tmy_value, title):
    bar_width = 0.35
    plt.bar(year, raws_values, bar_width, label="raws radiation")
    plt.bar(year - bar_width, nasa_values, bar_width, label="NASA POWER radiation")
    plt.axhline(y=tmy_value, label="tmy value = %.2f" % tmy_value, color="r")
    plt.xlabel("year")
    plt.ylabel("kWh/m2/year")
    plt.title(title)


def yearly_overview(year, raws_values, nasa_values, tmy_value, title):
    bar_width = 0.35
    ax = plt.axes()
    ax.bar(year, raws_values, bar_width, label="raws station radiation")
    ax.bar(year - bar_width, nasa_values, bar_width, label="NASA POWER radiation")
    ax.axhline(y=tmy_value, label="tmy value = %.2f" % tmy_value, color="r")
    ax.xaxis.set_major_locator(plt.MaxNLocator(8))
    ax.yaxis.set_major_locator(plt.MaxNLocator(8))
    ax.set_xlabel("year")
    ax.set_ylabel("kWh/m2/year")
    plt.legend(prop={'size': 10})
    plt.title(title)
    plt.savefig("graphed_by_year/" + title)
    plt.show()


def graph_of_one_year(months, raws_values, nasa_values, tmy_values, title):
    bar_width = 0.25
    plt.bar(months, raws_values, bar_width, label="raws radiation")
    plt.bar(months - bar_width, nasa_values, bar_width, label="NASA POWER radiation")
    plt.bar(months + bar_width, tmy_values, bar_width, label="TMY radiation")
    plt.xlabel("Month of the year")
    plt.ylabel("kWh/m2/month")
    plt.title(title)