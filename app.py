from flask import Flask, render_template, request, jsonify
from flask_socketio import SocketIO, emit
from config import Config
from database.connection import db
from database.models import *
from mqtt_client.mqtt_services import mqtt_service
from datetime import datetime, timedelta
import json
import pytz
import random
from dash import Dash, html, dcc, callback, Output, Input 
import plotly.graph_objects as go 
app = Flask(__name__)
app.config.from_object(Config)
socketio = SocketIO(app, cors_allowed_origins="*", async_mode="threading")
dash_app = Dash(__name__, server=app, url_base_pathname='/dash/')

# Add built-in functions to template context
app.jinja_env.globals.update(min=min, max=max, timedelta=timedelta)

# Initialize MQTT service
mqtt_service.connect()
mqtt_service.set_socketio(socketio)



dash_app.layout = html.Div([
    html.H3("Biểu đồ cảm biến realtime", style={"textAlign": "center"}),
    dcc.Graph(id="live-graph", style={"height": "600px"}),
    dcc.Interval(
        id="interval-component",
        interval=5*1000,  # 5 giây cập nhật
        n_intervals=0
    )
])

@dash_app.callback(
    Output("live-graph", "figure"),
    Input("interval-component", "n_intervals")
)
def update_graph(n):
    print(f"Updating graph, interval: {n}")  # Debug log
    
    try:
        # Lấy 50 bản ghi gần nhất từ MongoDB
        data = list(db.sensor_data.find().sort("timestamp", -1).limit(50))
        print(f"Found {len(data)} records in database")  # Debug log
        
        if not data:
            # Trả về biểu đồ trống với thông báo
            empty_fig = go.Figure()
            empty_fig.add_annotation(
                text="Không có dữ liệu cảm biến trong database",
                xref="paper", yref="paper",
                x=0.5, y=0.5, showarrow=False,
                font=dict(size=16, color="gray")
            )
            empty_fig.update_layout(
                title="⚠️ Chưa có dữ liệu cảm biến",
                template="plotly_white",
                height=600
            )
            return empty_fig
        
        # Đảo ngược để hiển thị theo thứ tự thời gian
        data.reverse()
        
        # Lấy dữ liệu với xử lý None values
        timestamps = [item["timestamp"] for item in data]
        temperatures = [item.get("temperature", 0) if item.get("temperature") is not None else 0 for item in data]
        humidities = [item.get("humidity", 0) if item.get("humidity") is not None else 0 for item in data]
        lights = [item.get("light", 0) if item.get("light") is not None else 0 for item in data]

        figure = go.Figure()

        # Trục 1: Nhiệt độ (°C)
        figure.add_trace(go.Scatter(
            x=timestamps,
            y=temperatures,
            mode="lines+markers",
            name="🌡️ Temperature (°C)",
            line=dict(color="#e74c3c", width=3),
            marker=dict(size=6, color="#e74c3c"),
            yaxis="y1"
        ))

        # Trục 2: Độ ẩm (%)
        figure.add_trace(go.Scatter(
            x=timestamps,
            y=humidities,
            mode="lines+markers",
            name="💧 Humidity (%)",
            line=dict(color="#3498db", width=3),
            marker=dict(size=6, color="#3498db"),
            yaxis="y2"
        ))

        # Trục 3: Ánh sáng (Lux)
        figure.add_trace(go.Scatter(
            x=timestamps,
            y=lights,
            mode="lines+markers",
            name="💡 Light (Lux)",
            line=dict(color="#f39c12", width=3),
            marker=dict(size=6, color="#f39c12"),
            yaxis="y3"
        ))

        # Cấu hình layout với 3 y-axis
        figure.update_layout(
            title={
                'text': f"📊 Biểu đồ cảm biến thời gian thực ({len(data)} điểm dữ liệu)",
                'x': 0.5,
                'font': {'size': 18, 'color': '#2c3e50'}
            },
            xaxis=dict(
                title="🕒 Thời gian",
                titlefont=dict(size=14, color='#2c3e50')
            ),
            yaxis=dict(
                title="🌡️ Temperature (°C)",
                titlefont=dict(color="#e74c3c", size=12),
                tickfont=dict(color="#e74c3c"),
                side="left"
            ),
            yaxis2=dict(
                title="💧 Humidity (%)",
                titlefont=dict(color="#3498db", size=12),
                tickfont=dict(color="#3498db"),
                overlaying="y",
                side="right"
            ),
            yaxis3=dict(
                title="💡 Light (Lux)",
                titlefont=dict(color="#f39c12", size=12),
                tickfont=dict(color="#f39c12"),
                anchor="free",
                overlaying="y",
                side="right",
                position=0.95  # Điều chỉnh position
            ),
            legend=dict(
                x=0, y=1, 
                bgcolor="rgba(255,255,255,0.8)",
                bordercolor="rgba(0,0,0,0.2)",
                borderwidth=1
            ),
            margin=dict(l=80, r=120, t=80, b=60),  # Tăng margin phải
            template="plotly_white",
            hovermode='x unified',
            height=600
        )

        return figure
        
    except Exception as e:
        print(f"Error in update_graph: {e}")  # Debug log
        
        # Trả về biểu đồ lỗi
        error_fig = go.Figure()
        error_fig.add_annotation(
            text=f"Lỗi khi tải dữ liệu: {str(e)}",
            xref="paper", yref="paper",
            x=0.5, y=0.5, showarrow=False,
            font=dict(size=16, color="red")
        )
        error_fig.update_layout(
            title="❌ Lỗi tải dữ liệu",
            template="plotly_white",
            height=600
        )
        return error_fig
