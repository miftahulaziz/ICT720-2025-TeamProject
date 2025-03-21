import paho.mqtt.client as mqtt
from datetime import datetime
import json
import os
import sys
import firebase_admin
from firebase_admin import credentials
from firebase_admin import db

# Initialize Firebase with service account key
cred = credentials.Certificate("chigga-bro-hiking-firebase-adminsdk-fbsvc-bab90ce1ce.json")  # Path to your service account key
firebase_admin.initialize_app(cred, {
    'databaseURL': 'https://chigga-bro-hiking-default-rtdb.asia-southeast1.firebasedatabase.app/'
})

# MQTT settings (matching your ESP32 code)
mqtt_broker = os.getenv('MQTT_BROKER', 'broker.emqx.io')
mqtt_port = os.getenv('MQTT_PORT', 1883)
mqtt_topic = os.getenv('MQTT_TOPIC', 'brohiking/')  # Base topic from your ESP32

if mqtt_broker is None or mqtt_port is None:
    print('MQTT_BROKER and MQTT_PORT are required')
    sys.exit(1)

# Callback for when the client connects to the MQTT broker
def on_connect(client, userdata, flags, reason_code, properties):
    print(f"Connected with result code {reason_code}")
    client.subscribe(mqtt_topic + "#")  # Subscribe to brohiking/# (all subtopics)

# Callback for when a message is received from the MQTT broker
def on_message(client, userdata, msg):
    print(f"Received from {msg.topic}: {msg.payload.decode()}")
    try:
        # Parse the JSON payload from ESP32
        data = json.loads(msg.payload.decode())
        
        # Extract the topic suffix (e.g., "all", "pressure", "climate", "acceleration", "gyro")
        topic_suffix = msg.topic.split('/')[-1]
        
        # Add server-side received timestamp
        data['received_timestamp'] = datetime.now().isoformat()
        
        # Define Firebase path based on MQTT topic
        firebase_path = f"/{topic_suffix}"
        
        # Push data to Firebase with a unique key
        ref = db.reference(firebase_path)
        new_entry = ref.push(data)
        
        print(f"Uploaded to Firebase at {firebase_path}/{new_entry.key}")
        
    except json.JSONDecodeError as e:
        print(f"Failed to parse JSON: {e}")
    except Exception as e:
        print(f"Error uploading to Firebase: {e}")

# Initialize MQTT client
mqttc = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)
mqttc.on_connect = on_connect
mqttc.on_message = on_message

# Connect to MQTT broker
mqttc.connect(mqtt_broker, int(mqtt_port), 60)

# Start the MQTT loop
print(f"Listening for messages on {mqtt_topic}#...")
mqttc.loop_forever()