/*
  ESP32 IoT System Example Code
  
  Kết nối ESP32 với hệ thống IoT Dashboard
  - Gửi dữ liệu cảm biến qua MQTT
  - Nhận lệnh điều khiển thiết bị
  
  Cần cài đặt thư viện:
  - PubSubClient by Nick O'Leary
  - DHT sensor library by Adafruit
  - BH1750 by Christopher Laws
*/

#include <WiFi.h>
#include <PubSubClient.h>
#include <DHT.h>
#include <Wire.h>
#include <BH1750.h>

// WiFi credentials
const char* ssid = "YOUR_WIFI_SSID";
const char* password = "YOUR_WIFI_PASSWORD";

// MQTT Broker
const char* mqtt_server = "YOUR_MQTT_BROKER_IP"; // Thay bằng IP máy tính chạy MQTT broker
const int mqtt_port = 1883;

// Sensor pins
#define DHT_PIN 4
#define DHT_TYPE DHT11
#define LED_PIN 2
#define FAN_PIN 5
#define AC_PIN 18

// MQTT Topics (ESP8266 format)
const char* sensors_data_topic = "esp8266/sensors";
const char* esp_status_topic = "esp8266/status";
const char* led1_topic = "esp8266/led1";
const char* led2_topic = "esp8266/led2";
const char* led3_topic = "esp8266/led3";
const char* led_all_topic = "esp8266/all";

// Objects
WiFiClient espClient;
PubSubClient client(espClient);
DHT dht(DHT_PIN, DHT_TYPE);
BH1750 lightMeter;

// Device states
bool ledState = false;
bool fanState = false;
bool acState = false;

// Timing
unsigned long lastSensorRead = 0;
const unsigned long sensorInterval = 5000; // 5 seconds

void setup() {
  Serial.begin(115200);
  
  // Initialize pins
  pinMode(LED_PIN, OUTPUT);
  pinMode(FAN_PIN, OUTPUT);
  pinMode(AC_PIN, OUTPUT);
  
  // Initialize sensors
  dht.begin();
  Wire.begin();
  lightMeter.begin();
  
  // Connect to WiFi
  setup_wifi();
  
  // Setup MQTT
  client.setServer(mqtt_server, mqtt_port);
  client.setCallback(callback);
}

void setup_wifi() {
  delay(10);
  Serial.println();
  Serial.print("Connecting to ");
  Serial.println(ssid);

  WiFi.begin(ssid, password);

  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
  }

  Serial.println("");
  Serial.println("WiFi connected");
  Serial.println("IP address: ");
  Serial.println(WiFi.localIP());
}

void callback(char* topic, byte* payload, unsigned int length) {
  Serial.print("Message arrived [");
  Serial.print(topic);
  Serial.print("] ");
  
  String message = "";
  for (int i = 0; i < length; i++) {
    message += (char)payload[i];
  }
  Serial.println(message);
  
  // Handle ESP8266 format topics
  if (strcmp(topic, led1_topic) == 0) {
    handleLED1Control(message);
  }
  else if (strcmp(topic, led2_topic) == 0) {
    handleLED2Control(message);
  }
  else if (strcmp(topic, led3_topic) == 0) {
    handleLED3Control(message);
  }
  else if (strcmp(topic, led_all_topic) == 0) {
    handleLEDAllControl(message);
  }
}

void handleLED1Control(String message) {
  if (message == "ON") {
    ledState = true;
    digitalWrite(LED_PIN, HIGH);
    publishESPStatus("LED1 ON");
  }
  else if (message == "OFF") {
    ledState = false;
    digitalWrite(LED_PIN, LOW);
    publishESPStatus("LED1 OFF");
  }
}

void handleLED2Control(String message) {
  if (message == "ON") {
    fanState = true;
    digitalWrite(FAN_PIN, HIGH);
    publishESPStatus("LED2 ON");
  }
  else if (message == "OFF") {
    fanState = false;
    digitalWrite(FAN_PIN, LOW);
    publishESPStatus("LED2 OFF");
  }
}

void handleLED3Control(String message) {
  if (message == "ON") {
    acState = true;
    digitalWrite(AC_PIN, HIGH);
    publishESPStatus("LED3 ON");
  }
  else if (message == "OFF") {
    acState = false;
    digitalWrite(AC_PIN, LOW);
    publishESPStatus("LED3 OFF");
  }
}

void handleLEDAllControl(String message) {
  if (message == "ON") {
    ledState = true;
    fanState = true;
    acState = true;
    digitalWrite(LED_PIN, HIGH);
    digitalWrite(FAN_PIN, HIGH);
    digitalWrite(AC_PIN, HIGH);
    publishESPStatus("ALL LED ON");
  }
  else if (message == "OFF") {
    ledState = false;
    fanState = false;
    acState = false;
    digitalWrite(LED_PIN, LOW);
    digitalWrite(FAN_PIN, LOW);
    digitalWrite(AC_PIN, LOW);
    publishESPStatus("ALL LED OFF");
  }
}

void publishESPStatus(String status) {
  client.publish(esp_status_topic, status.c_str());
  Serial.println("Published to " + String(esp_status_topic) + ": " + status);
}

void publishSensorData() {
  // Read sensors
  float humidity = dht.readHumidity();
  float temperature = dht.readTemperature();
  float lux = lightMeter.readLightLevel();
  
  // Create combined sensor data JSON
  String message = "{";
  message += "\"temperature\":" + String(temperature, 1) + ",";
  message += "\"humidity\":" + String(humidity, 1) + ",";
  message += "\"light\":" + String(lux, 1) + ",";
  message += "\"timestamp\":\"" + getCurrentTime() + "\"";
  message += "}";
  
  client.publish(sensors_data_topic, message.c_str());
  Serial.println("Published to " + String(sensors_data_topic) + ": " + message);
}

String getCurrentTime() {
  // Simple timestamp - in real application, use NTP
  return String(millis());
}

void reconnect() {
  while (!client.connected()) {
    Serial.print("Attempting MQTT connection...");
    
    String clientId = "ESP32Client-";
    clientId += String(random(0xffff), HEX);
    
    if (client.connect(clientId.c_str())) {
      Serial.println("connected");
      
      // Subscribe to ESP8266 control topics
      client.subscribe(led1_topic);
      client.subscribe(led2_topic);
      client.subscribe(led3_topic);
      client.subscribe(led_all_topic);
      
    } else {
      Serial.print("failed, rc=");
      Serial.print(client.state());
      Serial.println(" try again in 5 seconds");
      delay(5000);
    }
  }
}

void loop() {
  if (!client.connected()) {
    reconnect();
  }
  client.loop();

  // Read and publish sensor data every 5 seconds
  if (millis() - lastSensorRead > sensorInterval) {
    lastSensorRead = millis();
    
    // Read sensors and publish combined data
    float humidity = dht.readHumidity();
    float temperature = dht.readTemperature();
    float lux = lightMeter.readLightLevel();
    
    // Check if readings are valid and publish
    if (!isnan(humidity) && !isnan(temperature) && lux >= 0) {
      publishSensorData();
      Serial.println("Sensor data published");
    }
  }
}
