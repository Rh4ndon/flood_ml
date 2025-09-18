"""Philippine Weather Prediction Web app — Focused on Bongabon, Palayan, Cabanatuan."""
import flask
from flask import Flask, render_template, request
import pickle
import base64
from training import prediction  # Make sure this points to your fixed get_data()
import requests
import folium
from folium.plugins import HeatMap
import pandas as pd

app = Flask(__name__)

# Focus only on 3 target cities
cities = [
    {'name': 'Bongabon', "sel": "selected"},
    {'name': 'Palayan City', "sel": ""},
    {'name': 'Cabanatuan City', "sel": ""}
]

try:
    model = pickle.load(open("model.pickle", 'rb'))
except (ValueError, TypeError, FileNotFoundError) as e:
    print(f"⚠️ Model load error (using fallback): {e}")
    from sklearn.tree import DecisionTreeClassifier
    model = DecisionTreeClassifier()  # Fallback for dev only


@app.route("/")
@app.route('/index.html')
def index() -> str:
    return render_template("index.html")


@app.route('/predicts.html', methods=["GET"])
def predicts():
    return render_template('predicts.html', cities=cities, cityname="Check flood risk for Bongabon, Palayan, or Cabanatuan")


@app.route('/predicts.html', methods=["POST"])
def get_predicts():
    try:
        cityname = request.form["city"].strip()
        
        # Update selected city in dropdown
        cities_updated = [
            {'name': city['name'], "sel": "selected" if city['name'] == cityname else ""}
            for city in cities
        ]
        
        print(f"📍 Processing weather data for: {cityname}")
        
        # ✅ Fixed: Removed trailing space in URL
        URL = "https://nominatim.openstreetmap.org/search"
        params = {
            'q': f"{cityname}, Philippines",
            'format': 'json',
            'limit': 1
        }
        headers = {
            'User-Agent': 'PhilippineFloodPredictionApp/1.0'
        }
        
        response = requests.get(URL, params=params, headers=headers, timeout=10)
        
        if response.status_code != 200:
            raise Exception(f"Geocoding failed: HTTP {response.status_code}")
            
        data_response = response.json()
        
        if not data_response:
            raise ValueError(f"No location found for '{cityname}, Philippines'")
        
        latitude = float(data_response[0]['lat'])
        longitude = float(data_response[0]['lon'])
        print(f"🌍 Coordinates: {latitude}, {longitude}")
        
        # ✅ Get REAL weather data — NO artificial scaling
        final = prediction.get_data(latitude, longitude)
        # 🚫 REMOVED: final[4] *= 25  ← This caused 16,000mm error!

        # Get prediction
        prediction_result = model.predict([final])[0]
        if str(prediction_result) == "0":
            pred = "Maganda ang panahon"
            pred_en = "Good Weather"
        else:
            pred = "Masamang panahon"
            pred_en = "Adverse Weather"
        
        # ✅ Pass values AS-IS — they’re already realistic
        return render_template('predicts.html', 
                             cityname=f"Weather information for {cityname}", 
                             cities=cities_updated, 
                             temp=round(final[0], 2), 
                             maxt=round(final[1], 2), 
                             wspd=round(final[2], 2), 
                             cloudcover=min(100, round(final[3], 2)),  # Cap at 100
                             percip=round(final[4], 2),  # Total over 15 days — REALISTIC
                             humidity=min(100, round(final[5], 2)),  # Cap at 100
                             pred=pred_en,
                             pred_fil=pred)
    
    except Exception as e:
        error_msg = f"❌ Error: {str(e)}"
        print(error_msg)
        return render_template('predicts.html', 
                             cities=cities, 
                             cityname="Hindi makuha ang data para sa lungsod na ito. Subukang muli.")


@app.route('/map.html')
def weather_map():
    # Load your 3 focus locations (ensure final_plot.csv has Bongabon, Palayan, Cabanatuan)
    try:
        df = pd.read_csv('final_plot.csv', header=None)
        df.columns = ['City', 'Latitude', 'Longitude', 'Temperature', 'Class']
    except Exception as e:
        print(f"⚠️ CSV load error: {e}")
        # Fallback: create minimal dataset
        df = pd.DataFrame([
            ['Bongabon', 15.6050, 121.1950, 27.5, 0],
            ['Palayan City', 15.4917, 121.1350, 27.8, 1],
            ['Cabanatuan City', 15.4887, 120.9855, 28.1, 1]
        ], columns=['City', 'Latitude', 'Longitude', 'Temperature', 'Class'])

    # ✅ Center map on Nueva Ecija
    m = folium.Map(location=[15.53, 121.10], zoom_start=10)

    fg_markers = folium.FeatureGroup(name='Flood Risk Prediction (Markers)', show=True)
    fg_heatmap = folium.FeatureGroup(name='Precipitation Heatmap (mm)', show=False)

    for idx, row in df.iterrows():
        try:
            full_weather = prediction.get_data(row['Latitude'], row['Longitude'])
            # 🚫 NO MORE: full_weather[4] *= 25

            prediction_result = model.predict([full_weather])[0]
            flood_risk = "High Risk" if prediction_result == 1 else "Low Risk"
            color = 'red' if prediction_result == 1 else 'green'

            popup_text = f"""
            <b>{row['City']}</b><br>
            Temp: {full_weather[0]:.1f}°C<br>
            Precip: {full_weather[4]:.1f} mm<br>
            Wind: {full_weather[2]:.1f} km/h<br>
            Flood Risk: <b style='color:{color}'>{flood_risk}</b>
            """

            icon = folium.Icon(color=color, icon='exclamation-triangle', prefix='fa')
            folium.Marker(
                location=[row['Latitude'], row['Longitude']],
                popup=popup_text,
                icon=icon
            ).add_to(fg_markers)

            # Add to heatmap (real precip values)
            fg_heatmap.add_child(
                folium.CircleMarker(
                    location=[row['Latitude'], row['Longitude']],
                    radius=max(5, min(30, full_weather[4] / 5)),  # Scale 0-150mm → radius 5-30
                    color='blue',
                    fill=True,
                    fill_color='blue',
                    fill_opacity=0.3,
                    popup=f"Precip: {full_weather[4]:.1f} mm"
                )
            )

        except Exception as e:
            print(f"Error processing {row['City']}: {e}")
            continue

    # Build heatmap with real data
    heat_data = []
    for idx, row in df.iterrows():
        try:
            full_weather = prediction.get_data(row['Latitude'], row['Longitude'])
            heat_data.append([row['Latitude'], row['Longitude'], full_weather[4]])  # Real mm
        except:
            continue

    if heat_data:
        HeatMap(
            heat_data,
            radius=25,
            blur=15,
            max_zoom=1,
            gradient={0.3: 'blue', 0.6: 'lime', 1: 'red'}  # Blue=low, Red=high precip
        ).add_to(fg_heatmap)

    fg_markers.add_to(m)
    fg_heatmap.add_to(m)
    folium.LayerControl().add_to(m)

    map_html = m._repr_html_()
    return render_template('map.html', map_html=map_html)


if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0', port=5000)