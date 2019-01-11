import urllib
import csv
import requests
import time


'''
The job of this script is to get the GHI values from nasa for a given latitude, longitude
and time frame

The main intention for this script is to allow a real time comparision of the nasa power data
set to a weather station that we have setup

This will usually mean that the value that is to be entered for the end of the time frame will 
be the current year-month-day 
'''


def get_the_csv_url(lat, lon, start_time, end_time):

    url = "https://power.larc.nasa.gov/cgi-bin/v1/DataAccess.py" \
          "?request=execute&identifier=SinglePoint&parameters=ALLSKY_SFC_SW_DWN&startDate=" + str(start_time) \
          + "&endDate=" + str(end_time) + \
          "&userCommunity=SSE&tempAverage=DAILY&outputList=JSON,CSV&lat=" + str(lat) + \
          "&lon=" + str(lon) + "&user=anonymous"
    csv_url = ""
    with requests.Session() as s:
        download = s.get(url)
        decoded_content = download.content.decode('utf-8')
        cr = csv.reader(decoded_content.splitlines(), delimiter=',')
        my_list = list(cr)
        print(my_list)  # Error checker in case there is a problem with the NASA POWER API
        for row in my_list:
            if "\"csv\":" in row[0]:
                temp = row[0].split("\"")
                csv_url = temp[3]

    return csv_url


def output_new_nasa_csv_file(new_filename, csv_url):
    response = urllib.request.urlopen(csv_url)
    html = response.read()
    with open(new_filename, 'wb') as f:
        f.write(html)


'''
Single station download. Kept for reference

lat = 64.835365
lon = -147.776749
start = 20050329
# end = time.strftime("%Y%m%d")
end = 20181120
csv_url = get_the_csv_url(lat, lon, start, end)
output_new_nasa_csv_file("Fairbanks Nasa.csv", csv_url)
'''

