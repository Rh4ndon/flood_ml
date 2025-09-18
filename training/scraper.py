import requests
import datetime
import csv
import random

# --- CONFIG ---
API_KEY = "EYR6KGTLK9CVKS5CBGTJ8ATXJ"

# --- SELECT ONLY KEY PHILIPPINE CITIES (to limit API usage) ---
# Chosen based on: capital status, population, flood history
PHILIPPINE_CITIES = [
    "Cabanatuan City",          # Capital, low-lying, river systems, extreme flood risk
    "Palayan City",     # Largest population, Marikina River basin, frequent flooding
    "Bongabon"            # Major Mindanao hub, prone to flash floods during heavy rains
]

# --- Fetch Weather Data ---
def get_data(date, month, year, days, location):
    try:
        a = datetime.date(year, month, date)
        b = a - datetime.timedelta(days=days)
        
        url = (
            f"https://weather.visualcrossing.com/VisualCrossingWebServices/rest/services/weatherdata/history?"
            f"aggregateHours={24 * days}&"
            f"startDateTime={b}T00:00:00&"
            f"endDateTime={a}T00:00:00&"
            f"unitGroup=uk&contentType=json&"
            f"dayStartTime=0:0:00&dayEndTime=0:0:00&"
            f"location={location}&"
            f"key={API_KEY}"
        )
        
        response = requests.get(url)
        if response.status_code != 200:
            print(f"⚠️ HTTP {response.status_code} for {location}: {response.text}")
            return None

        data = response.json()
        if 'error' in data:
            print(f"⚠️ API Error for {location}: {data.get('message', data['error'])}")
            return None

        if 'locations' not in data:
            print(f"⚠️ No 'locations' in response for {location}")
            return None

        loc_key = next(iter(data['locations']))
        values = data['locations'][loc_key]['values']
        
        if not values:
            print(f"⚠️ No weather values for {location}")
            return None

        y = values[0]
        final = [
            y.get('temp', 0),
            y.get('maxt', 0),
            y.get('wspd', 0),
            y.get('cloudcover', 0),
            y.get('precip', 0),
            y.get('humidity', 0),
            y.get('precipcover', 0)
        ]
        return final

    except Exception as e:
        print(f"⚠️ Exception for {location}: {e}")
        return None


# --- Generate No-Flood Data (Label 0) ---
print("⏳ Generating no-flood data (label=0)...")
with open('data1.csv', mode='w', newline='', encoding='UTF-8') as f:
    writer = csv.writer(f)
    
    for city in PHILIPPINE_CITIES:
        for j in range(1, 6):      # Only 5 samples per city → 25 total API calls
            a = random.randint(1, 28)
            b = random.randint(1, 12)
            c = random.randint(2018, 2023)  # Updated to more recent years

            k = get_data(a, b, c, 15, city)
            
            if k and k[4] is not None and k[4] < 20:  # Precip < 20mm
                print(f"✅ No-flood sample from {city}: {k}")
                writer.writerow(k + [0])


# --- Helper: Extract Date from "9 June, 2020" format ---
def extract_date(date_str):
    parts = date_str.split(" ")
    day = int(parts[0])
    
    month_map = {
        'january': 1, 'february': 2, 'march': 3, 'april': 4,
        'may': 5, 'june': 6, 'july': 7, 'august': 8,
        'september': 9, 'october': 10, 'november': 11, 'december': 12
    }
    month_name = parts[1].rstrip(',').lower()
    month = month_map.get(month_name, 1)
    year = int(parts[2])
    return [day, month, year]


# --- Process Flood Events (Label 1) ---
# Map Indian locations to one of our 10 Philippine cities (randomly)
def process(row):
    selected_city = random.choice(PHILIPPINE_CITIES)
    print(f"🌍 Mapping '{row[0]}' → '{selected_city}' for demo")
    
    x = extract_date(row[1])
    return get_data(x[0], x[1], x[2], 15, selected_city)


print("\n⏳ Generating flood data (label=1)...")
with open('data.csv', mode='w', newline='', encoding='UTF-8') as f:
    writer = csv.writer(f)
    
    with open('mined.csv', mode='r', encoding='UTF-8') as csv_file:
        csv_reader = csv.reader(csv_file)
        for row in csv_reader:
            print(f"Processing: {row}")
            weather_data = process(row)
            if weather_data:
                writer.writerow(weather_data + [1])
            else:
                print(f"❌ Skipping {row} due to missing weather data")

print("\n✅ Done! Created:")
print("   - data.csv (flood events, label=1)")
print("   - data1.csv (no-flood samples, label=0)")
print(f"   - Used only {len(PHILIPPINE_CITIES)} cities to limit API usage.")