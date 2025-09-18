import csv
import datetime
import pickle
import requests

def get_data(lat, lon):
    k = "https://weather.visualcrossing.com/VisualCrossingWebServices/rest/services/weatherdata/forecast?locations=" + str(lat) + "%2C%20" + str(lon) + "&aggregateHours=24&unitGroup=metric&shortColumnNames=false&contentType=json&key=Q6JH8Y4DVMP94X2D8LK7YX4HY"
    response = requests.get(k)
    if response.status_code != 200:
        print("API Error:", response.status_code, response.text)
        return [0]*6

    data = response.json()
    x = data['locations']
    for i in x:
        y = x[i]['values']

    print("=== DEBUG: Raw daily values from API ===")
    for idx, day in enumerate(y):
        print(f"Day {idx+1}: Temp={day['temp']}, Precip={day['precip']}, Humidity={day['humidity']}, Cloud={day['cloudcover']}")

    final = [0, 0, 0, 0, 0, 0]

    for j in y:
        final[0] += j['temp']
        if j['maxt'] > final[1]:
            final[1] = j['maxt']
        final[2] += j['wspd']
        final[3] += j['cloudcover']
        final[4] += j['precip']        # 🚫 DO NOT DIVIDE THIS
        final[5] += j['humidity']

    final[0] /= 15  # avg temp
    final[2] /= 15  # avg wind
    final[3] /= 15  # avg cloud
    final[5] /= 15  # avg humidity

    final[3] = min(100, final[3])  # Cap cloud
    final[5] = min(100, final[5])  # Cap humidity

    print("=== DEBUG: Final processed values ===")
    print(f"Total Precipitation: {final[4]} mm")
    print(f"Avg Temp: {final[0]:.2f}°C")
    print(f"Max Temp: {final[1]:.2f}°C")
    print(f"Avg Wind: {final[2]:.2f} km/h")
    print(f"Avg Cloud: {final[3]:.2f}%")
    print(f"Avg Humidity: {final[5]:.2f}%")

    return final

def testConnection():
    return "yo"



get_data(15.6321,121.144)