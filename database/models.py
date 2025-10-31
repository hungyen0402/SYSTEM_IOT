from database.connection import db
from werkzeug.security import generate_password_hash, check_password_hash
import pytz
from datetime import datetime, timedelta

# Lấy múi giờ Việt Nam
VN_TZ = pytz.timezone('Asia/Ho_Chi_Minh')

def get_vietnam_time():
    return datetime.now(VN_TZ)

# ---------------------------
# User helpers (example)
# ---------------------------
def create_user(user_id, username, password, role, email):
    # ...existing code... (if any), otherwise simple create
    password_hash = generate_password_hash(password)
    doc = {
        "user_id": user_id,
        "username": username,
        "password_hash": password_hash,
        "role": role,
        "email": email,
        "created_at": get_vietnam_time()
    }
    db.users.insert_one(doc)
    return doc

def get_user_by_name(username):
    return db.users.find_one({"username": username})

def check_user_password(user, password):
    if not user:
        return False
    return check_password_hash(user.get('password_hash', ''), password)

# ---------------------------
# Sensor & Device helpers
# ---------------------------
def create_sensor_reading(temperature=None, humidity=None, light=None, device_id=None):
    """
    Lưu reading. Chuẩn hóa timestamp: lưu ở UTC (aware).
    """
    try:
        vn_now = get_vietnam_time().replace(microsecond=0)
        # convert to UTC for storage
        utc_now = vn_now.astimezone(pytz.UTC)
        doc = {
            "device_id": device_id,
            "temperature": float(temperature) if temperature is not None else None,
            "humidity": float(humidity) if humidity is not None else None,
            "light": float(light) if light is not None else None,
            "timestamp": utc_now
        }
        db.sensor_data.insert_one(doc)
        return doc
    except Exception as e:
        print("Error create_sensor_reading:", e)
        return None

def update_device_status(device_id, status):
    """
    Cập nhật trạng thái device (ON/OFF). Tạo device nếu chưa tồn tại.
    """
    try:
        vn_now = get_vietnam_time().replace(microsecond=0)
        res = db.devices.update_one(
            {"device_id": device_id},
            {"$set": {"status": bool(status), "last_seen": vn_now}},
            upsert=True
        )
        return res
    except Exception as e:
        print("Error update_device_status:", e)
        return None

def create_action(action_id, device_id=None, device_name=None, action_type=None, user_id=None, auto_generated=False, description=None):
    """
    Ghi lịch sử hành động.
    - Chuẩn hóa action_type về 'Bật' / 'Tắt' nếu có thể.
    - Lưu timestamp ở UTC (timezone-aware).
    """
    try:
        # Normalize action_type input
        raw = (action_type or '').strip()
        raw_low = raw.lower()
        if raw_low in ('on', 'bật', 'bat', 'true', '1', 'turn_on', 'turnon'):
            norm = 'Bật'
        elif raw_low in ('off', 'tắt', 'tat', 'false', '0', 'turn_off', 'turnoff'):
            norm = 'Tắt'
        else:
            # If already Vietnamese 'Bật'/'Tắt' or unknown, keep as-is or mark 'Khác'
            if raw in ('Bật', 'Tắt'):
                norm = raw
            else:
                norm = raw or 'Khác'

        # VN now normalized then convert to UTC for storage
        vn_now = get_vietnam_time().replace(microsecond=0)
        utc_now = vn_now.astimezone(pytz.UTC)

        doc = {
            "action_id": action_id,
            "device_id": device_id,
            "device_name": device_name,
            "action_type": norm,
            "user_id": user_id,
            "auto_generated": bool(auto_generated),
            "description": description,
            "timestamp": utc_now
        }
        db.actions.insert_one(doc)
        return doc
    except Exception as e:
        print("Error create_action:", e)
        return None

