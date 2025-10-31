import os 
from dotenv import load_dotenv

load_dotenv()

class Config:
    SECRET_KEY = os.getenv('SECRET_KEY', 'hoangduchung')
    MONGO_URI = os.getenv('MONGO_URI', 'mongodb://localhost:27017/iotsystem')
    MQTT_BROKER = os.getenv('MQTT_BROKER', 'localhost')
    MQTT_PORT = int(os.getenv('MQTT_PORT', 1883))
    MQTT_USERNAME = os.getenv('MQTT_USERNAME', 'duchung')
    MQTT_PASSWORD = os.getenv('MQTT_PASSWORD', 'duchung')
    
    # Sensor topics (ESP8266 format)
    SENSORS_DATA_TOPIC = os.getenv('SENSORS_DATA_TOPIC', 'esp8266/sensors') # Dữ liệu cảm biến
    ESP_STATUS_TOPIC = os.getenv('ESP_STATUS_TOPIC', 'esp8266/status') # Trạng thái ESP8266
    
    # LED Control topics
    TOPIC_LED1 = os.getenv('TOPIC_LED1', 'esp8266/led1') # Điều khiển Led 1
    TOPIC_LED2 = os.getenv('TOPIC_LED2', 'esp8266/led2') # Điều khiển Led 2
    TOPIC_LED3 = os.getenv('TOPIC_LED3', 'esp8266/led3') # Điều khiển Led 3
    TOPIC_LED_ALL = os.getenv('TOPIC_LED_ALL', 'esp8266/all') # Điều khiển tất cả Led

    # NEW: topics for LEDs on D0 and A0
    TOPIC_LED_D0 = os.getenv('TOPIC_LED_D0', 'esp8266/led_d0')   # Điều khiển LED D0
    TOPIC_LED_A0 = os.getenv('TOPIC_LED_A0', 'esp8266/led_a0')   # Điều khiển LED A0
    
    # LED State topics (ACK từ ESP)
    TOPIC_LED1_STATE = os.getenv('TOPIC_LED1_STATE', 'esp8266/led1/state') # Trạng thái Led 1
    TOPIC_LED2_STATE = os.getenv('TOPIC_LED2_STATE', 'esp8266/led2/state') # Trạng thái Led 2
    TOPIC_LED3_STATE = os.getenv('TOPIC_LED3_STATE', 'esp8266/led3/state') # Trạng thái Led 3
    TOPIC_LED_ALL_STATE = os.getenv('TOPIC_LED_ALL_STATE', 'esp8266/all/state') # Trạng thái tất cả Led

    # NEW: state topics for D0 and A0
    TOPIC_LED_D0_STATE = os.getenv('TOPIC_LED_D0_STATE', 'esp8266/led_d0/state')
    TOPIC_LED_A0_STATE = os.getenv('TOPIC_LED_A0_STATE', 'esp8266/led_a0/state')


