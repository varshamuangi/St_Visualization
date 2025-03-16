from flask import Flask, jsonify
import pandas as pd

# Load dataset
DATASET_PATH = "flight_delay_space_weather_extended.csv"
df = pd.read_csv(DATASET_PATH)

# Initialize Flask App
app = Flask(__name__)

@app.route("/fetch_flight_data", methods=["GET"])
def fetch_flight_data():
    """Fetch all flight delay data"""
    return jsonify(df.to_dict(orient="records"))

@app.route("/fetch_space_weather", methods=["GET"])
def fetch_space_weather():
    """Fetch space weather summary (Kp Index & Solar Flare Intensity)"""
    space_weather_summary = {
        "average_kp_index": round(df["geomagnetic_kp_index"].mean(), 1),
        "max_kp_index": df["geomagnetic_kp_index"].max(),
        "solar_flare_intensity": df["solar_flare_intensity"].mode()[0]
    }
    return jsonify(space_weather_summary)

if __name__ == "__main__":
    app.run(debug=True, port=5000)
