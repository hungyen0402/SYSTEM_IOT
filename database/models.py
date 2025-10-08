from database.connection import db
from werkzeug.security import generate_password_hash, check_password_hash
import datetime
import pytz

# Lấy múi giờ Việt Nam
VN_TZ = pytz.timezone('Asia/Ho_Chi_Minh')

def get_vietnam_time():
    # Tạo datetime với múi giờ Việt Nam
    return datetime.datetime.now(VN_TZ)
# User 
def create_user(user_id, username, password, role, email):
    password_hash = generate_password_hash(password)
    user = {
        "_id": user_id,
        'username': username, 
        'password_hash': password_hash,
        'role': role,
        'email': email
    }
    db.users.insert_one(user)
    return user 

def get_user_by_name(username):
    return db.users.find_one({'username': username})

def check_user_password(user, password):
    return check_password_hash(user['password_hash'], password)

# Device (thay thế Sensor)
def create_device(device_id=None, name=None, device_type_id=None, status=False, location=None, user_id=None, description=None, data_logging=None):
    # Nếu data_logging không được chỉ định, tự động xác định dựa trên device_type
    if data_logging is None:
        device_type = db.device_types.find_one({'_id': device_type_id})
        if device_type and device_type.get('role') == 0:  # 0=sensor
            data_logging = 60  # Mặc định 60 giây cho sensor
        else:  # 1=actuator hoặc không xác định
            data_logging = 0   # Không cần data logging cho actuator
    current_time = get_vietnam_time()
    device = {
        'name': name,
        'device_type_id': device_type_id,  # Foreign key to DeviceType
        'status': status,
        'location': location,
        'user_id': user_id,  # Foreign key to User
        'description': description,
        'data_logging': data_logging,  # 0=không cần, >0=interval (giây)
        'created_at': current_time,
        'last_updated': current_time
    }
    if device_id is not None:
        device['_id'] = device_id
    result = db.devices.insert_one(device)
    if '_id' not in device:
        device['_id'] = result.inserted_id
    return device

def get_device(device_id):
    return db.devices.find_one({'_id': device_id})

def get_all_devices():
    return list(db.devices.find())

def get_devices_by_type(device_type_id):
    return list(db.devices.find({'device_type_id': device_type_id}))

def get_devices_by_user(user_id):
    return list(db.devices.find({'user_id': user_id}))

def update_device_status(device_id, status):
    result = db.devices.update_one(
        {'_id': device_id},
        {'$set': {'status': status, 'last_updated': get_vietnam_time()}}
    )
    return result.matched_count > 0

# Sensor data 
def create_sensor_data(sensorData_id=None, value=None, device_id=None):
    sensor_data = {
        'value': value,
        'timestamp': get_vietnam_time(),
        'device_id': device_id  # Foreign key to Device
    }
    if sensorData_id is not None:
        sensor_data['_id'] = sensorData_id
    result = db.sensor_data.insert_one(sensor_data)
    if '_id' not in sensor_data:
        sensor_data['_id'] = result.inserted_id
    return sensor_data 

def get_sensor_data_by_device(device_id):
    return list(db.sensor_data.find({'device_id': device_id}))

def get_sensor_data_by_legacy_sensor_id(sensor_id):
    # Backward-compat shim if any old code still queries by sensor_id
    return list(db.sensor_data.find({'sensor_id': sensor_id}))

# Device type (thay thế Sensor type)
def create_device_type(name, unit=None, role=None, device_type_id=None):
    """
    Tạo loại thiết bị theo ERD
    role: 0=sensor, 1=actuator
    """
    device_type = {
        'name': name,
        'unit': unit,
        'role': role  # 0=sensor, 1=actuator
    }
    if device_type_id is not None:
        device_type['_id'] = device_type_id
        db.device_types.replace_one({'_id': device_type_id}, device_type, upsert=True)
        return db.device_types.find_one({'_id': device_type_id})
    else:
        result = db.device_types.insert_one(device_type)
        device_type['_id'] = result.inserted_id
        return device_type

def get_device_types_by_role(role):
    """Lấy tất cả device types theo role (0=sensor, 1=actuator)"""
    return list(db.device_types.find({'role': role}))

def get_all_device_types():
    """Lấy tất cả device types"""
    return list(db.device_types.find())

# Action logging
def create_action(action_id=None, device_id=None, user_id=None, device_name=None, action_type=None, description=None, timestamp=None):
    if timestamp is None:
        timestamp = get_vietnam_time()
    
    # If device_name is not provided, get it from device_id
    if device_name is None and device_id:
        device = db.devices.find_one({'_id': device_id})
        device_name = device.get('name') if device else None
    
    action = {
        'device_id': device_id,  # Foreign key to Device
        'user_id': user_id,      # Foreign key to User
        'device_name': device_name,
        'action_type': action_type,
        'description': description,
        'timestamp': timestamp
    }
    if action_id is not None:
        action['_id'] = action_id
    result = db.actions.insert_one(action)
    if '_id' not in action:
        action['_id'] = result.inserted_id
    return action

def get_recent_actions(limit=10):
    return list(db.actions.find().sort('timestamp', -1).limit(limit))

def get_actions_by_device(device_id):
    return list(db.actions.find({'device_id': device_id}).sort('timestamp', -1))

def get_actions_by_user(user_id):
    return list(db.actions.find({'user_id': user_id}).sort('timestamp', -1))


# Sensor data with enhanced functionality
# Hàm này để nhận dữ liệu trực tiếp từ esp 
def create_sensor_reading(temperature, humidity, light, timestamp=None):
    if timestamp is None:
        # Sử dụng thời gian Việt Nam (UTC+7)
        timestamp = get_vietnam_time()
    
    reading = {
        'temperature': temperature,
        'humidity': humidity,
        'light': light,
        'timestamp': timestamp
    }
    db.sensor_data.insert_one(reading)
    return reading

def get_latest_sensor_data():
    return db.sensor_data.find_one(sort=[('timestamp', -1)])

def get_sensor_data_range(start_time, end_time):
    return list(db.sensor_data.find({
        'timestamp': {'$gte': start_time, '$lte': end_time}
    }).sort('timestamp', 1))