@app.route('/')
def dashboard():
    # Get latest sensor data
    latest_data = get_latest_sensor_data()
    
    # Get device status
    devices = get_all_devices()
    
    # Get LED status from database
    led_status = {}
    for device in devices:
        if device.get('_id') in ['led1', 'led2', 'led3']:
            led_status[device['_id']] = device.get('status')
    
    # Mock data for demo if no real data
    if not latest_data:
        vn_tz = pytz.timezone('Asia/Ho_Chi_Minh')
        latest_data = {
            'temperature': 28.5,
            'humidity': 65,
            'light': 500,
            'timestamp': datetime.now(vn_tz)
        }
    
    return render_template('dashboard.html', 
                         latest_data=latest_data,
                         devices=devices,
                         led_status=led_status,
                         esp_connected=mqtt_service.esp32_connected)

@app.route('/data-sensor')
def data_sensor():
    # Get sensor data with pagination
    page = request.args.get('page', 1, type=int)
    per_page = 10
    
    # Get total count
    total = db.sensor_data.count_documents({})
    
    # Get data with pagination
    data = list(db.sensor_data.find().sort('timestamp', -1).skip((page-1)*per_page).limit(per_page))
    
    return render_template('data_sensor.html', 
                         sensor_data=data,
                         page=page,
                         per_page=per_page,
                         total=total)

@app.route('/action-history')
def action_history():
    # Get action history with pagination and filtering
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)
    device_filter = request.args.get('device', '')
    date_from = request.args.get('date_from', '')
    date_to = request.args.get('date_to', '')
    
    # Build query with filters
    query = {}
    
    # Device filter
    if device_filter:
        query['device_name'] = device_filter
    
    # Date range filter
    if date_from or date_to:
        date_query = {}
        if date_from:
            try:
                from_date = datetime.strptime(date_from, '%Y-%m-%d')
                date_query['$gte'] = from_date
            except ValueError:
                pass
        if date_to:
            try:
                to_date = datetime.strptime(date_to, '%Y-%m-%d')
                # Add 23:59:59 to include the whole day
                to_date = to_date.replace(hour=23, minute=59, second=59)
                date_query['$lte'] = to_date
            except ValueError:
                pass
        if date_query:
            query['timestamp'] = date_query
    
    # Get total count with filters
    total = db.actions.count_documents(query)
    
    # Get actions with pagination and filters
    actions = list(db.actions.find(query).sort('timestamp', -1).skip((page-1)*per_page).limit(per_page))
    
    # Get unique device names for filter dropdown
    device_names = db.actions.distinct('device_name')
    
    return render_template('action_history.html',
                         actions=actions,
                         page=page,
                         per_page=per_page,
                         total=total,
                         device_names=device_names,
                         current_device=device_filter,
                         current_date_from=date_from,
                         current_date_to=date_to)

