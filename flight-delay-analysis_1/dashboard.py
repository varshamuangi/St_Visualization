import streamlit as st
import pandas as pd
import plotly.express as px
import numpy as np
import folium
from streamlit_folium import folium_static
import plotly.figure_factory as ff

# Load the dataset
dataset_path = "flight_delays_dataset.csv"

# ✅ Check if the file exists before loading
try:
    df = pd.read_csv(dataset_path)
except FileNotFoundError:
    st.error("🚨 Dataset not found! Please upload 'flight_delays_dataset.csv' to run this dashboard.")
    st.stop()

# Convert date columns to datetime format
df["Departure Time"] = pd.to_datetime(df["Departure Time"])
df["Arrival Time"] = pd.to_datetime(df["Arrival Time"])

# Define airport coordinates for mapping
airport_coords = {
    "JFK": [40.6413, -73.7781],
    "LAX": [33.9416, -118.4085],
    "ORD": [41.9742, -87.9073],
    "ATL": [33.6407, -84.4277],
    "DFW": [32.8998, -97.0403],
    "AMS": [52.3081, 4.7642],
    "LHR": [51.4700, -0.4543],
    "CDG": [49.0097, 2.5479],
    "DXB": [25.2532, 55.3657],
    "SIN": [1.3644, 103.9915]
}

# 🎨 Apply Custom Styling
st.set_page_config(page_title="Flight Delay Dashboard", layout="wide")

st.title("✈️ Flight Delay & Route Analysis Dashboard")
st.markdown("This interactive dashboard provides **real-time flight delay insights, weather impact, and route recommendations**.")

# 🗂️ Sidebar - Select Airport
st.sidebar.header("🔎 Filter Options")
selected_airport = st.sidebar.selectbox("Select an Airport", sorted(df["Departure Airport"].unique()), help="Pick an airport to analyze its delay trends.")

# Filter data by selected airport
filtered_df = df[df["Departure Airport"] == selected_airport]

# 🎭 Layout with Columns
col1, col2 = st.columns(2)

# 📊 Left Column: Improved Flight Delay Trends Graph
with col1:
    st.subheader("📉 Flight Delay Trends Over Time")

    # Aggregate delays per day for better readability
    daily_delays = filtered_df.groupby(filtered_df["Departure Time"].dt.date).agg({"Delay Minutes": "mean"}).reset_index()
    daily_delays["Smoothed Delay"] = daily_delays["Delay Minutes"].rolling(window=5, min_periods=1).mean()

    # Provide option to switch between Area Chart and Bar Chart
    chart_type = st.radio("Select Chart Type:", ["Area Chart", "Bar Chart"], horizontal=True)

    if chart_type == "Area Chart":
        fig_trends = px.area(daily_delays, x="Departure Time", y="Smoothed Delay",
                             title="Average Flight Delays Over Time",
                             labels={"Departure Time": "Date", "Smoothed Delay": "Avg Delay (mins)"},
                             template="plotly_white",
                             line_shape="spline")
    else:
        fig_trends = px.bar(daily_delays, x="Departure Time", y="Smoothed Delay",
                             title="Average Flight Delays Over Time",
                             labels={"Departure Time": "Date", "Smoothed Delay": "Avg Delay (mins)"},
                             template="plotly_white")

    st.plotly_chart(fig_trends, use_container_width=True)

# 🏔️ Right Column: Flight Delays by Weather Condition & Airline Impact
with col2:
    st.subheader("🌦️ Flight Delays by Airline and Weather Conditions")
    
    # Group by Airline and Weather Condition, calculating average delay
    airline_weather_delays = filtered_df.groupby(["Airline", "Weather Condition"])["Delay Minutes"].mean().reset_index()

    # Create grouped bar chart
    fig_airline_weather = px.bar(
        airline_weather_delays,
        x="Airline",
        y="Delay Minutes",
        color="Weather Condition",
        barmode="group",  # Grouped bars for better comparison
        title=f"Flight Delays by Airline and Weather Conditions at {selected_airport}",
        labels={"Delay Minutes": "Avg Delay (mins)", "Airline": "Airline"},
        color_discrete_sequence=px.colors.qualitative.Set3
    )

    # Display chart
    st.plotly_chart(fig_airline_weather, use_container_width=True)


# ✅ **Filter Flights by Delay Reason**
st.subheader("🚨 Filter Flights by Delay Reason")

# Create a bar chart showing the count of flights per delay reason
delay_reason_counts = filtered_df["Delay Reason"].value_counts().reset_index()
delay_reason_counts.columns = ["Delay Reason", "Number of Flights"]

# Interactive Bar Chart
fig_delay_reasons = px.bar(
    delay_reason_counts, 
    x="Delay Reason", 
    y="Number of Flights", 
    title="✈️ Number of Flights Affected by Each Delay Reason",
    labels={"Delay Reason": "Delay Type", "Number of Flights": "Total Flights"},
    color="Number of Flights", 
    color_continuous_scale="Reds"
)
st.plotly_chart(fig_delay_reasons, use_container_width=True)

# ✅ Dropdown to Select a Specific Delay Reason
selected_reason = st.selectbox("🔍 Select a Delay Reason to View Affected Flights", delay_reason_counts["Delay Reason"].unique())

# 📋 Display Affected Flights in a Styled Table
st.subheader(f"📋 Top 10 Flights Affected by {selected_reason}")

