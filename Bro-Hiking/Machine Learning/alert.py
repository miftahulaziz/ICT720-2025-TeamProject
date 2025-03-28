from anomaly import detect_anomaly
from linebot import send_line_broadcast_curl
import joblib
import numpy as np
import requests
import json
import pandas as pd

def detect_anomaly(model_path, firebase_url):
    # Load the model
    model = joblib.load(model_path)
    
    try:
        response = requests.get(firebase_url)
        response.raise_for_status()
        data = response.json()
        
        if isinstance(data, dict):
            latest_key = max(data.keys())
            latest_data = {latest_key: data[latest_key]}
        else:
            latest_data = "Unexpected data format"
        
    except requests.exceptions.RequestException as e:
        return f"Error fetching data: {e}", None
    except json.JSONDecodeError as e:
        return f"Error decoding JSON: {e}", None
    except Exception as e:
        return f"An unexpected error occurred: {e}", None
    
    all_data = data.get("all", {})
    
    records = []
    for values in all_data.values():
        record = {
            "acceleration_x": values["acceleration"][0],
            "acceleration_y": values["acceleration"][1],
            "acceleration_z": values["acceleration"][2],
            "angular_velocity_x": values["angular_velocity"][0],
            "angular_velocity_y": values["angular_velocity"][1],
            "angular_velocity_z": values["angular_velocity"][2],
            "pressure": values["pressure"],
            "timestamp": values["timestamp"]
        }
        records.append(record)
    
    df = pd.DataFrame(records)
    
    df['angular_velocity_magnitude'] = np.sqrt(df['angular_velocity_x']**2 + df['angular_velocity_y']**2 + df['angular_velocity_z']**2)
    df['acceleration_magnitude'] = np.sqrt(df['acceleration_x']**2 + df['acceleration_y']**2 + df['acceleration_z']**2)
    
    df['delta_acceleration_magnitude'] = df['acceleration_magnitude'].diff()
    df['delta_angular_velocity_magnitude'] = df['angular_velocity_magnitude'].diff()
    df['delta_pressure'] = df['pressure'].diff()
    
    x = np.array(df.tail(1)[['delta_acceleration_magnitude', 'delta_angular_velocity_magnitude', 'delta_pressure']])
    
    if df['delta_pressure'].iloc[-1] > 0:
        return "Normal", 0.0
    
    prediction = model.predict(x)
    anomaly_score = model.decision_function(x)
    
    return ("Anomaly" if prediction[0] == -1 else "Normal"), anomaly_score[0]

# Load the LINE channel access token from token.json
with open('token.json', 'r') as f:
    token_data = json.load(f)
    channel_access_token = token_data["token"]


result, score = detect_anomaly('model.joblib', 'https://chigga-bro-hiking-default-rtdb.asia-southeast1.firebasedatabase.app/.json')
if score < 0:
    message1 = "Anomaly detected"
    message2 = f"Anomaly score: {score}"

    send_line_broadcast_curl(channel_access_token, message1, message2)
    