@app.route('/profile')
def profile():
    return render_template('profile.html')

# API endpoints for device control (ESP8266)
@app.route('/api/control/led', methods=['POST'])
def control_led():
    data = request.get_json()
    status = data.get('status', False)
    
    success = mqtt_service.control_led(status)
    
    if success:
        return jsonify({'success': True, 'status': status, 'message': 'LED control command sent'})
    else:
        return jsonify({'success': False, 'status': status, 'message': 'Failed to send LED control command'})

@app.route('/api/control/led1', methods=['POST'])
def control_led1():
    data = request.get_json()
    status = data.get('status', False)
    
    success = mqtt_service.control_led1(status)
    
    if success:
        return jsonify({'success': True, 'status': status, 'message': 'LED1 control command sent'})
    else:
        return jsonify({'success': False, 'status': status, 'message': 'Failed to send LED1 control command'})

@app.route('/api/control/led2', methods=['POST'])
def control_led2():
    data = request.get_json()
    status = data.get('status', False)
    
    success = mqtt_service.control_led2(status)
    
    if success:
        return jsonify({'success': True, 'status': status, 'message': 'LED2 control command sent'})
    else:
        return jsonify({'success': False, 'status': status, 'message': 'Failed to send LED2 control command'})

@app.route('/api/control/led3', methods=['POST'])
def control_led3():
    data = request.get_json()
    status = data.get('status', False)
    
    success = mqtt_service.control_led3(status)
    
    if success:
        return jsonify({'success': True, 'status': status, 'message': 'LED3 control command sent'})
    else:
        return jsonify({'success': False, 'status': status, 'message': 'Failed to send LED3 control command'})

 

# API endpoint for sensor data
@app.route('/api/sensor-data')
def api_sensor_data():
    limit = request.args.get('limit', 10, type=int)
    data = list(db.sensor_data.find().sort('timestamp', -1).limit(limit))
    
    # Convert ObjectId to string for JSON serialization
    for item in data:
        item['_id'] = str(item['_id'])
        if 'timestamp' in item:
            item['timestamp'] = item['timestamp'].isoformat()
    
    return jsonify(data)


