# Code to set positions for a "sun" and "moon" servo based on sunrise and sunet
# times for a given city. The code uses the OpenWeatherMap API to get the sunrise and sunset info

import requests
import serial
import time
from datetime import datetime, timedelta, timezone
import threading

serial_port = "/dev/cu.usbmodem101"

# Obtain the latitude and longitude of a given city using the API
def get_lat_long(city):
    url = f"https://api.openweathermap.org/geo/1.0/direct?q=${city}&limit=5&appid=9aab6fc5372a05a9b9579dee92514753"
    response = requests.get(url)
    data = response.json()
    latitude = data[0]['lat']
    longitude = data[0]['lon']
    return latitude, longitude
    
# get information about the sunrise and sunset times for a given latitude and longitude
def get_sunrise_sunset_zone_time(Lat, Lon, date):
    today_url = f"https://api.openweathermap.org/data/2.5/weather?lat={Lat}&lon={Lon}&appid=9aab6fc5372a05a9b9579dee92514753"
    utc_offset = -21600
    tomorrow = date + timedelta(days=1)
    tomorrow_url = f"https://api.openweathermap.org/data/2.5/weather?lat={Lat}&lon={Lon}&dt={int(tomorrow.timestamp())}&appid=9aab6fc5372a05a9b9579dee92514753"
    yesterday = date - timedelta(days=1)
    yesterday_url = f"https://api.openweathermap.org/data/2.5/weather?lat={Lat}&lon={Lon}&dt={int(yesterday.timestamp())}&appid=9aab6fc5372a05a9b9579dee92514753"
    today_response = requests.get(today_url)
    tomorrow_response = requests.get(tomorrow_url)
    yesterday_response = requests.get(yesterday_url)
    today_data = today_response.json()
    tomorrow_data = tomorrow_response.json()
    timezonee = today_data['timezone']
    tz = timezone(timedelta(seconds=timezonee))
    yesterday_data = yesterday_response.json()
    today_sunrise = today_data['sys']['sunrise'] + timezonee
    today_sunset = today_data['sys']['sunset']+ timezonee
    now_time = datetime.utcnow().timestamp() + utc_offset + timezonee
    
    tomorrow_sunrise = today_sunrise + timedelta(days=1).total_seconds()
    tomorrow_sunset = today_sunset + timedelta(days=1).total_seconds()
    tomorrow_time = tomorrow_data['dt']
    yesterday_sunrise = today_sunrise - timedelta(days=1).total_seconds()
    yesterday_sunset = today_sunset - timedelta(days=1).total_seconds()
    yesterday_time = yesterday_data['dt']
    return today_sunrise, today_sunset, timezonee, now_time, tomorrow_sunrise, tomorrow_sunset, tomorrow_time, yesterday_sunrise, yesterday_sunset, yesterday_time
    
# format the sunrise and sunset times to be more readable
def findSunsetSunrise(city):
    lat, long = get_lat_long(city)
    todsunrise, todsunset, zone, todtime, tomsunrise, tomsunset, tomtime, yessunrise, yessunset, yestime = get_sunrise_sunset_zone_time(lat, long, datetime.utcnow())
    formattodsunrise = format_sun_time(todsunrise, zone)
    formattodsunset = format_sun_time(todsunset, zone)
    formattodtime= (datetime.utcnow() + timedelta(seconds=zone)).strftime('%Y-%m-%d %H:%M:%S %Z')
    formattomsunrise = format_sun_time(tomsunrise, zone)
    formattomsunset = format_sun_time(tomsunset, zone)
    formattomtime = format_sun_time(tomtime, zone)
    formatyesunrise = format_sun_time(yessunrise, zone)
    formatyesunset = format_sun_time(yessunset, zone)
    formatyestime = format_sun_time(yestime, zone)
    return todsunrise, todsunset, todtime, formattodsunrise, formattodsunset, formattodtime, tomsunrise, tomsunset, tomtime, formattomsunrise, formattomsunset, formattomtime, yessunrise, yessunset, yestime, formatyesunrise, formatyesunset, formatyestime

    
