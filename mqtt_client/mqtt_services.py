import paho.mqtt.client as mqtt
import json
import datetime
from config import Config
from database.models import create_sensor_reading, create_action, update_device_status
import threading
import time
import pytz

class MQTTService:
    def __init__(self):
        self.client = mqtt.Client()
        self.client.on_connect = self.on_connect
        self.client.on_message = self.on_message
        self.client.on_disconnect = self.on_disconnect
        self.connected = False
        self.socketio = None
        # Biến track ESP32 (như bạn thêm)
        self.esp32_connected = False
        self.esp_timeout = 30  # Timeout 30 giây
        self.last_message_time = None
        self.timeout_timer = None

    def set_socketio(self, socketio_instance):
        self.socketio = socketio_instance
        print("✅ MQTT socketio injected")

    def on_connect(self, client, userdata, flags, rc):
        if rc == 0:
            print(f"Connected to MQTT broker")
            self.connected = True
            # Subscribe topics
            client.subscribe(Config.SENSORS_DATA_TOPIC)
            client.subscribe(Config.TOPIC_LED1_STATE)
            client.subscribe(Config.TOPIC_LED2_STATE)
            client.subscribe(Config.TOPIC_LED3_STATE)
            client.subscribe(Config.TOPIC_LED_ALL_STATE)
            print(f"Subscribed to {Config.SENSORS_DATA_TOPIC}")
            print(f"Subscribed to LED state topics")
            # Yêu cầu ESP gửi state
            client.publish("esp8266/get_state", "get")
            print("Requested current LED states")
            # Bắt đầu timer để track ESP (nếu chưa có message)
            self.start_timeout_timer()
        else:
            print(f"Failed to connect: {rc}")
            
    def on_disconnect(self, client, userdata, rc):
        print(f"Disconnected from MQTT broker: {rc}")
        self.connected = False
        self.stop_timeout_timer()
        self.update_esp_status(False)

    def on_message(self, client, userdata, msg):
        try:
            topic = msg.topic
            payload = msg.payload.decode('utf-8')
            
            print(f"Received message on {topic}: {payload}")
            
            # Khi nhận message từ ESP, set online
            if not msg.retain and topic in [Config.SENSORS_DATA_TOPIC, Config.TOPIC_LED1_STATE, Config.TOPIC_LED2_STATE, Config.TOPIC_LED3_STATE, Config.TOPIC_LED_ALL_STATE]:
                self.update_esp_status(True)
            
            self.handle_message_fallback(topic, payload)
        except Exception as e:
            print(f"Error processing message: {e}")

    def update_esp_status(self, connected):
        """Cập nhật trạng thái ESP32 và emit nếu thay đổi"""
        if self.esp32_connected != connected:
            self.esp32_connected = connected
            print(f"ESP32 status changed: {'Online' if connected else 'Offline'}")
            
            # Nếu ESP32 disconnect, cập nhật tất cả LED thành OFF
            if not connected:
                print("ESP32 disconnected - Setting all LEDs to OFF")
                led_devices = [
                    {"id": "led1", "name": "LED 1"},
                    {"id": "led2", "name": "LED 2"},
                    {"id": "led3", "name": "LED 3"}
                ]
                for led in led_devices:
                    # Cập nhật trạng thái LED trong database thành OFF
                    update_device_status(led["id"], False)
                    # Emit qua Socket.IO để cập nhật UI dashboard
                    self.emit_device_status_update(led["id"], False, led["name"])
            
            # Emit trạng thái ESP32
            if self.socketio:
                self.socketio.emit('esp_status_update', {'connected': connected})
            
            if connected:
                self.start_timeout_timer()
            else:
                self.stop_timeout_timer()

    def start_timeout_timer(self):
        """Bắt đầu timer để detect offline"""
        self.stop_timeout_timer()
        self.last_message_time = time.time()
        self.timeout_timer = threading.Timer(self.esp_timeout, self.check_esp_timeout)
        self.timeout_timer.start()

    def stop_timeout_timer(self):
        """Dừng timer"""
        if self.timeout_timer:
            self.timeout_timer.cancel()
            self.timeout_timer = None

    def check_esp_timeout(self):
        """Kiểm tra offline nếu không message trong esp_timeout"""
        if time.time() - self.last_message_time >= self.esp_timeout:
            self.update_esp_status(False)

    def handle_message_fallback(self, topic, payload):
        """Xử lý message nếu không có callback từ app.py"""
        try:
            if topic == Config.SENSORS_DATA_TOPIC:
                self.handle_sensor_data(payload)
            elif topic in [Config.TOPIC_LED1_STATE, Config.TOPIC_LED2_STATE, Config.TOPIC_LED3_STATE, Config.TOPIC_LED_ALL_STATE]:
                self.handle_led_state(topic, payload)
        except Exception as e:
            print(f"Error in fallback message handling: {e}")

    def handle_sensor_data(self, payload):
        try:
            data = json.loads(payload)
            temperature = data.get('temperature')
            humidity = data.get('humidity')
            light = data.get('light')
            
            # Store combined sensor reading in database
            if temperature is not None or humidity is not None or light is not None:
                create_sensor_reading(
                    temperature=temperature,
                    humidity=humidity,
                    light=light
                )
                print(f"Sensor data stored: T={temperature}°C, H={humidity}%, L={light}lux")
                
                # **THÊM: Emit qua Socket.IO để cập nhật client thời gian thực**
                self.emit_sensor_data_update(temperature, humidity, light)
            
        except Exception as e:
            print(f"Error handling sensor data: {e}")

    # **THÊM: Method mới để emit sensor data qua Socket.IO**
    def emit_sensor_data_update(self, temperature, humidity, light):
        """Gửi WebSocket event để cập nhật UI dashboard thời gian thực"""
        try:
            
            # Lấy thời gian Việt Nam (UTC+7)
            vn_tz = pytz.timezone('Asia/Ho_Chi_Minh')
            vn_time = datetime.datetime.now(vn_tz)
            
            # Emit data với format match dashboard.html
            self.socketio.emit('sensor_data_update', {
                'temperature': temperature,
                'humidity': humidity,
                'light': light,
                'timestamp': vn_time.isoformat()  # Thêm timestamp nếu cần
            })
            print(f"WebSocket emitted sensor data: T={temperature}, H={humidity}, L={light}")
        except Exception as e:
            print(f"Error emitting sensor WebSocket: {e}")
    
    def handle_led_state(self, topic, payload):
        """Xử lý ACK trạng thái LED từ ESP"""
        try:
            # Xác định device ID từ topic
            if topic == Config.TOPIC_LED1_STATE:
                device_id = "led1"
                device_name = "LED 1"
            elif topic == Config.TOPIC_LED2_STATE:
                device_id = "led2"
                device_name = "LED 2"
            elif topic == Config.TOPIC_LED3_STATE:
                device_id = "led3"
                device_name = "LED 3"
            # elif topic == Config.TOPIC_LED_ALL_STATE:
            #     # Xử lý trạng thái tất cả LED
            #     self.handle_all_led_state(payload)
            #     return
            else:
                return
            
            # Xác định trạng thái
            status = payload == "ON"
            action_type = "Bật" if status else "Tắt"
            
            print(f"LED State ACK: {device_name} = {payload}")
            
            # Cập nhật database
            update_device_status(device_id, status)
            
            # Ghi lịch sử hành động
            create_action(
                action_id=f"{device_id}_{int(time.time())}",
                device_id=device_id,
                device_name=device_name,
                action_type=action_type
            )
            
            # Gửi WebSocket để cập nhật UI
            self.emit_device_status_update(device_id, status, device_name)
            
        except Exception as e:
            print(f"Error handling LED state: {e}")
    
    def handle_all_led_state(self, payload):
        """Xử lý ACK trạng thái tất cả LED từ ESP"""
        try:
            status = payload == "ON"
            action_type = "Bật" if status else "Tắt"
            
            print(f"All LED State ACK: {payload}")
            
            # Cập nhật trạng thái cho tất cả LED
            all_leds = [
                {"id": "led1", "name": "LED 1"},
                {"id": "led2", "name": "LED 2"}, 
                {"id": "led3", "name": "LED 3"}
            ]
            
            for led in all_leds:
                # Cập nhật database
                update_device_status(led["id"], status)
                
                # Ghi lịch sử hành động
                create_action(
                    action_id=f"{led['id']}_all_{int(time.time())}",
                    device_id=led["id"],
                    device_name=led["name"],
                    action_type=action_type
                )
                
                # Gửi WebSocket để cập nhật UI
                self.emit_device_status_update(led["id"], status, led["name"])
                
        except Exception as e:
            print(f"Error handling All LED state: {e}")
    
    def emit_device_status_update(self, device_id, status, device_name):
        """Gửi WebSocket event để cập nhật UI"""
        try:
            
            # Lấy thời gian Việt Nam (UTC+7)
            vn_tz = pytz.timezone('Asia/Ho_Chi_Minh')
            vn_time = datetime.datetime.now(vn_tz)
            
            self.socketio.emit('device_status_update', {
                'device': device_id,
                'status': status,
                'device_name': device_name,
                'timestamp': vn_time.isoformat()
            })
            print(f"WebSocket emitted: {device_id} = {status}")
        except Exception as e:
            print(f"Error emitting WebSocket: {e}")
    
    # def handle_esp_status(self, payload):
    #     try:
    #         message = payload.strip()
    #         print(f"ESP Status: {message}")
            
    #         # Parse status message and log action
    #         if "LED" in message and "ON" in message:
    #             device_name = "LED" if "ALL" not in message else "Tất cả LED"
    #             action_type = "Bật"
    #             create_action(
    #                 action_id=f"led_{int(time.time())}",
    #                 device_name=device_name,
    #                 action_type=action_type
    #             )
    #         elif "LED" in message and "OFF" in message:
    #             device_name = "LED" if "ALL" not in message else "Tất cả LED"
    #             action_type = "Tắt"
    #             create_action(
    #                 action_id=f"led_{int(time.time())}",
    #                 device_name=device_name,
    #                 action_type=action_type
    #             )
                
    #     except Exception as e:
    #         print(f"Error handling ESP status: {e}")
    
    def connect(self):
        try:
            if Config.MQTT_USERNAME and Config.MQTT_PASSWORD:
                self.client.username_pw_set(Config.MQTT_USERNAME, Config.MQTT_PASSWORD)
            
            self.client.connect(Config.MQTT_BROKER, Config.MQTT_PORT, 60)
            self.client.loop_start()
            return True
        except Exception as e:
            print(f"Failed to connect to MQTT broker: {e}")
            return False
    
    def disconnect(self):
        self.client.loop_stop()
        self.client.disconnect()
        self.stop_timeout_timer()
        self.update_esp_status(False)
    
    def publish_device_control(self, topic, message): # hàm pub lệnh bât/tắt led 
        if not self.connected:
            print("MQTT client not connected")
            return False

        # ESP8266 expects raw text payload (e.g., "ON"/"OFF"), not JSON
        result = self.client.publish(topic, payload=message, qos=0, retain=False)
        if result.rc == mqtt.MQTT_ERR_SUCCESS:
            print(f"Published to {topic}: {message}")
            return True
        else:
            print(f"Failed to publish to {topic}: rc={result.rc}")
            return False
    
    def control_led(self, status):
        # ESP8266 expects simple text commands
        message = "ON" if status else "OFF"
        return self.publish_device_control(Config.TOPIC_LED_ALL, message)
    
    def control_led1(self, status):
        message = "ON" if status else "OFF"
        return self.publish_device_control(Config.TOPIC_LED1, message)
    
    def control_led2(self, status):
        message = "ON" if status else "OFF"
        return self.publish_device_control(Config.TOPIC_LED2, message)
    
    def control_led3(self, status):
        message = "ON" if status else "OFF"
        return self.publish_device_control(Config.TOPIC_LED3, message)
    
    def control_internal_led(self, status):
        # Internal LED có thể sử dụng LED1 topic hoặc tạo topic riêng
        message = "ON" if status else "OFF"
        return self.publish_device_control(Config.TOPIC_LED1, message)

# Global MQTT service instance
mqtt_service = MQTTService()