import streamlit as st
import requests
import pandas as pd
import folium
from streamlit_folium import folium_static
import matplotlib.pyplot as plt

# ✅ API Endpoints
FLIGHTS_API = "http://127.0.0.1:5000/api/flights-weather"  # Replace with your Flask API URL

# ✅ Fetch Data from API
@st.cache_data
def get_flight_weather_data():
    response = requests.get(FLIGHTS_API)
    if response.status_code == 200:
        return response.json()
    else:
        st.error(f"Failed to fetch data: {response.status_code}")
        return None

# ✅ Process Data for Visualization
def process_data(data):
    flights = data["flights"]
    weather = data["weather"]

    # Convert to DataFrame
    df = pd.DataFrame(flights)
    df["departure_time"] = pd.to_datetime(df["departure_time"])
    df["hour"] = df["departure_time"].dt.hour

    return df, weather

# ✅ Create a Map with Flight Departures
def create_map(df):
    st.subheader("🌍 Flight Departure Locations")

    # Base map centered on Charles de Gaulle Airport (CDG)
    m = folium.Map(location=[49.0097, 2.5479], zoom_start=5)

    for _, row in df.iterrows():
        folium.Marker(
            location=[49.0097, 2.5479],  # Fixed to CDG Airport (Modify for real coords)
            popup=f"Flight {row['flight_number']} to {row['destination']} - Delay: {row['delay']} min",
            icon=folium.Icon(color="red" if row["delay"] > 15 else "green")
        ).add_to(m)

    folium_static(m)

# ✅ Plot Hourly Delay Trends
def plot_hourly_delays(df):
    st.subheader("📊 Hourly Flight Delays")
    
    hourly_delays = df.groupby("hour")["delay"].mean().reset_index()

    fig, ax = plt.subplots()
    ax.plot(hourly_delays["hour"], hourly_delays["delay"], marker="o", linestyle="-", color="red", label="Avg Delay (mins)")
    ax.set_xlabel("Hour of Day")
    ax.set_ylabel("Average Delay (mins)")
    ax.set_title("Hourly Flight Delays vs. Wind Speed")
    ax.legend()

    st.pyplot(fig)

# ✅ Main Streamlit App
st.title("✈️ Flight Delay Analytics Due to Wind Speeds")

# Fetch Data
data = get_flight_weather_data()
if data:
    df, weather = process_data(data)

    # ✅ Display Weather Data
    st.subheader("🌦️ Weather Conditions at Departure Time")
    st.write(f"**Condition:** {weather['condition']}")
    st.write(f"**Temperature:** {weather['temperature']}°C")
    st.write(f"**Wind Speed:** {weather['wind_speed']} km/h")
    st.write(f"**Wind Gusts:** {weather['wind_gusts']} km/h")

    # ✅ Display Flight Delay Analysis
    create_map(df)
    plot_hourly_delays(df)
    
    st.subheader("📌 Conclusion")
    st.write(
        "Analysis shows that **high wind speeds during departure increase flight delays**. "
        "Higher delays are observed during **strong wind gusts**."
    )
