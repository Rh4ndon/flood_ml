"""Philippine Weather Prediction Web app."""
import flask
from flask import Flask, render_template, request
import pickle
import base64
from training import prediction
import requests
import folium
from folium.plugins import HeatMap
import pandas as pd

app = Flask(__name__)

# Philippine cities data
data = [{'name':'Manila', "sel": "selected"}, {'name':'Cebu City', "sel": ""}, {'name':'Davao City', "sel": ""}, {'name':'Quezon City', "sel": ""}, {'name':'Makati', "sel": ""}]

# Philippine months - focusing on key weather seasons
months = [{"name":"January", "sel": ""}, {"name":"March", "sel": ""}, {"name":"May", "sel": ""}, {"name":"July", "sel": "selected"}, {"name":"September", "sel": ""}, {"name":"November", "sel": ""}]

# Philippine cities with major urban centers
cities = [
    {'name':'Manila', "sel": "selected"}, 
    {'name':'Quezon City', "sel": ""}, 
    {'name':'Makati', "sel": ""}, 
    {'name':'Cebu City', "sel": ""}, 
    {'name':'Davao City', "sel": ""}, 
    {'name':'Iloilo City', "sel": ""}, 
    {'name':'Cagayan de Oro', "sel": ""}, 
    {'name':'Zamboanga City', "sel": ""}, 
    {'name':'Baguio', "sel": ""}, 
    {'name':'Tuguegarao', "sel": ""}, 
    {'name':'Antipolo', "sel": ""}
]

try:
    model = pickle.load(open("model.pickle", 'rb'))
except (ValueError, TypeError) as e:
    print(f"Error loading model: {e}")
    from sklearn.tree import DecisionTreeClassifier
    model = DecisionTreeClassifier()  # Fallback placeholder

@app.route("/")
@app.route('/index.html')
def index() -> str:
    return render_template("index.html")


@app.route('/predicts.html')
def predicts():
    return render_template('predicts.html', cities=cities, cityname="Weather information for Philippine cities")

@app.route('/predicts.html', methods=["GET", "POST"])
def get_predicts():
    try:
        cityname = request.form["city"]
        
        cities_updated = [
            {'name': city['name'], "sel": "selected" if city['name'] == cityname else ""}
            for city in cities
        ]
        
        print(f"Processing weather data for: {cityname}")
        
        # ✅ Use OpenStreetMap Nominatim (FREE, no credit card needed)
        URL = "https://nominatim.openstreetmap.org/search"
        params = {
            'q': f"{cityname}, Philippines",
            'format': 'json',
            'limit': 1
        }
        headers = {
            'User-Agent': 'PhilippineFloodPredictionApp/1.0'
        }
        
        response = requests.get(URL, params=params, headers=headers)
        
        if response.status_code != 200:
            raise Exception(f"Geocoding API error: {response.status_code}")
            
        data_response = response.json()
        
        if not data_response:
            raise ValueError(f"No location found for '{cityname}, Philippines'")
        
        latitude = float(data_response[0]['lat'])
        longitude = float(data_response[0]['lon'])
        
        # Get weather prediction data
        final = prediction.get_data(latitude, longitude)
        final[4] *= 25  # Adjust for Philippine tropical climate
        
        # Prediction
        prediction_result = model.predict([final])[0]
        if str(prediction_result) == "0":
            pred = "Maganda ang panahon"  # Good weather
            pred_en = "Good Weather"
        else:
            pred = "Masamang panahon"     # Bad weather
            pred_en = "Adverse Weather"
        
        return render_template('predicts.html', 
                             cityname=f"Weather information for {cityname}", 
                             cities=cities_updated, 
                             temp=round(final[0], 2), 
                             maxt=round(final[1], 2), 
                             wspd=round(final[2], 2), 
                             cloudcover=round(final[3], 2), 
                             percip=round(final[4], 2), 
                             humidity=round(final[5], 2), 
                             pred=pred_en,
                             pred_fil=pred)
    
    except Exception as e:
        print(f"❌ Error processing {cityname}: {e}")
        return render_template('predicts.html', 
                             cities=cities, 
                             cityname="Hindi makuha ang data para sa lungsod na ito (Unable to retrieve data for this city.)")
        

@app.route('/map.html')
def weather_map():
    # Load location data (City, Lat, Lon, Temp, Class)
    df = pd.read_csv('final_plot.csv', header=None)
    df.columns = ['City', 'Latitude', 'Longitude', 'Temperature', 'Class']  # Now matches 5 columns

    # Create a base map
    m = folium.Map(location=[15.55, 121.15], zoom_start=10)

    # Create Feature Groups
    fg_markers = folium.FeatureGroup(name='Flood Risk Prediction (Markers)', show=True)
    fg_heatmap = folium.FeatureGroup(name='Precipitation Heatmap (mm)', show=False)

    for idx, row in df.iterrows():
        try:
            # Get full weather data for this location
            full_weather = prediction.get_data(row['Latitude'], row['Longitude'])
            full_weather[4] *= 25  # Adjust precip for Philippine context

            # Get flood risk prediction from your model
            prediction_result = model.predict([full_weather])[0]
            flood_risk = "High Risk" if prediction_result == 1 else "Low Risk"
            color = 'red' if prediction_result == 1 else 'green'

            # Prepare popup with real data
            popup_text = f"""
            <b>{row['City']}</b><br>
            Temp: {full_weather[0]:.1f}°C<br>
            Precip: {full_weather[4]:.1f} mm<br>
            Flood Risk: <b style='color:{color}'>{flood_risk}</b>
            """

            # Add marker
            icon = folium.Icon(color=color, icon='exclamation-triangle', prefix='fa')
            folium.Marker(
                location=[row['Latitude'], row['Longitude']],
                popup=popup_text,
                icon=icon
            ).add_to(fg_markers)

            # Add to heatmap (use actual precipitation)
            fg_heatmap.add_child(
                folium.CircleMarker(
                    location=[row['Latitude'], row['Longitude']],
                    radius=full_weather[4] / 10,  # Scale radius by precip
                    color='blue',
                    fill=True,
                    fill_color='blue',
                    fill_opacity=0.2,
                    popup=f"Precip: {full_weather[4]:.1f} mm"
                )
            )

        except Exception as e:
            print(f"Error processing {row['City']}: {e}")
            continue

    # Add heatmap layer using actual precipitation values
    heat_data = []
    for idx, row in df.iterrows():
        try:
            full_weather = prediction.get_data(row['Latitude'], row['Longitude'])
            full_weather[4] *= 25
            heat_data.append([row['Latitude'], row['Longitude'], full_weather[4]])
        except:
            continue

    if heat_data:
        HeatMap(
            heat_data,
            radius=25,
            blur=15,
            max_zoom=1,
            gradient={0.4: 'blue', 0.65: 'lime', 1: 'red'}
        ).add_to(fg_heatmap)

    # Add layers to map
    fg_markers.add_to(m)
    fg_heatmap.add_to(m)
    folium.LayerControl().add_to(m)

    map_html = m._repr_html_()
    return render_template('map.html', map_html=map_html)

if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0', port=5000)