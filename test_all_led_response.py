#!/usr/bin/env python3
"""
Test script để giả lập response từ ESP khi điều khiển tất cả LED
"""

import paho.mqtt.client as mqtt
import time
import json

# MQTT Settings
MQTT_BROKER = "localhost"
MQTT_PORT = 1883

# Topics
ALL_LED_STATE_TOPIC = "esp8266/all/state"

def on_connect(client, userdata, flags, rc):
    if rc == 0:
        print("Connected to MQTT broker")
        # Subscribe to ALL LED control topic to simulate ESP response
        client.subscribe("esp8266/all")
        print("Subscribed to esp8266/all")
    else:
        print(f"Failed to connect: {rc}")

def on_message(client, userdata, msg):
    topic = msg.topic
    payload = msg.payload.decode()
    
    print(f"Received: {topic} -> {payload}")
    
    # Giả lập ESP response cho ALL LED
    if topic == "esp8266/all":
        if payload in ["ON", "OFF"]:
            # Simulate ESP response after 1 second delay
            time.sleep(1)
            
            # Publish ALL LED state response
            client.publish(ALL_LED_STATE_TOPIC, payload)
            print(f"Simulated ESP response: {ALL_LED_STATE_TOPIC} -> {payload}")
            
            # Also publish individual LED states
            for led in ["led1", "led2", "led3"]:
                client.publish(f"esp8266/{led}/state", payload)
                print(f"Simulated ESP response: esp8266/{led}/state -> {payload}")

def main():
    client = mqtt.Client()
    client.on_connect = on_connect
    client.on_message = on_message
    
    try:
        client.connect(MQTT_BROKER, MQTT_PORT, 60)
        print("Starting MQTT loop...")
        client.loop_forever()
    except KeyboardInterrupt:
        print("\nShutting down...")
        client.disconnect()
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    main()