def get_today_action_counts():
    """
    Trả về dict: { device_name: { 'Bật': count_on, 'Tắt': count_off } } cho ngày hiện tại theo múi giờ VN.
    - Tạo start/end theo VN, chuyển sang UTC để match với timestamps lưu ở DB (UTC).
    - Giữ chuẩn hóa action_type ('Bật'/'Tắt') và gom các dạng khác vào 'Khác'.
    """
    try:
        # VN local day boundaries
        vn_today = get_vietnam_time().date()
        start_vn = datetime.combine(vn_today, datetime.min.time()).replace(microsecond=0)
        end_vn = datetime.combine(vn_today, datetime.max.time()).replace(microsecond=0)
        start_vn = VN_TZ.localize(start_vn)
        end_vn = VN_TZ.localize(end_vn)

        # Convert to UTC for matching DB timestamps stored in UTC
        start_utc = start_vn.astimezone(pytz.UTC)
        end_utc = end_vn.astimezone(pytz.UTC)

        pipeline = [
            {"$match": {"timestamp": {"$gte": start_utc, "$lte": end_utc}}},
            {"$project": {
                "device_name": {"$ifNull": ["$device_name", "$device_id"]},
                "action_type": 1
            }},
            {"$group": {
                "_id": {"device_name": "$device_name", "action_type": "$action_type"},
                "count": {"$sum": 1}
            }}
        ]
        agg = list(db.actions.aggregate(pipeline))
        result = {}
        for item in agg:
            device = item['_id'].get('device_name') or 'Unknown'
            raw_action = (item['_id'].get('action_type') or '').strip()
            raw_low = raw_action.lower()
            # normalize possible variants
            if raw_low in ('on', 'bật', 'bat', 'true', '1'):
                action = 'Bật'
            elif raw_low in ('off', 'tắt', 'tat', 'false', '0'):
                action = 'Tắt'
            elif raw_action in ('Bật', 'Tắt'):
                action = raw_action
            else:
                action = 'Khác'

            cnt = item['count']
            if device not in result:
                result[device] = {"Bật": 0, "Tắt": 0}
            if action in ('Bật', 'Tắt'):
                result[device][action] = result[device].get(action, 0) + cnt
            else:
                result[device].setdefault('Khác', 0)
                result[device]['Khác'] += cnt
        return result
    except Exception as e:
        print("Error get_today_action_counts:", e)
        return {}

def get_latest_sensor_data():
    """
    Trả về document cảm biến mới nhất (most recent).
    - Nếu không có dữ liệu trả về {}
    - Chuyển timestamp sang múi giờ VN và thêm trường 'timestamp_vn' (ISO string)
    """
    try:
        doc = db.sensor_data.find_one(sort=[('timestamp', -1)])
        if not doc:
            return {}
        ts = doc.get('timestamp')
        if ts is not None:
            # Nếu timestamp naive giả định là UTC, chuẩn hóa thành timezone-aware
            if ts.tzinfo is None:
                ts = pytz.UTC.localize(ts)
            # Chuyển về VN timezone
            ts_vn = ts.astimezone(VN_TZ)
            # Lưu format dễ hiển thị
            doc['timestamp_vn'] = ts_vn.isoformat()
        return doc
    except Exception as e:
        print("Error get_latest_sensor_data:", e)
        return {}

def get_all_devices():
    """
    Trả về danh sách document devices từ DB.
    Thêm trường last_seen_vn (ISO string) nếu có last_seen.
    """
    try:
        docs = list(db.devices.find())
        for d in docs:
            ts = d.get('last_seen')
            if ts:
                # chuẩn hóa: nếu naive giả định UTC, chuyển về timezone-aware
                if ts.tzinfo is None:
                    ts = pytz.UTC.localize(ts)
                d['last_seen_vn'] = ts.astimezone(VN_TZ).isoformat()
        return docs
    except Exception as e:
        print("Error get_all_devices:", e)
        return []

def get_device_status_dict():
    """
    Trả về dict: { device_id: status } để tiện dùng trên dashboard.
    """
    try:
        devices = get_all_devices()
        return { d.get('device_id'): bool(d.get('status', False)) for d in devices if d.get('device_id') }
    except Exception as e:
        print("Error get_device_status_dict:", e)
        return {}