affected_flights = filtered_df[filtered_df["Delay Reason"] == selected_reason]

if affected_flights.empty:
    st.warning(f"No flights affected by {selected_reason}.")
else:
    # Sort by Delay Minutes (highest delays first) and get top 10
    table_data = affected_flights.nlargest(10, "Delay Minutes")[["Flight Number", "Departure Airport", "Arrival Airport", "Airline", "Departure Time", "Delay Minutes"]].copy()
    
    # Reset index to start from 1
    table_data.reset_index(drop=True, inplace=True)
    table_data.index = table_data.index + 1  # Set index to start from 1

    # Format Departure Time
    table_data["Departure Time"] = table_data["Departure Time"].dt.strftime("%I:%M %p")

    # Add Status Column
    def get_status(delay):
        if delay == 0:
            return "🟢 On Time"
        elif delay < 30:
            return "🟡 Slight Delay"
        else:
            return "🔴 Delayed"

    table_data["Status"] = table_data["Delay Minutes"].apply(get_status)

    # ✅ Display Styled Table
    st.dataframe(table_data)



# ✅ Predict Best & Worst Dates to Fly for Next Month
# st.subheader("📅 Find the Best & Worst Dates to Fly for Next Month")

# # 🛫 Start Destination is Fixed to the Selected Airport
# start_destination = selected_airport  # Ensures it syncs with sidebar selection

# # 🛬 User selects the end destination
# end_destination = st.selectbox("Select End Destination", sorted(df[df["Departure Airport"] == start_destination]["Arrival Airport"].unique()))

# # Generate delay predictions for the next month
# next_month_dates = pd.date_range(start=df["Departure Time"].max() + pd.Timedelta(days=1), periods=30, freq='D')
# delay_predictions = np.random.randint(5, 60, size=len(next_month_dates))  
# best_day = next_month_dates[np.argmin(delay_predictions)]  
# worst_day = next_month_dates[np.argmax(delay_predictions)]  

# # 📌 Show Best & Worst Date Recommendation for Next Month
# st.markdown(f"✅ **Best Day to Fly:** ✈️ {best_day.strftime('%Y-%m-%d')}")
# st.markdown(f"❌ **Day to Avoid:** ⚠️ {worst_day.strftime('%Y-%m-%d')}")


# ✅ Predict Best Date Based on Available Flights
st.subheader("📅 Find the Best Available Date & Flight for Next Month")

# 🛫 Start Destination is Fixed to the Selected Airport
start_destination = selected_airport  

# 🛬 User selects the end destination
end_destination = st.selectbox("Select End Destination", sorted(df[df["Departure Airport"] == start_destination]["Arrival Airport"].unique()))

# ✅ Find Dates with Available Flights for Selected Route
route_flights = df[(df["Departure Airport"] == start_destination) & (df["Arrival Airport"] == end_destination)]

if route_flights.empty:
    st.warning(f"⚠️ No flights available from {start_destination} to {end_destination}. Please try another route.")
else:
    # Extract available dates
    available_dates = route_flights["Departure Time"].dt.date.unique()
    
    if len(available_dates) == 0:
        st.warning("⚠️ No available dates found for this route.")
    else:
        # ✅ Find the Best Date (Least Average Delay)
        best_date = (
            route_flights.groupby(route_flights["Departure Time"].dt.date)["Delay Minutes"]
            .mean()
            .idxmin()
        )

        # ✅ Select the Best Flight on That Date
        best_flight_df = route_flights[route_flights["Departure Time"].dt.date == best_date].sort_values(by="Delay Minutes").head(1)

        # 📌 Show Best Date Recommendation
        st.markdown(f"✅ **Best Day to Fly:** ✈️ `{best_date}`")

        # ✅ Display Best Flight Information
        if not best_flight_df.empty:
            best_flight = best_flight_df.iloc[0]  # Get the best flight row
            st.success("🎉 Best flight found with the shortest delay!")
            st.markdown(f"**🛫 Flight Number:** `{best_flight['Flight Number']}`")
            st.markdown(f"**🚀 Airline:** `{best_flight['Airline']}`")
            st.markdown(f"**📅 Date:** `{best_flight['Departure Time'].strftime('%Y-%m-%d')}`")
            st.markdown(f"**🕒 Departure Time:** `{best_flight['Departure Time'].strftime('%H:%M')}`")
            st.markdown(f"**⏳ Expected Delay:** `{best_flight['Delay Minutes']} minutes`")
        else:
            st.warning(f"⚠️ No flights available on `{best_date}`. Try another route.")


# 🗺️ Show Flight Route Map
st.subheader("🌍 Flight Route Visualization")
map_center = airport_coords.get(start_destination, [37.7749, -95.7129])
m = folium.Map(location=map_center, zoom_start=4)

if start_destination in airport_coords and end_destination in airport_coords:
    folium.Marker(airport_coords[start_destination], popup=start_destination, icon=folium.Icon(color="blue")).add_to(m)
    folium.Marker(airport_coords[end_destination], popup=end_destination, icon=folium.Icon(color="red")).add_to(m)
    folium.PolyLine([airport_coords[start_destination], airport_coords[end_destination]], color="blue", weight=4).add_to(m)

folium_static(m)

st.subheader("⚠️ Advisory: Be Prepared for Delays")
st.markdown("These conditions have historically caused significant delays. Plan accordingly.")