# API endpoint for chart HTML
@app.route('/api/chart-html')
def api_chart_html():
    try:
        # Gọi trực tiếp function update_graph từ Dash callback
        figure = update_graph(0)  # n_intervals = 0
        
        # Convert Plotly figure to HTML
        import plotly.offline as pyo
        
        config = {
            'displayModeBar': True,
            'displaylogo': False,
            'modeBarButtonsToRemove': ['pan2d', 'lasso2d', 'select2d', 'resetScale2d'],
            'responsive': True
        }
        
        chart_html = pyo.plot(
            figure, 
            output_type='div', 
            include_plotlyjs=False,  # Sẽ load từ CDN
            config=config,
            div_id='embedded-dash-chart'
        )
        
        return jsonify({
            'success': True,
            'chart_html': chart_html,
            'timestamp': datetime.now().isoformat()
        })
        
    except Exception as e:
        print(f"Error in api_chart_html: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

# Thêm API mới cho dữ liệu lịch sử (để biểu đồ tải ban đầu)
@app.route('/api/sensor-data-latest')
def api_sensor_data_latest():
    range_param = request.args.get('range', '1h')  # Mặc định 1 giờ
    vn_tz = pytz.timezone('Asia/Ho_Chi_Minh')
    now = datetime.now(vn_tz)
    
    # Xác định khoảng thời gian dựa trên range
    if range_param == '1h':
        start_time = now - timedelta(hours=1)
    elif range_param == '6h':
        start_time = now - timedelta(hours=6)
    elif range_param == '24h':
        start_time = now - timedelta(hours=24)
    else:
        start_time = now - timedelta(hours=1)
    
    # Lấy dữ liệu từ DB
    data = list(db.sensor_data.find({
        'timestamp': {'$gte': start_time}
    }).sort('timestamp', 1).limit(100))  # Giới hạn 100 điểm
    
    if not data:
        return jsonify({'success': False, 'message': 'No data available'})
    
    # Chuẩn bị dữ liệu cho Chart.js
    labels = [item['timestamp'].strftime('%H:%M:%S') for item in data]
    temperature = [item.get('temperature', 0) for item in data]
    humidity = [item.get('humidity', 0) for item in data]
    light = [item.get('light', 0) for item in data]
    
    return jsonify({
        'success': True,
        'data': {
            'labels': labels,
            'temperature': temperature,
            'humidity': humidity,
            'light': light
        }
    })

# WebSocket events
@socketio.on('connect')
def handle_connect():
    print('Client connected')
    emit('status', {'msg': 'Connected to server'})

@socketio.on('disconnect')
def handle_disconnect():
    print('Client disconnected')

@socketio.on('request_sensor_data')
def handle_sensor_data_request():
    latest_data = get_latest_sensor_data()
    if latest_data:
        latest_data['_id'] = str(latest_data['_id'])
        if 'timestamp' in latest_data:
            latest_data['timestamp'] = latest_data['timestamp'].isoformat()
    emit('sensor_data_update', latest_data)

def init_database(force_reset=False):
    if force_reset:
        db.users.drop()
        db.devices.drop()
        db.device_types.drop()
        db.actions.drop()
        db.sensor_data.drop()
        print("🗑️ Database reset complete - All data cleared")
    """Initialize database with sample data"""
    # Create device types - chỉ cần 2 loại: DHT11 và BH1750
    create_device_type("dht11_sensor", "DHT11 Sensor", "°C/%", 0)  # role=0 (sensor) - nhiệt độ + độ ẩm
    create_device_type("bh1750_sensor", "BH1750 Light Sensor", "Lux", 0)  # role=0 (sensor) - ánh sáng
    create_device_type("led_actuator", "Đèn LED", "", 1)  # role=1 (actuator)
    
    # Create sample user
    create_user("user_001", "admin", "admin123", "admin", "admin@iot.com")
    
    # Create devices - chỉ 3 LED + 2 cảm biến
    # 3 LED (sử dụng ID đơn giản để match với MQTT)
    create_device("led1", "LED 1", "led_actuator", False, "Phòng làm việc", "user_001", "LED điều khiển ánh sáng")
    create_device("led2", "LED 2", "led_actuator", False, "Phòng khách", "user_001", "LED điều khiển ánh sáng")
    create_device("led3", "LED 3", "led_actuator", False, "Phòng ngủ", "user_001", "LED điều khiển ánh sáng")
    
    # 2 cảm biến
    create_device("dht11_001", "DHT11 Sensor", "dht11_sensor", True, "Phòng khách", "user_001", "Cảm biến nhiệt độ và độ ẩm DHT11")
    create_device("bh1750_001", "BH1750 Light Sensor", "bh1750_sensor", True, "Phòng khách", "user_001", "Cảm biến ánh sáng BH1750")
    
    # Add sample sensor data
    # Check if we already have data
    if db.sensor_data.count_documents({}) == 0:
        print("Adding sample sensor data...")
        vn_tz = pytz.timezone('Asia/Ho_Chi_Minh')
        for i in range(20):
            timestamp = datetime.now(vn_tz) - timedelta(minutes=i*5)
            create_sensor_reading(
                temperature=round(random.uniform(25, 30), 1),
                humidity=round(random.uniform(45, 70), 1),
                light=round(random.uniform(500, 800), 1),
                timestamp=timestamp
            )
    
    # Add sample actions
    if db.actions.count_documents({}) == 0:
        print("Adding sample action data...")
        actions = ["Bật", "Tắt"]
        
        for i in range(10):
            create_action(
                action_id=f"sample_{i}",
                device_id=random.choice(["led1", "led2", "led3"]),
                user_id="user_001",
                action_type=random.choice(actions),
                description=f"Sample action {i}",
            )

if __name__ == '__main__':
    # Run the app
    # init_database(force_reset=True)
    socketio.run(app, debug=True, host='0.0.0.0', port=5000)
