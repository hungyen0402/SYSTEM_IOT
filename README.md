# IoT System Dashboard

Hệ thống điều khiển thiết bị IoT thông minh với giao diện web và kết nối MQTT.

## Tính năng

- **Dashboard**: Hiển thị dữ liệu cảm biến real-time (nhiệt độ, độ ẩm, ánh sáng)
- **Data Sensor**: Xem lịch sử dữ liệu cảm biến với tìm kiếm và phân trang
- **Action History**: Theo dõi lịch sử các hành động bật/tắt thiết bị
- **Device Control**: Điều khiển LED, quạt, máy điều hòa qua MQTT
- **Real-time Updates**: Cập nhật dữ liệu real-time qua WebSocket

## Công nghệ sử dụng

- **Backend**: Flask, Flask-SocketIO
- **Database**: MongoDB (PyMongo)
- **MQTT**: Paho MQTT Client
- **Frontend**: Bootstrap 5, Chart.js, Socket.IO
- **Hardware**: ESP32

## Cài đặt

### 1. Cài đặt dependencies

```bash
pip install -r requirements.txt
```

### 2. Cài đặt MongoDB

- Tải và cài đặt MongoDB từ https://www.mongodb.com/try/download/community
- Khởi động MongoDB service

### 3. Cài đặt MQTT Broker (Mosquitto)

- Windows: Tải từ https://mosquitto.org/download/
- Linux: `sudo apt install mosquitto mosquitto-clients`
- macOS: `brew install mosquitto`

### 4. Cấu hình biến môi trường

Tạo file `.env` trong thư mục gốc:

```env
SECRET_KEY=your-secret-key-here-change-in-production
MONGO_URI=mongodb://localhost:27017/iotsystem
MQTT_BROKER=localhost
MQTT_PORT=1883
MQTT_USERNAME=
MQTT_PASSWORD=

# Sensor topics
TEMPERATURE_TOPIC=sensors/temperature
HUMIDITY_TOPIC=sensors/humidity
LIGHT_TOPIC=sensors/light

# Device control topics
LED_CONTROL_TOPIC=devices/led/control
FAN_CONTROL_TOPIC=devices/fan/control
AC_CONTROL_TOPIC=devices/ac/control
```

## Chạy ứng dụng

```bash
python app.py
```

Ứng dụng sẽ chạy tại: http://localhost:5000

## Cấu trúc dự án

```
BTL_IOT/
├── app.py                 # Ứng dụng Flask chính
├── config.py             # Cấu hình
├── requirements.txt      # Dependencies
├── README.md            # Hướng dẫn
├── database/
│   ├── __init__.py
│   ├── connection.py    # Kết nối MongoDB
│   └── models.py        # Models và database functions
├── mqtt_client/
│   └── mqtt_services.py # MQTT client service
├── templates/
│   ├── base.html        # Template cơ sở
│   ├── dashboard.html   # Trang dashboard
│   ├── data_sensor.html # Trang dữ liệu cảm biến
│   ├── action_history.html # Trang lịch sử hành động
│   └── profile.html     # Trang profile
└── static/
    ├── css/
    │   └── style.css    # CSS tùy chỉnh
    └── js/
        └── main.js      # JavaScript chính
```

## MQTT Topics

### Sensor Data Topics
- `sensors/temperature` - Dữ liệu nhiệt độ
- `sensors/humidity` - Dữ liệu độ ẩm  
- `sensors/light` - Dữ liệu ánh sáng

### Device Control Topics
- `devices/led/control` - Điều khiển LED
- `devices/fan/control` - Điều khiển quạt
- `devices/ac/control` - Điều khiển máy điều hòa

### Device Status Topics
- `devices/led/control/status` - Trạng thái LED
- `devices/fan/control/status` - Trạng thái quạt
- `devices/ac/control/status` - Trạng thái máy điều hòa

## Format dữ liệu MQTT

### Sensor Data
```json
{
    "value": 25.5,
    "timestamp": "2024-10-26T11:30:00Z"
}
```

### Device Control
```json
{
    "device_id": "led_001",
    "action": "on",
    "timestamp": "2024-10-26T11:30:00Z"
}
```

### Device Status
```json
{
    "device_id": "led_001",
    "device_name": "Đèn LED",
    "status": true,
    "timestamp": "2024-10-26T11:30:00Z"
}
```

## API Endpoints

- `GET /` - Dashboard
- `GET /data-sensor` - Trang dữ liệu cảm biến
- `GET /action-history` - Trang lịch sử hành động
- `GET /profile` - Trang profile
- `POST /api/control/led` - Điều khiển LED
- `POST /api/control/fan` - Điều khiển quạt
- `POST /api/control/ac` - Điều khiển máy điều hòa
- `GET /api/sensor-data` - API dữ liệu cảm biến

## ESP32 Integration

Để kết nối ESP32 với hệ thống, bạn cần:

1. Cài đặt thư viện MQTT cho ESP32
2. Kết nối các cảm biến (DHT11, LM35, BH1750)
3. Kết nối các thiết bị điều khiển (LED, Relay)
4. Gửi dữ liệu lên các MQTT topics tương ứng

## Troubleshooting

### Lỗi kết nối MongoDB
- Kiểm tra MongoDB đã chạy chưa
- Kiểm tra URI kết nối trong file .env

### Lỗi kết nối MQTT
- Kiểm tra MQTT broker đã chạy chưa
- Kiểm tra cấu hình MQTT trong file .env

### Lỗi WebSocket
- Kiểm tra port 5000 có bị chiếm không
- Kiểm tra firewall settings

## Tác giả

**Hoàng Đức Hưng** - B22DCCN408
- GitHub: https://github.com/hungyen0402/IOTSYSTEM.git

## License

Dự án này được tạo cho mục đích học tập và nghiên cứu.
