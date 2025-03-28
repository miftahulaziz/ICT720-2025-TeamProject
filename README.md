# Project Title:  **Bro - Hiking** 🧗‍♂️🗿⛰️
 

# ICT720 2025 Team Project  
**Group Project Members:**  
1. [Mr. Thitikorn Suwannapeng](https://github.com/BenzThitikorn)  
2. [Mr. Natthanon Ratborirak](https://github.com/incer555)  
3. [Mr. Miftahul Aziz](https://github.com/miftahulaziz)  

# Project Description:  
This project collects data from the **Cucumber RS Gravitech ESP32-S2 WiFi Dev Board** equipped with sensors: **HTS221**, **BMP280**, and **MPU-6050**. While all three sensors are present, we focus only on data from **BMP280** (pressure) and **MPU-6050** (accelerometer and gyroscope) for our analysis of detecting movement changes, altitude variations, and accident occurrences using sensor fusion techniques. The system leverages accelerometer and barometric pressure sensors to provide accurate real-time monitoring and anomaly detection.

## Sensor Data Overview  
The sensors provide the following measurements:

| Sensor    | Measurements                     | Data Type         |
|-----------|----------------------------------|-------------------|
| HTS221    | Humidity, Temperature           | $\mathbb{R}$, $\mathbb{R}$ |
| BMP280    | Pressure                        | $\mathbb{R}$       |
| MPU-6050  | Accelerometer, Gyroscope        | $\mathbb{R}^3$, $\mathbb{R}^3$ |

The full data vector $\overrightarrow{X_{all}}$ is a $1 \times 9$ vector:  

$$
\overrightarrow{X_{all}} = \begin{bmatrix}
\text{Humidity} & \text{Temperature} & \text{Pressure} & \text{Accelerometer} & \text{Gyroscope} \\
\in \mathbb{R} & \in \mathbb{R} & \in \mathbb{R} & \in \mathbb{R}^3 & \in \mathbb{R}^3
\end{bmatrix}_{1 \times 9}
$$

However, we reduce this to a $1 \times 7$ feature vector $\vec{X}$ for our analysis, excluding humidity and temperature from HTS221:  

$$
\vec{X} = \begin{bmatrix}
\text{Pressure} & \text{Accelerometer} & \text{Gyroscope} \\
\in \mathbb{R} & \in \mathbb{R}^3 & \in \mathbb{R}^3
\end{bmatrix}_{1 \times 7}
$$

Where:  
- **Pressure**: Scalar value ($\mathbb{R}$).  
- **Accelerometer**: Vector ($[a_{x},a_{y}, a_{z}] \in \mathbb{R}^3$).  
- **Gyroscope**: Vector ($[\omega_{x}, \omega_{y}, \omega_{z}] \in \mathbb{R}^3$).  

Thus, $\vec{X} \in \mathbb{R}^7$ represents the feature vector used as input for anomaly detection. The train and test sets will be labeled based on real experiments conducted during hiking scenarios.

- **Input**: $\vec{X} \in \mathbb{R}^7$  
- **Output**: $Y \in GF(2)$ (i.e., $\{0, 1\}$), where:  
  - $Y = 0$: Normal movement  
  - $Y = 1$: Anomalous movement  

The Deep learning model is expressed as:  

$$
MLP(\vec{X}) = Y
$$


### Physical Interpretation  
The sensor data can be physically interpreted as:  
- **Pressure** $\mapsto$ **Height (Altitude)**: Pressure decreases with increasing altitude, enabling height tracking.  
- **Accelerometer + Time** $\mapsto$ **Average Speed or Velocity**: Integrating acceleration over time provides velocity or speed estimates.  
- **Gyroscope** $\mapsto$ **Angular Velocity**: Measures rotational speed and orientation changes, useful for detecting turns or tilts.  

These interpretations support detecting movement changes, altitude variations, and sudden anomalies like falls.

# Objectives:  
1. **Movement Change Detection**: Utilize accelerometer data to monitor changes in movement patterns, including acceleration, deceleration, and directional shifts.  
2. **Pressure and Altitude Change Detection**: Use barometric pressure sensors to measure altitude variations, enabling detection of ascending or descending movements.  
3. **Accident Detection**: Identify sudden, irregular movement patterns indicative of accidents (e.g., falls or collisions).
4. **Data Fusion**: Combine data from both accelerometer and barometric sensors for more accurate and reliable event detection.
5. **Data Processing**: Process sensor data to provide alerts in case of detected anomalies.  

# Methodology:  
- **Data Collection**: Acquire raw data from the BMP280 (pressure) and MPU-6050 (accelerometer and gyroscope) via the ESP32-S2, published to an MQTT broker (`broker.emqx.io`) under topics like `brohiking/all`, `brohiking/pressure`, etc.  
- **Pre-processing**: Filter noise using a low-pass filter and calibrate sensor readings to account for environmental variations (e.g., temperature effects on pressure).  
- **Feature Extraction**: Calculate key features such as:  
  - Acceleration magnitude: $\sqrt{x^2 + y^2 + z^2}$  
  - Altitude change rate: Derived from pressure differences over time.  
  - Sudden movement spikes: Detected via gyroscope and accelerometer thresholds.  
- **Anomaly Detection**: Use real experimental data to label normal and anomalous patterns, with detection implemented via LINE Bot, LLM API, and a web app.  
- **Integration**: Fuse accelerometer and pressure data to enhance detection accuracy.  
- **Alert System**: Notify users through LINE Bot messages, leveraging an LLM API for intelligent analysis and a web app for visualization, upon detecting anomalies.

# User Stories:  
- As a hiker, I want to monitor altitude changes during my activity to track my climbing progress.  
- As a hiker, I want real-time alerts via LINE if I fall or experience an accident, so emergency help can be notified.  
- As an outdoor enthusiast, I want to analyze my movement patterns on a web app to improve my hiking performance.

# Expected Outcomes:  
- Accurate detection of movement changes and altitude variations with a resolution of ±1 meter for altitude and ±0.1 m/s² for acceleration.  
- Reliable accident detection with minimal false positives (target accuracy > 90%).  
- Real-time alert system delivering notifications within 5 seconds of an anomaly via LINE Bot.  
- Scalable solution for applications like personal safety devices, vehicle monitoring, or outdoor activity tracking.

# Tools and Technologies:  
- **Hardware**:  
  - Cucumber RS Gravitech ESP32-S2 WiFi Dev Board  
  - Sensors: MPU-6050 (Accelerometer, Gyroscope), BMP280 (Pressure)  
- **Software**:  
  - **ESP32 Code**: Arduino C++ with libraries (`Adafruit_BMP280`, `Adafruit_MPU6050`, `PubSubClient`)  
  - **Data Pipeline**: Python with `paho-mqtt` (MQTT client) and `firebase-admin` (Firebase integration)  
- **Cloud Services**:  
  - MQTT Broker: `broker.emqx.io`  
  - Firebase Realtime Database: `https://chigga-bro-hiking-default-rtdb.asia-southeast1.firebasedatabase.app/`  
- **Alert System**:  
  - LINE Bot and LLM API for messaging  
  - Web App for data visualization and user interaction  

# Implementation Details:  
- **ESP32 Setup**: The ESP32 collects sensor data every 5 seconds, formats it as JSON, and publishes it to MQTT topics (e.g., `brohiking/all`).  
- **Python Script**: Subscribes to MQTT, processes data, and uploads it to Firebase with a server-side timestamp.  
- **Alert System**: LINE Bot + LLM api sends alerts based on anomaly detection.

# How to Run:  
1. **ESP32 Setup**:  
   - Install PlatformIO or Arduino IDE.  
   - Upload the ESP32 code from the repository to the Cucumber RS ESP32-S2 board.  
   - Update WiFi credentials (`WIFI_SSID`, `WIFI_PASSWD`) if needed.  
2. **Python Script**:  
   - Install dependencies: `pip install paho-mqtt firebase-admin`  
   - Download `serviceAccountKey.json` from Firebase Console and place it in the script directory.  
   - Run: `python mqtt_to_firebase.py`  
3. **Monitor Data**:  
   - Use Serial Monitor (`pio device monitor`) for ESP32 output.  
   - Use MQTT Explorer to subscribe to `brohiking/#`.  
   - Check Firebase Console for real-time updates.
  
# Data Result Visualization
![Description of the Image](https://github.com/miftahulaziz/ICT720-2025-TeamProject/blob/main/images/Data-2.webp?raw=true)

![Description of the Image](https://github.com/miftahulaziz/ICT720-2025-TeamProject/blob/main/images/data-1.webp?raw=true)


# Future Work:  
- Conduct real experiments to label training and test datasets for anomaly detection.  
- Integrate LINE Bot and LLM API for intelligent alerts.  
- Develop a web app for real-time data visualization and user interaction.  
- Test the system in hiking scenarios.
  
# Acknowledgments  
- **Adafruit**: For developing the sensor libraries (`Adafruit_BMP280`, `Adafruit_MPU6050`) that simplified our hardware integration.  
- **EMQX**: For offering the `broker.emqx.io` MQTT broker, enabling reliable data transmission.  
- **Firebase**: For providing the Realtime Database infrastructure to store and manage our sensor data.  
- **Vsupacha**: A special thank you to Ajarn Supachai Vorapojpisut for teaching ICT720 and his personal blog about the Cucumber RS Gravitech ESP32-S2 [Vsupacha's Medium article](https://vsupacha-90388.medium.com/การสร้าง-iot-sensor-ด้วยบอร์ด-cucumber-rs-52601663c1ff) for providing base code and valuable teaching insights that guided us in learning and implementing this IoT sensor project during the course. (And also, a big thank you for his lunch and snacks during the classes! 🍛)
