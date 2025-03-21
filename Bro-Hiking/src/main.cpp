#include <Wire.h>
#include <Adafruit_BMP280.h>
#include <Adafruit_MPU6050.h>
#include <Adafruit_HTS221.h>
#include <WiFi.h>
#include <WiFiClient.h>
#include <PubSubClient.h>

// WiFi and MQTT Settings
#define WIFI_SSID "Chigga"
#define WIFI_PASSWD "12345678"
#define MQTT_SERVER "broker.emqx.io"
#define MQTT_PORT 8084
#define MQTT_TOPIC "brohiking/data"  // Topic to publish sensor data
#define MQTT_CLIENT_ID "ESP32_Sensor_Client"  // Unique client ID

// Global objects
WiFiClient wifi_client;
PubSubClient mqtt_client(wifi_client);
Adafruit_BMP280 bmp;
Adafruit_HTS221 hts;
Adafruit_MPU6050 mpu;

void setupHardware() {
  Wire.begin(41, 40, 100000);
  
  if (!bmp.begin(0x76)) {
    Serial.println("BMP280 sensor failed");
    while (1) delay(10); // Hang if sensor fails
  } else {
    Serial.println("BMP280 sensor ready");
  }
  
  if (!hts.begin_I2C()) {
    Serial.println("HTS221 sensor failed");
    while (1) delay(10);
  } else {
    Serial.println("HTS221 sensor ready");
  }
  
  if (!mpu.begin()) {
    Serial.println("MPU6050 sensor failed");
    while (1) delay(10);
  } else {
    Serial.println("MPU6050 sensor ready");
  }
  
  pinMode(2, OUTPUT);
  digitalWrite(2, HIGH);
}

void reconnect() {
  while (!mqtt_client.connected()) {
    Serial.print("Attempting MQTT connection...");
    if (mqtt_client.connect(MQTT_CLIENT_ID)) {
      Serial.println("connected");
      mqtt_client.subscribe(MQTT_TOPIC); 
    } else {
      Serial.print("failed, rc=");
      Serial.print(mqtt_client.state());
      Serial.println(" try again in 5 seconds");
      delay(5000);
    }
  }
}

void setup() {
  Serial.begin(115200);
  
  // 1. Initialize the sensors
  setupHardware();
  
  // 2. Initialize WiFi
  WiFi.begin(WIFI_SSID, WIFI_PASSWD);
  while (WiFi.status() != WL_CONNECTED) {
    delay(100);
    Serial.print(".");
  }
  Serial.println("\nWiFi connected");
  Serial.printf("IP address: %s\n", WiFi.localIP().toString().c_str());
  
  // 3. Initialize MQTT
  mqtt_client.setServer(MQTT_SERVER, MQTT_PORT);
  Serial.println("Starting");
}

void loop() {
  if (!mqtt_client.connected()) {
    reconnect();
  }
  mqtt_client.loop(); // Handle MQTT messages

  static uint32_t prev_millis = 0;
  char json_body[200];
  const char json_tmpl[] = "{\"pressure\": %.2f,"
                           "\"temperature\": %.2f,"
                           "\"humidity\": %.2f,"
                           "\"acceleration\": [%.2f,%.2f,%.2f],"
                           "\"angular_velocity\": [%.2f,%.2f,%.2f]}";
  
  if (millis() - prev_millis > 5000) {
    prev_millis = millis();
    sensors_event_t temp, humid;
    sensors_event_t a, g;
    
    float p = bmp.readPressure();
    hts.getEvent(&humid, &temp);
    float t = temp.temperature;
    float h = humid.relative_humidity;
    mpu.getEvent(&a, &g, &temp);
    float ax = a.acceleration.x;
    float ay = a.acceleration.y;
    float az = a.acceleration.z;
    float gx = g.gyro.x;
    float gy = g.gyro.y;
    float gz = g.gyro.z;
    
    sprintf(json_body, json_tmpl, p, t, h, ax, ay, az, gx, gy, gz);
    Serial.println(json_body);
    mqtt_client.publish(MQTT_TOPIC, json_body);
  }
  delay(10);
}