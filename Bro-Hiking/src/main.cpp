#include <Wire.h>
#include <Adafruit_BMP280.h>
#include <Adafruit_MPU6050.h>
#include <Adafruit_HTS221.h>
#include <WiFi.h>
#include <WiFiClient.h>
#include <PubSubClient.h>
#include "time.h"

// WiFi setting
#define WIFI_SSID "Chigga"
#define WIFI_PASSWD "12345678"
// MQTT setting
#define MQTT_SERVER "broker.emqx.io"
#define MQTT_PORT 1883
#define MQTT_TOPIC "brohiking/#"
#define MQTT_CLIENT_ID "ESP32_Sensor_Client"

// NTP server settings for time synchronization
const char* ntpServer = "pool.ntp.org";
const long  gmtOffset_sec = 25200;  // UTC+7 for Bangkok (7 * 3600 seconds)
const int   daylightOffset_sec = 0;  // No daylight saving in Thailand

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
    while (1) delay(10);
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
  
  setupHardware();
  
  WiFi.begin(WIFI_SSID, WIFI_PASSWD);
  while (WiFi.status() != WL_CONNECTED) {
    delay(100);
    Serial.print(".");
  }
  Serial.println("\nWiFi connected");
  Serial.printf("IP address: %s\n", WiFi.localIP().toString().c_str());
  
  // Initialize time
  configTime(gmtOffset_sec, daylightOffset_sec, ntpServer);
  Serial.println("Waiting for time sync...");
  while (time(nullptr) < 100000) {
    delay(100);
    Serial.print(".");
  }
  Serial.println("\nTime synchronized");
  
  mqtt_client.setServer(MQTT_SERVER, MQTT_PORT);
  Serial.println("Starting");
}

void loop() {
  if (!mqtt_client.connected()) {
    reconnect();
  }
  mqtt_client.loop();

  static uint32_t prev_millis = 0;
  char json_body[300];
  const char json_tmpl[] = "{\"timestamp\": \"%s\","
                          "\"pressure\": %.2f,"
                          "\"temperature\": %.2f,"
                          "\"humidity\": %.2f,"
                          "\"acceleration\": [%.2f,%.2f,%.2f],"
                          "\"angular_velocity\": [%.2f,%.2f,%.2f]}";
  
  if (millis() - prev_millis > 5000) {
    prev_millis = millis();
    sensors_event_t temp, humid;
    sensors_event_t a, g;
    
    // Get current time (Bangkok time)
    time_t now;
    struct tm timeinfo;
    time(&now);
    localtime_r(&now, &timeinfo);
    char timestamp[20];
    strftime(timestamp, sizeof(timestamp), "%Y-%m-%d %H:%M:%S", &timeinfo);
    
    // Read sensor data
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
    
    // Format and publish combined data
    sprintf(json_body, json_tmpl, timestamp, p, t, h, ax, ay, az, gx, gy, gz);
    Serial.println(json_body);
    mqtt_client.publish("brohiking/all", json_body);
    
  }
  delay(10);
}