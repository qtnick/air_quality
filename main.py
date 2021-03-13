import requests
import time
import sqlite3
from datetime import datetime
from pytz import timezone


conn = sqlite3.connect('air_quality.db')
c = conn.cursor()


def create_database():
    """Create database if doesn't exist."""
    c.execute("""CREATE TABLE IF NOT EXISTS air_quality (
                city text,
                pm25 real,
                pm10 real,
                time text
                )""")


def store_in_database(city, pm25, pm10, now_time):
    """Store values in database."""
    with conn:
        c.execute("INSERT INTO air_quality VALUES (:city, :pm25, :pm10, :now_time)", {'city': city, 'pm25': pm25, 'pm10': pm10, 'now_time': now_time})


def get_measurements(installation_id):
    """Get measurements from specified installation."""
    headers = {'Accept': 'application/json', 'apikey': 'GtIGUeKlILqJwMiGBTVKdEkIGM4hWEwc'}
    url = f'https://airapi.airly.eu/v2/measurements/installation?installationId={installation_id}'
    response = requests.get(url, headers=headers)
    r_dict = response.json()
    return r_dict


def get_pm25(installation_id):
    """Get PM25 measurements from specified installation."""
    measurements = get_measurements(installation_id)
    pm25 = measurements['current']['values'][1]['value']
    return pm25


def get_pm10(installation_id):
    """Get PM10 measurements from specified installation."""
    measurements = get_measurements(installation_id)
    pm10 = measurements['current']['values'][2]['value']
    return pm10


def get_city(installation_id):
    """"Get list of available installations."""
    headers = {'Accept': 'application/json', 'apikey': 'GtIGUeKlILqJwMiGBTVKdEkIGM4hWEwc'}
    url = f'https://airapi.airly.eu/v2/installations/{installation_id}'
    response = requests.get(url, headers=headers)
    installation = response.json()
    city = installation['address']['displayAddress1']
    return city


def get_current_time():
    current_time = datetime.now(timezone('Europe/Warsaw'))
    return current_time.strftime("%H:%M:%S %d-%m-%y")


def run_forever():
    print('\nCtrl+c to exit.\n')
    interval_in_sec = 1800
    installations = [9928, 37995, 13310]
    while True:
        create_database()
        try:
            for installation in installations:
                city = get_city(installation)
                pm25 = get_pm25(installation)
                pm10 = get_pm10(installation)
                now_time = get_current_time()

                store_in_database(city, pm25, pm10, now_time)
        except KeyboardInterrupt:
            print('\nInterrupted.')
            exit(0)

        time.sleep(interval_in_sec)


if __name__ == "__main__":
    run_forever()
