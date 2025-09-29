# FloodML – Flood Prediction for Nueva Ecija

FloodML is a machine learning-powered web application that predicts flood risk in **Palayan, Cabanatuan, and Bongabon**—three key municipalities in **Nueva Ecija, Philippines**, a province highly vulnerable to seasonal flooding due to its location in the Central Luzon plains and proximity to major river systems like the Pampanga River.

🔗 **Live Demo**: https://flood-ml-ca97.onrender.com/

---

## 🌧️ Why Focus on Nueva Ecija?

Nueva Ecija is the “Rice Granary of the Philippines,” but its flat terrain and monsoon-driven rainfall make it prone to severe flooding—especially in low-lying areas like **Cabanatuan**, the provincial capital **Palayan**, and the agricultural town of **Bongabon**. Heavy rains from typhoons or the southwest monsoon (Habagat) often cause rivers to overflow, damaging crops, infrastructure, and homes.

FloodML aims to provide **early, localized flood forecasts** for these communities using real-time weather data and historical patterns—helping residents, farmers, and local governments prepare and respond effectively.

---

## 🚀 Getting Started

To run FloodML locally for development:

```bash
# Clone the repo
git clone https://github.com/your-username/floodml.git
cd floodml

# Set up virtual environment
python -m venv venv
source venv/bin/activate  # Linux/macOS
# or venv\Scripts\activate  # Windows

# Install dependencies
pip install -r requirements.txt

# Run the app
python app.py
```

Visit `http://localhost:5000` in your browser.

---

## 🌐 What It Does

FloodML delivers **hyperlocal flood predictions** for Palayan, Cabanatuan, and Bongabon using real-time weather inputs:

- Precipitation
- Temperature & Max Temperature
- Humidity
- Wind Speed
- Cloud Cover

### Key Features:

#### 1. **Predict Page**

Enter any of the three cities, and FloodML:

- Fetches 15-day weather forecasts via the Visual Crossing API
- Runs the data through a trained **Random Forest Classifier**
- Returns a **flood risk score** (Low / Moderate / High)

#### 2. **Localized Visualizations**

- Interactive maps and charts focused **only on Nueva Ecija**
- Bubble plots showing predicted flood likelihood and potential impact across the three towns
- Historical context based on past flood events in the region

#### 3. **Actionable Insights**

Results are designed for **local decision-making**—whether you're a farmer in Bongabon, a barangay official in Cabanatuan, or a planner in Palayan.

---

## 🛠️ How We Built It

### Data

- Historical flood reports from **NDRRMC** and **PAGASA** for Nueva Ecija
- Weather data (2015–2024) for Palayan, Cabanatuan, and Bongabon via **Visual Crossing API**
- Population and geographic data from Philippine census records

### Model

- **Random Forest Classifier** (98.7% accuracy on test set)
- Trained on local weather-flood correlations
- Saved as a `pickle` file for fast inference

### Frontend & Hosting

- Built with **Flask**, **Plotly**, and **Bootstrap**
- Hosted on **Render** for global accessibility

---

## 🔮 What’s Next

We plan to **expand FloodML to monitor flood risk across the entire Philippines**—covering major cities, agricultural zones, and vulnerable coastal communities nationwide. This will require:

- Access to **real-time weather data for hundreds of locations**
- Increased API usage (currently limited by free-tier quotas)
- Enhanced infrastructure for scalable predictions

**With additional funding for weather API credits**, we can unlock **country-wide monitoring**, making FloodML a national early-warning tool for LGUs, disaster agencies, and communities.

Until then, we remain focused on delivering **accurate, life-saving forecasts** for the people of **Nueva Ecija**.

---

## 💡 Our Vision

FloodML isn’t just a model—it’s a tool for **resilience in the rice fields of Central Luzon**. By focusing on **Palayan, Cabanatuan, and Bongabon**, we aim to turn data into early warnings that protect livelihoods, crops, and lives in one of the Philippines’ most vital agricultural regions.

> 🌾 _“Ang una naming alaga ay ang bukid—ang FloodML ay para protektahan ito.”_  
> — The FloodML Team
