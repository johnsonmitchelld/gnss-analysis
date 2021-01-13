import pandas as pd
import csv
import math
from datetime import datetime
import os


def nmea_to_csv(nmea_data, filename):

    # open the output file in write mode
    with open(filename, 'wt') as output_file:

        # create a csv reader object from the input file (nmea files are basically csv)

        # create a csv writer object for the output file
        writer = csv.writer(output_file, delimiter=',', lineterminator='\n')

        # write the header line to the csv file
        writer.writerow(['date_and_time', 'lat', 'lon', 'speed'])

        # iterate over all the rows in the nmea file
        for row in nmea_data:

            # skip all lines that do not start with $GPRMC
            if row[0].startswith('$GNRMC'):
                # for each row, fetch the values from the row's columns
                # columns that are not used contain technical GPS stuff that you are probably not interested in
                time = row[1]
                warning = row[2]
                lat = row[3]
                lat_direction = row[4]
                lon = row[5]
                lon_direction = row[6]
                speed = row[7]
                date = row[9]

                # if the "warning" value is "V" (void), you may want to skip it since this is an indicator for an incomplete data row)
                if warning == 'V':
                    continue

                # merge the time and date columns into one Python datetime object (usually more convenient than having both separately)
                date_and_time = datetime.strptime(
                    date + ' ' + time, '%d%m%y %H%M%S.%f')

                # convert the Python datetime into your preferred string format, see http://www.tutorialspoint.com/python/time_strftime.htm for futher possibilities
                # [:-3] cuts off the last three characters (trailing zeros from the fractional seconds)
                date_and_time = date_and_time.strftime(
                    '%y-%m-%d %H:%M:%S.%f')[:-3]

                # lat and lon values in the $GPRMC nmea sentences come in an rather uncommon format. for convenience, convert them into the commonly used decimal degree format which most applications can read.
                # the "high level" formula for conversion is: DDMM.MMMMM => DD + (YY.ZZZZ / 60), multiplicated with (-1) if direction is either South or West
                # the following reflects this formula in mathematical terms.
                # lat and lon have to be converted from string to float in order to do calculations with them.
                # you probably want the values rounded to 6 digits after the point for better readability.
                lat = round(math.floor(float(lat) / 100) +
                            (float(lat) % 100) / 60, 6)
                if lat_direction == 'S':
                    lat = lat * -1

                lon = round(math.floor(float(lon) / 100) +
                            (float(lon) % 100) / 60, 6)
                if lon_direction == 'W':
                    lon = lon * -1

                # speed is given in knots, you'll probably rather want it in km/h and rounded to full integer values.
                # speed has to be converted from string to float first in order to do calculations with it.
                # conversion to int is to get rid of the tailing ".0".
                speed = float(speed) * 1.15078

                # write the calculated/formatted values of the row that we just read into the csv file
                writer.writerow([date_and_time, lat, lon, speed])


def parse_log_file(filepath):
    filepath = os.path.split(filepath)
    input_directory = filepath[0]
    input_filename = filepath[1]
    input_filename_noext = os.path.splitext(input_filename)[0]
    with open(os.path.join(input_directory, input_filename)) as csvfile:
        reader = csv.reader(csvfile)
        data = {'NMEA': []}
        for row in reader:
            if row[0][0] == '#':
                if 'Version' in row[0] or 'Header' in row[0] or len(row[0]) == 2:
                    pass
                elif len(row[0]) > 1:
                    data[row[0][2:]] = [row[1:]]
            else:
                data[row[0]].append(row[1:])


    nmea_data = data.pop('NMEA')

    output_directory = os.path.join(input_directory, input_filename_noext)
    os.mkdir(output_directory)


    for key, values in data.items():
        data[key] = pd.DataFrame(values[1:], columns=values[0])
        data[key].to_csv(os.path.join(output_directory, key + '.csv'), index=False)

    nmea_to_csv(nmea_data, os.path.join(output_directory,
                                        'NMEA.csv'))

if __name__ == '__main__':
    input_filepath ='/home/johnsonmitchelld/dev/pynav/data/personal/gnss_log_2020_12_14_17_52_46.txt'
    parse_log_file(input_filepath)

