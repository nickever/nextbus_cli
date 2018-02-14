#!/usr/bin/env python3
"""
Command Line Interface for logging next bus times for given bus stop
"""

import sys
import csv
import time
import requests

# import from this project
import user

__author__ = "Nick Everett"
__version__ = "0.5.0"
__license__ = "GNU GPLv3"


def get_bus_list(destination_name, stop_no):
    stop_data = requests.get('https://api.tfl.gov.uk/StopPoint/' + stop_no + '/arrivals',
                             auth=(user.tfl_id, user.tfl_key)).json()
    my_bus_list = []
    for bus in stop_data:
        if bus['destinationName'] == destination_name:
            my_bus = [bus['lineName'], bus['destinationName'],
                      bus['vehicleId'],
                      round(bus['timeToStation']/60),
                      bus['expectedArrival'][11:16]]
            my_bus_list.append(my_bus)
    return my_bus_list


def update_csv(value):  # appends log file with time and temp value
    log_date = time.strftime("%Y-%m-%d", time.gmtime())
    log_time = time.strftime("%H:%M:%S", time.gmtime())
    with open("bus_log.csv", "a+", newline='') as f:
        writer = csv.writer(f)
        writer.writerow([log_date, log_time, value])
    print("CSV Updated: {}".format("{},{},{}\n".format(log_date, log_time, value)))


while True:
    exceptions = (OSError, requests.exceptions.Timeout,
                  requests.exceptions.ConnectionError,
                  requests.exceptions.HTTPError)
    try:
        data = get_bus_list(user.which_bus[0], user.which_bus[2])
        data_sorted = sorted(data, key=lambda x: int(x[3]))
        data_string = data_sorted
        update_csv(data_string)
        time.sleep(60)
    except KeyboardInterrupt:
        sys.exit("\nKeyboard Interrupt: Exiting")
    except exceptions as err:
        print("\nERROR\n\n{}\n\nSleeping for 1 mins\n".format(err))
        try:
            time.sleep(60)
        except KeyboardInterrupt:
            sys.exit("\nKeyboard Interrupt: Exiting")
        continue
