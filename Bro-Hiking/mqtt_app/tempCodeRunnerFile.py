import paho.mqtt.client as mqtt
from datetime import datetime
import urllib3
import json
import os
import sys
import sqlite3
from pymongo import MongoClient

# initialize environment variables
mongo_uri = os.getenv('MONGO_URI', None)
mongo_db = os.getenv('MONGO_DB', None)
mongo_col_device = os.getenv('MONGO_COL_DEV', None)
mqtt_broker = os.getenv('MQTT_BROKER', None)
mqtt_port = os.getenv('MQTT_PORT', None)
mqtt_topic = os.getenv('MQTT_TOPIC', None)
if mongo_uri is None or mqtt_broker is None or mqtt_port is None or mqtt_topic is None:
    print('MONGO_URI and MQTT settings are required')
    sys.exit(1)

# initialize app
mongo_client = MongoClient(mongo_uri)

# The callback for when the client receives a CONNACK response from the server.
def on_connect(client, userdata, flags, reason_code, properties):
    print(f"Connected with result code {reason_code}")
    # Subscribing in on_connect() means that if we lose the connection and
    # reconnect then subscriptions will be renewed.
    client.subscribe(mqtt_topic + "#")

# The callback for when a PUBLISH message is received from the server.
def on_message(client, userdata, msg):
    print(msg.topic+" "+str(msg.payload))
    # heartbeat message
    if msg.topic.split('/')[-1] == "beat":
        data = json.loads(msg.payload.decode())
        print(f"Device: {data['mac']}")
        return
    # data message
    if msg.topic.split('/')[-1] == "data":
        data = json.loads(msg.payload.decode())
        print(f"Device: {data['name']}")
        # insert to SQLite
        station = msg.topic.split('/')[2]
        device = data['name']
        rssi = data['rssi']
        c.execute("INSERT INTO taist (station, device, rssi) VALUES (?, ?, ?)", 
                  (station, device, rssi))
        print("Inserted to SQLite")
        conn.commit()
        # insert to MongoDB
        db = mongo_client[mongo_db]
        db_dev_col = db[mongo_col_device]
        db_dev_col.insert_one({"timestamp": datetime.now(), 
                               "station": station, 
                               "device": device, 
                               "rssi": rssi})
        print(db_dev_col.count_documents({}))
        print("Inserted to MongoDB")

    # insert to Firebase
     http = urllib3.PoolManager()
     payload = {"timestamp": datetime.now().isoformat(), "message": msg.payload.decode()}
     encoded_payload = json.dumps(payload).encode('utf-8')
     print(encoded_payload)
    http.request('POST', 'https://chigga-bro-hiking-default-rtdb.asia-southeast1.firebasedatabase.app/bro.json', 
                 body=encoded_payload, headers={'Content-Type': 'application/json'})



# init MQTT
mqttc = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)
mqttc.on_connect = on_connect
mqttc.on_message = on_message

mqttc.connect(mqtt_broker, int(mqtt_port), 60)

# Blocking call that processes network traffic, dispatches callbacks and
# handles reconnecting.
# Other loop*() functions are available that give a threaded interface and a
# manual interface.
mqttc.loop_forever()