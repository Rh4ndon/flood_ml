import csv
import datetime
import pickle
import requests

def get_data(lat, lon):
    url = f"https://weather.visualcrossing.com/VisualCrossingWebServices/rest/services/weatherdata/forecast?locations={lat}%2C%20{lon}&aggregateHours=24&unitGroup=metric&shortColumnNames=false&contentType=json&key=Q6JH8Y4DVMP94X2D8LK7YX4HY"
    response = requests.get(url)
    if response.status_code != 200:
        return [0] * 6

    data = response.json()
    location_data = next(iter(data['locations'].values()))
    daily_values = location_data['values']

    final = [0, 0, 0, 0, 0, 0]

    for day in daily_values:
        final[0] += day['temp']
        if day['maxt'] > final[1]:
            final[1] = day['maxt']
        final[2] += day['wspd']
        final[3] += day['cloudcover']
        final[4] += day['precip']        # 🚫 DO NOT DIVIDE THIS
        final[5] += day['humidity']

    final[0] /= 15  # avg temp
    final[2] /= 15  # avg wind
    final[3] /= 15  # avg cloud
    final[5] /= 15  # avg humidity

    final[3] = min(100, final[3])  # Cap cloud
    final[5] = min(100, final[5])  # Cap humidity

    return final

def testConnection():
    return "yo"