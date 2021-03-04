import requests
import json
import time
import sqlite3


conn = sqlite3.connect('air_quality.db')
c = conn.cursor()


def create_database():
    """Create database if doesn't exist."""
    c.execute("""CREATE TABLE IF NOT EXISTS air_quality (
                city text,
                pm25 real
                )""")


def store_in_database(city, pm25):
    """Store values in database."""
    with conn:
        c.execute("INSERT INTO air_quality VALUES (:city, :pm25)", {'city': city, 'pm25': pm25})


def get_measurements(installation_id):
    """Get measurements from specified installation."""
    headers = {'Accept': 'application/json', 'apikey': 'GtIGUeKlILqJwMiGBTVKdEkIGM4hWEwc'}
    url = f'https://airapi.airly.eu/v2/measurements/installation?installationId={installation_id}'
    response = requests.get(url, headers=headers)
    r_dict = response.json()
    filename = 'data_airly.json'

    with open(filename, 'w') as f:
        json.dump(r_dict, f)
    # percentage_of_pollution = r_dict['current']['standards'][0]['percent']
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


def run_forever():
    print('\nCtrl+c to exit.\n')
    interval_in_sec = 10
    installations = [7523, 9902, 6891, 10010]
    while True:
        create_database()
        for installation in installations:
            city = get_city(installation)
            pm25 = get_pm25(installation)
            try:
                store_in_database(city, pm25)
                time.sleep(interval_in_sec)
            except KeyboardInterrupt:
                print('\nInterrupted.')
                exit(0)


if __name__ == "__main__":
    run_forever()
