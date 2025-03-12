#Bro-Hiking first draft with mock up

import streamlit as st
import pandas as pd
import numpy as np
import time

# Function to simulate hiking data
def generate_hiking_data():
    time_series = np.arange(0, 60, 1)  # 60 seconds tracking
    height_series = np.cumsum(np.random.randint(-2, 5, size=len(time_series))) + 1000  # Height fluctuation
    speed_series = np.abs(np.random.normal(5, 2, size=len(time_series)))  # Random speed values
    return pd.DataFrame({"Time (s)": time_series, "Height (m)": height_series, "Speed (km/h)": speed_series})

# Simulated real-time hiking data
st.title("🥾 Bro-Hiking Tracker")
st.write("Monitor your hiking height and speed in real-time!")

data = generate_hiking_data()

# Line Chart for height tracking
st.subheader("📈 Height Tracking Over Time")
st.line_chart(data.set_index("Time (s)")["Height (m)"])

# Detect sudden height drops
fall_threshold = 8  # Define height drop threshold (meters per second)
data['Height Drop'] = data['Height (m)'].diff().fillna(0)
if (data['Height Drop'] < -fall_threshold).any():
    st.error("⚠️ Sudden height drop detected! Possible fall!")

# Show last recorded data
st.subheader("📊 Latest Tracking Data")
st.dataframe(data.tail(10))
