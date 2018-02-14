#!/usr/bin/env python3
"""
Command Line Interface for displaying next bus times for given bus stop
"""

# import from standard library
import os
import sys
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
            my_bus = [bus['lineName'], bus['towards'], bus['timeToStation'], bus['expectedArrival']]
            my_bus_list.append(my_bus)
    return my_bus_list


def print_buses(next_buses_eta, next_buses_time):
    fill = "x{: ^31}x".format("")
    for bus_eta, bus_time in zip(next_buses_eta, next_buses_time):
        if bus_eta < 1:
            print("\x1b[1;37;41m" + "x{: ^31}x".format("* due now *") + "\x1b[0m")
        else:
            printout = "{: ^3}mins @ {}".format(bus_eta, bus_time[11:16])
            print("\x1b[1;37;40m" + "x{: ^31}x"
                  .format(printout) + "\x1b[0m")
    print(fill)
    print(" {:x^31} ".format(""))


def print_header(which_bus):
    fill = "x{: ^31}x".format("")
    print(" {:x^31}".format(""))
    print(fill)
    print('x{: ^31}x\nx{: ^31}x\nx{: ^31}x'.format("next buses to", which_bus[0], which_bus[1]))
    print(fill)


def wait():
    refresh_time = 15
    while refresh_time > 0:
        print("\x1b[2;37;40m" + "{}".format(refresh_time) + "\x1b[0m")
        time.sleep(1)
        sys.stdout.write("\033[F")  # up one line
        sys.stdout.write("\033[K")  # clear line
        refresh_time -= 1


def screen_refresh(next_buses_time):
    lines_printed = len(next_buses_time) + 1
    while lines_printed > 0:  # Clear previous lines of printed times
        sys.stdout.write("\033[F")  # up one line
        sys.stdout.write("\033[K")  # clear line
        lines_printed -= 1
    time.sleep(1)
    sys.stdout.write("\033[F")  # up one line
    sys.stdout.write("\033[K")  # clear line


exceptions = (KeyboardInterrupt, OSError, requests.exceptions.Timeout,
              requests.exceptions.ConnectionError, requests.exceptions.HTTPError)

while True:
    try:
        os.system('cls' if os.name == 'nt' else 'clear')
        print_header(user.which_bus)
        while True:
            next_buses = sorted(get_bus_list(user.which_bus[0], user.which_bus[2]), key=lambda x: int(x[2]))
            next_buses_eta = [(int(bus[2] / 60)) for bus in next_buses]
            next_buses_time = [bus[3] for bus in next_buses]
            print_buses(next_buses_eta, next_buses_time)
            wait()
            screen_refresh(next_buses_time)
    except KeyboardInterrupt:
        sys.exit("\nKeyboard Interrupt: Exiting")
    except exceptions as err:
        print("\nERROR\n\n{}\n\nSleeping for 5 secs\n".format(err))
        try:
            time.sleep(5)
        except KeyboardInterrupt:
            sys.exit("\nKeyboard Interrupt: Exiting")
        continue
