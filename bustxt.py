#!/usr/bin/env python3
"""
Command Line Interface that sends a text to a given number listing
the next bus times for given bus stop
"""

import sys
import time
import requests
import schedule
import twilio.rest

# import from this project
import user


def get_forecast():
    try:
        forecast_data = requests.get('https://api.tfl.gov.uk/airquality',
                                     auth=(user.tfl_id, user.tfl_key)
                                     ).json()['currentForecast']
        for x in forecast_data:
            if x['forecastType'] == "Current":
                forecast_today = {"Band": x['forecastBand'],
                                  "n02": x['nO2Band'],
                                  "pM10": x['pM10Band'],
                                  "pM25": x['pM25Band'],
                                  "Summary": x['forecastText'].split("&")[0]}
                return forecast_today
            else:
                return None
    except ConnectionError:
        return None


def get_bus_list(destination_name, stop_no):
    stop_data = requests.get('https://api.tfl.gov.uk/StopPoint/' + stop_no + '/arrivals',
                             auth=(user.tfl_id, user.tfl_key)).json()
    my_bus_list = []
    for bus in stop_data:
        if bus['destinationName'] == destination_name:
            my_bus = [bus['lineName'], bus['destinationName'], bus['timeToStation']-180, bus['expectedArrival']]
            my_bus_list.append(my_bus)
    return my_bus_list


def sort_buses(my_bus_list):
    next_buses = sorted(my_bus_list, key=lambda x: int(x[2]))
    if len(next_buses) > 3:
        next_buses = next_buses[:3]
    next_buses_eta = [(int(bus[2] / 60)) for bus in next_buses]
    next_buses_time = [bus[3] for bus in next_buses]
    return next_buses, next_buses_eta, next_buses_time


def text_string(next_buses, which_buses, forecast):
    next_buses_sorted = []
    next_buses_eta = []
    next_buses_time = []
    bus_string = "\nNext buses"
    if forecast is not None:
        forecast_string = forecast['Summary']
    else:
        forecast_string = "No forecast today"
    for i in range(len(which_buses)):
        x = sort_buses(next_buses[i])
        next_buses_sorted.append(x[0])
        next_buses_eta.append(x[1])
        next_buses_time.append(x[2])
        bus_string += "\n\n{} to {}:".format(which_buses[i][1], which_buses[i][0])
        for bus_eta, bus_time in zip(next_buses_eta[i], next_buses_time[i]):
            if 0 < bus_eta <= 1:
                bus_string += "\n* due now *"
            elif bus_eta > 1:
                bus_string += "\n{: >2} mins at {}".format(bus_eta, bus_time[11:16])
            else:
                pass
    return bus_string, forecast_string


def text_next_buses(bus_string, forecast_string, phone_numbers):
    sent_time = time.strftime("%H:%M:%S", time.gmtime())
    for num in phone_numbers:
        client = twilio.rest.Client(user.twilio_sid, user.twilio_auth_token)
        message = client.messages.create(
            to=phone_numbers[num],
            from=user.twilio_number,
            body="Morning {}!\n{}\n\n{}".format(num, bus_string, forecast_string))
        print("\nMessage Sent to {} on {} at {}:\n{}\n\n{}".format(num, phone_numbers[num], sent_time,
                                                                   bus_string, forecast_string))
        print("\n")


def shell():
    try:
        forecast = get_forecast()
        next_buses = []
        for bus in user.which_bus:
            next_buses.append(get_bus_list(bus[0], bus[2]))
        bus_string, forecast_string = text_string(next_buses, user.which_bus, forecast)
        text_next_buses(bus_string, forecast_string, user.phone_numbers)
        print("\nThe next text will be sent at {} on {}".format(schedule.next_run().strftime("%H:%M:%S"),
                                                                schedule.next_run().strftime("%d-%m-%Y")))
    except KeyboardInterrupt:
        sys.exit("Keyboard Interrupt. Exiting...")


if __name__ == "__main__":
    schedule.every().monday.at("07:40").do(shell)
    schedule.every().tuesday.at("07:40").do(shell)
    schedule.every().wednesday.at("07:40").do(shell)
    schedule.every().thursday.at("07:40").do(shell)
    schedule.every().friday.at("07:40").do(shell)
    print("\nThe next text will be sent at {} on {}".format(schedule.next_run().strftime("%H:%M:%S"),
                                                            schedule.next_run().strftime("%d-%m-%Y")))
    while True:
        schedule.run_pending()
        time.sleep(1)
