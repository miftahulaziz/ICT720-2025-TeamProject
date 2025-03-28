import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import time
import joblib
import json
import requests
from datetime import datetime
from model import detect_anomaly
import firebase_admin
from firebase_admin import credentials
from firebase_admin import db

url = "https://chigga-bro-hiking-default-rtdb.asia-southeast1.firebasedatabase.app/.json"
model_path = 'model.joblib'

try:
    response = requests.get(url)
    response.raise_for_status()  # Raise an exception for bad status codes

    data = response.json()

    if isinstance(data, dict):  # Check if data is a dictionary
        latest_key = max(data.keys())  # Get the latest key (assuming keys are time-ordered)
        latest_data = {latest_key: data[latest_key]}  # Extract the latest record
    else:
        latest_data = "Unexpected data format"

    print(json.dumps(latest_data, indent=2))

except requests.exceptions.RequestException as e:
    print(f"Error fetching data: {e}")
except json.JSONDecodeError as e:
    print(f"Error decoding JSON: {e}")
except Exception as e:
    print(f"An unexpected error occurred: {e}")

def pressure_to_altitude(pressure):
    P0 = 1013.25  # Sea level standard pressure in hPa
    return 44330 * (1 - (pressure / P0) ** 0.1903)


all_data = data["all"]

records = []
for id, values in all_data.items():
    record = {
        "acceleration_x": values["acceleration"][0],
        "acceleration_y": values["acceleration"][1],
        "acceleration_z": values["acceleration"][2],
        "angular_velocity_x": values["angular_velocity"][0],
        "angular_velocity_y": values["angular_velocity"][1],
        "angular_velocity_z": values["angular_velocity"][2],
        "pressure": values["pressure"],
        "received_timestamp": values["received_timestamp"],
        "timestamp": values["timestamp"]
    }
    records.append(record)

df = pd.DataFrame(records)

records = []
for id, values in all_data.items():
    record = {
        "acceleration_x": values["acceleration"][0],
        "acceleration_y": values["acceleration"][1],
        "acceleration_z": values["acceleration"][2],
        "angular_velocity_x": values["angular_velocity"][0],
        "angular_velocity_y": values["angular_velocity"][1],
        "angular_velocity_z": values["angular_velocity"][2],
        "pressure": values["pressure"],
        "temperature": values["temperature"],
        "timestamp": values["timestamp"]
    }
    records.append(record)

df = pd.DataFrame(records)
df['angular_velocity_magnitude'] = np.sqrt(df['angular_velocity_x']**2 + df['angular_velocity_y']**2 + df['angular_velocity_z']**2)
df['acceleration_magnitude'] = np.sqrt(df['acceleration_x']**2 + df['acceleration_y']**2 + df['acceleration_z']**2)

df['delta_acceleration_magnitude'] = df['acceleration_magnitude'].diff()
df['delta_angular_velocity_magnitude'] = df['angular_velocity_magnitude'].diff()
df['delta_pressure'] = df['pressure'].diff()

# Set page layout to fullscreen
st.set_page_config(layout="wide")

# UI Header
st.title("Bro-Hiking: Mate Monitoring")

# Display current date and time
st.markdown(f"<div class='datetime'>{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</div>", unsafe_allow_html=True)

# Toggle between chart and table
view_mode = st.radio("Select View Mode:", ["Live Chart", "Historical Table"])

col1, col2 = st.columns([3, 1])

with col1:
    if view_mode == "Live Chart":
        fig = px.line(df, x="timestamp", y=pressure_to_altitude(pressure=df["pressure"]), markers=True, title="Real-Time Altitude")
        st.plotly_chart(fig)
    else:
        st.table(df[::-1])  # Show latest data on top

with col2:
    latest_speed = df.iloc[-1]["delta_acceleration_magnitude"] if df.shape[0] > 1 else 0
    latest_temperature = df.iloc[-1]["temperature"]

    st.metric(label="Speed (km/h)", value=f"{latest_speed:.2f}")
    st.metric(label="Temperature (°C)", value=f"{latest_temperature:.2f}")

# Auto-refresh every second
time.sleep(1)
st.experimental_rerun()
