Overview of the entire process for how the TMY3, NASA POWER, and MESO West comparisons are setup

There are two single point comparisons that were done first. They are in the folders
and represent Michchumina and Fairbanks Alaska. These points were analysed first to obtain an
estimate of where or not further analysis had potential with this data.

This readme breaks down the work done on this project in the following format. Python scripts that are
used in multiple single point analysis. Then the API download scripts that obtain data from NASA POWER and
MESO west. After that each single point analysis is broken down. Finally the analysis for the comparison of
the state of Alaska is broken down.

########################################################################################################################

Overview of API download scripts download_nasa_file.py, Meso_station_download.py and graphing Comparison_graphs.py,
Subplot_Comparison_Graphs.py
------------------------------------------------------------------------------------------------------------------------

API download scripts download_nasa_file.py and Meso_station_download.py
------------------------------------------------------------------------------------------------------------------------
These are the scripts that download individual csv files from single point latitude and longitude combinations.

download_nasa_file.py requires a start and end time along with a latitude and longitude to begin downloading data.
The time entered cannot exceed the current date. Times entered that are within a 7 day period from the current date
will result in data that is undefined. Data will be in the format total GHI solar summed by day. Data file will
be a csv file.

Alaska Station MetaData All Solar.csv IS REQUIRED for Meso_station_download.py. This is due to the MESO WEST API
requiring a station id to download a file. Due to that Alaska Station MetaData All Solar.csv is a file that holds
the metadata for all MESO WEST stations in Alaska with solar data.

________________________________________________________________________________________________________________________

Comparison_graphs.py and Subplot_Comparison_Graphs.py
------------------------------------------------------------------------------------------------------------------------

This is the python script that contains all of the graphing functions for both the Fairbanks and Michchumina point
comparisons. These graphing functions are only useful for single point comparisons.

Within both Comparison_graphs.py and Subplot_Comparison_Graphs.py the graphs are divided up into two different types of
time analysis types. Either a monthly analysis that extents over a number of years. Or a Yearly analysis that covers a
range of months.

The monthly graphing functions are as follows:
from Comparison_graphs.py: all_year_overview_single_month and all_month_over_years

from Subplot_Comparison_Graphs.py: yearly_overview, all_year_overview_single_month, all_month_over_years

Things to note: The month is what remains constant for each of these graphs while the year changes,
There are both single month graphs and multi-month graphs.

Yearly graphing functions:
from Comparison_graphs.py: yearly_overview, graph_of_one_year

from Subplot_Comparison_Graphs.py: yearly_overview, graph_of_one_year

Things to note: The year will remain constant while the months change, multi-year and single year graphs.

function percent_difference just graphs a difference between two data points in both scripts
________________________________________________________________________________________________________________________


Michchumina and Fairbanks single point overviews

Both of these single point locations compare the following three datasets. The NASA POWER, MESO West, and TMY3
datasets for Michchumina and Fairbanks.
########################################################################################################################

All graphing functions are located in Comparison_graphs.py and Subplot_Comparison_Graphs.py

Data for Michchumina:
Lake Minchumina weather station.csv # Meso West data
Minchumina Nasa.csv # NASA POWER data
USA AK Minchumina (TMY3).csv  # TMY3 data

Data for Fairbanks:
Fairbanks Airport tmy3.CSV # TMY3 data
Fairbanks Nasa.csv  # NASA POWER data
Fairbanks weather station.csv  # MESO West data


NASA_TMY_RAWS_comparison.py
------------------------------------------------------------------------------------------------------------------------
This script contains all of the dataset manipulation and handles picking out data correctly to do all comparisons

from the main function:
step one:  Import datasets
step two: remove all negative values from dataset and replace with zeros
step three: function preprocess_raws_and_tmy_to_daily_sums
step four: graph_by_month_over_year
final step: graph_by_year


preprocess_raws_and_tmy_to_daily_sums:
Both the TMY3 and the Meso West datasets have hourly data. While NASA POWER contains the sum of the solar energy
for that day in the site given. So to do a comparison for all three datasets The TMY3 and Meso West data must also
have there data points summed by day. Which is handled in this function. Then to handle parsing the data to do correct
comparisons the MESO West and TMY3 data has a datetime column added to it. Allowing correct selection by year-month-day

graph_by_month_over_year:
This function compares all three datasets over all twelve months over the time in years that the Meso West data covers.
If either the NASA data or Meso West data does not possess the same time in years this function will not work.
At this point a for loop is entered for each month. With a subselection of each dataset pulled out for that month.
February, March, and April are dropped in year 2008 since the corresponding raws data is missing.
This is also true for October 2018.
At this point all three datasets have the sum of the solar data for that month summed up bu year. For example
all the solar energy that occurred for every day in April 2007 is summed up into a single value.
This is then graphed for that month.
The percent difference between the solar energy for NASA POWER and Meso West is then calculated and graphed.
Following this the percent differences between all three datasets is then calculated and graphed.
Finally a percent difference is calculated for all twelve months for one graph for the percent difference
between NASA POWER and MESO West.

graph_by_year:
This function compares all three datasets over the years of data that Meso West possesses.
If either the NASA data or Meso West data does not possess the same time in years this function will not work.
All three datasets have the total solar energy summed up by year. For example all the solar energy for 2007 is summed
into a single value.
This is then graphed.
A for loop is then entered by unique year.
The MESO West and NASA POWER datasets are then checked to make sure that no months are missing for that year.
2002, 2008, and 2018 are skipped due to missing data.
Then the solar values are summed by month for the unique year in the for loop and the year is then graphed.
________________________________________________________________________________________________________________________


Alaska State Comparison




