# function for formatting unix timestamps to human readable time
def format_sun_time(unix_time, timezonee):
    localized_time = datetime.fromtimestamp(unix_time) + timedelta(seconds=timezonee) + timedelta(seconds=timezonee)
    return localized_time.strftime('%Y-%m-%d %H:%M:%S %Z')

# calculate the position of the servo motor based on the current time and the sunrise and sunset times for today, yesterday and tomorrow
def calculate_servo_position(current_time, todsunrise, todsunset, tomsunrise, tomsunset, yessunrise, yessunset, yestime):
    day = False
    if (current_time >= datetime.fromtimestamp(todsunrise)) and (current_time <= datetime.fromtimestamp(todsunset)):
        time_since_sunrise = current_time - datetime.fromtimestamp(todsunrise)
        time_till_sunrise = datetime.fromtimestamp(tomsunrise) - current_time
        time_since_sunset = datetime.fromtimestamp(yessunset) - current_time
        time_till_sunset = datetime.fromtimestamp(todsunset) - current_time
        day = True
        
    elif (current_time > datetime.fromtimestamp(todsunset)) and (current_time < datetime.fromtimestamp(tomsunrise)):
        time_since_sunset = current_time - datetime.fromtimestamp(todsunset)
        time_till_sunset = datetime.fromtimestamp(tomsunset) - current_time
        time_since_sunrise = datetime.fromtimestamp(todsunrise) - current_time
        time_till_sunrise = datetime.fromtimestamp(tomsunrise) - current_time
        day = False

    elif (current_time < datetime.fromtimestamp(todsunrise)) and (current_time > datetime.fromtimestamp(yessunset)):
        time_since_sunrise = datetime.fromtimestamp(yessunrise) - current_time
        time_till_sunrise = datetime.fromtimestamp(todsunrise) - current_time
        time_since_sunset = current_time - datetime.fromtimestamp(yessunset)
        time_till_sunset = datetime.fromtimestamp(tomsunset) - current_time
        day = False
           
    day_length = todsunset - todsunrise
    night_length = tomsunrise - todsunset

    if time_since_sunrise.total_seconds() >= 0 and time_since_sunset.total_seconds() < 0:
        # sun servo position for sunrise to sunset
        sun_position = 180 - ((time_since_sunrise.total_seconds() / day_length) * 180)
    else:
        # Sun is below the horizon after sunset, reset position to 180
        sun_position = 180
    
    if time_since_sunset.total_seconds() >= 0 and time_since_sunrise.total_seconds() < 0:
        # moon servo position for sunset to sunrise
        moon_position = ((time_since_sunset.total_seconds() / night_length) * 180)
    else:
        # Moon is below the horizon after sunrise, reset position to 180
        moon_position = 0
    
    # Ensure servo position is within the valid range (0 to 180)
    return min(max(0, sun_position), 180), min(max(0, moon_position), 180)

# make the task run in a thread, so that the clock can be updated even if waiting for user input
def thread_task(city, ser):
    while True:
        if city[0] == "exit":
            break
        todsunrise, todsunset, todtime, formattodrise, formattodset, formattodtime, tomsunrise, tomsunset, tomtime, formattomrise, formattomset, formattomtime, yessunrise, yessunset, yestime, formatyesrise, formatyesset, formatyestime = findSunsetSunrise(city)
        currentstamp = datetime.fromtimestamp(todtime)
        sunpos, moonpos = calculate_servo_position(currentstamp, todsunrise, todsunset, tomsunrise, tomsunset, yessunrise, yessunset, yestime)
        ser.write(f"{sunpos},{moonpos}\n".encode())
        threading.Event().wait(10)  # Wait for one minute before updating again
    
def main():
    city = [None]
    ser = serial.Serial(serial_port, 9600, timeout=1)
    time.sleep(2)
    city[0] = input("Enter city or exit to quit: ")
    background_thread = threading.Thread(target=thread_task, args=(city, ser))
    background_thread.daemon = True
    background_thread.start()
    while city[0] != "exit":
        time.sleep(10)
        city[0] = input("Enter city or exit to quit: ")
        
    ser.write("180,0\n".encode())

    ser.close()
    
main()