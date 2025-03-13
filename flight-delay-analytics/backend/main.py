from flask import Flask, jsonify
import requests
import logging

# ✅ Configure Logger
logger = logging.getLogger("werkzeug")
logger.setLevel(logging.DEBUG)

# ✅ Ensure log messages appear in console
console_handler = logging.StreamHandler()
console_handler.setLevel(logging.DEBUG)
formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
console_handler.setFormatter(formatter)
logger.addHandler(console_handler)

# ✅ Initialize Flask
app = Flask(__name__)

# API Keys
FLIGHT_API_KEY = "c70ce30c1b8ed102a5979b9031e4ab3c"
WEATHER_API_KEY = "04d6010fd3f5450a95873756251303"

# ✅ Fetch flight data
def fetch_flight_data():
    logger.info("📡 Fetching flight data from AviationStack API...")
    url = f"https://api.aviationstack.com/v1/flights?access_key={FLIGHT_API_KEY}&dep_iata=CDG"
    
    response = requests.get(url)
    
    if response.status_code != 200:
        logger.error(f"❌ Flight API Error: {response.text}")
        return {"error": "Failed to fetch flight data"}
    
    flights = response.json().get("data", [])
    
    if not flights:
        logger.warning("⚠ No flights found.")
        return []
    
    logger.info(f"✅ {len(flights)} flights retrieved.")
    
    return [
        {
            "flight_number": flight.get("flight", {}).get("iata", "N/A"),
            "airline": flight.get("airline", {}).get("name", "Unknown"),
            "status": flight.get("flight_status", "Unknown"),
            "departure_time": flight.get("departure", {}).get("estimated", "N/A"),
            "delay": flight.get("departure", {}).get("delay", 0) or 0,
            "destination": flight.get("arrival", {}).get("iata", "N/A")
        }
        for flight in flights
    ]

# ✅ Fetch weather data
def fetch_weather_data():
    logger.info("🌦️ Fetching weather data from OpenWeather API...")
    url = f"http://api.openweathermap.org/data/2.5/weather?q=Paris&appid={WEATHER_API_KEY}&units=metric"
    
    response = requests.get(url)
    
    if response.status_code != 200:
        logger.error(f"❌ Weather API Error: {response.text}")
        return {"error": "Failed to fetch weather data"}
    
    weather = response.json()
    
    logger.info(f"✅ Weather data retrieved: {weather['weather'][0]['description']}")
    
    return {
        "temperature": weather.get("main", {}).get("temp", "N/A"),
        "wind_speed": round(weather.get("wind", {}).get("speed", 0) * 3.6, 2),
        "wind_gusts": round(weather.get("wind", {}).get("gust", 0) * 3.6, 2),
        "condition": weather.get("weather", [{}])[0].get("description", "No data")
    }

# ✅ API Endpoint: Get Flight Data
@app.route("/api/flights", methods=["GET"])
def get_flights():
    logger.info("📡 API Request: /api/flights")
    return jsonify({"flights": fetch_flight_data()})

# ✅ API Endpoint: Get Weather Data
@app.route("/api/weather", methods=["GET"])
def get_weather():
    logger.info("📡 API Request: /api/weather")
    return jsonify({"weather": fetch_weather_data()})

# ✅ API Endpoint: Get Both Flights & Weather
@app.route("/api/flights-weather", methods=["GET"])
def get_flight_weather():
    logger.info("📡 API Request: /api/flights-weather")
    return jsonify({"weather": fetch_weather_data(), "flights": fetch_flight_data()})

# ✅ Run the Flask App
if __name__ == "__main__":
    app.run(debug=True)
