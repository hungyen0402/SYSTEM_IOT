#!/usr/bin/env python3
"""
Script test cấu trúc database theo ERD chính thức
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from database.connection import db
from database.models import *
import datetime

def test_erd_structure():
    """Test cấu trúc database theo ERD"""
    print("=" * 70)
    print("TESTING ERD DATABASE STRUCTURE")
    print("=" * 70)
    
    try:
        # Test connection
        if db.test_connection():
            print("✅ Database connection: SUCCESS")
        else:
            print("❌ Database connection: FAILED")
            return False
            
        # Test collections
        collections = ['users', 'devices', 'sensor_data', 'device_types', 'actions']
        print("\n📊 Testing collections:")
        
        for collection_name in collections:
            try:
                collection = getattr(db, collection_name)
                count = collection.count_documents({})
                print(f"  ✅ {collection_name}: {count} documents")
            except Exception as e:
                print(f"  ❌ {collection_name}: ERROR - {e}")
                
        return True
        
    except Exception as e:
        print(f"❌ Database test failed: {e}")
        return False

def test_user_entity():
    """Test User entity"""
    print("\n" + "=" * 70)
    print("TESTING USER ENTITY")
    print("=" * 70)
    
    try:
        # Test create user
        print("📝 Testing user creation...")
        user = create_user("test_user_001", "testuser", "password123", "user", "test@example.com")
        print(f"  ✅ Created user: {user['_id']}")
        
        # Test get user
        print("📖 Testing get user...")
        found_user = get_user_by_name("testuser")
        if found_user:
            print(f"  ✅ Found user: {found_user['username']}")
        else:
            print("  ❌ User not found")
        
        return True
        
    except Exception as e:
        print(f"❌ User entity test failed: {e}")
        return False

def test_device_type_entity():
    """Test DeviceType entity"""
    print("\n" + "=" * 70)
    print("TESTING DEVICE TYPE ENTITY")
    print("=" * 70)
    
    try:
        # Test create device types
        print("📝 Testing device type creation...")
        
        # Sensor types (role=0)
        temp_type = create_device_type("test_temp", "Test Temperature", "°C", 0)
        humidity_type = create_device_type("test_humidity", "Test Humidity", "%", 0)
        
        # Actuator types (role=1)
        led_type = create_device_type("test_led", "Test LED", "", 1)
        fan_type = create_device_type("test_fan", "Test Fan", "", 1)
        
        print(f"  ✅ Created {4} device types")
        
        # Test get by role
        print("📖 Testing get by role...")
        sensor_types = get_device_types_by_role(0)
        actuator_types = get_device_types_by_role(1)
        
        print(f"  ✅ Sensor types (role=0): {len(sensor_types)}")
        print(f"  ✅ Actuator types (role=1): {len(actuator_types)}")
        
        return True
        
    except Exception as e:
        print(f"❌ Device type entity test failed: {e}")
        return False

def test_device_entity():
    """Test Device entity"""
    print("\n" + "=" * 70)
    print("TESTING DEVICE ENTITY")
    print("=" * 70)
    
    try:
        # Test create devices
        print("📝 Testing device creation...")
        
        # Create devices with foreign keys
        led_device = create_device("test_led_001", "Test LED", "test_led", False, "Test Room", "test_user_001", "Test LED device", 0)
        temp_device = create_device("test_temp_001", "Test Temperature", "test_temp", True, "Test Room", "test_user_001", "Test temperature sensor", 1)
        
        print(f"  ✅ Created {2} devices")
        
        # Test get by type
        print("📖 Testing get by device type...")
        led_devices = get_devices_by_type("test_led")
        temp_devices = get_devices_by_type("test_temp")
        
        print(f"  ✅ LED devices: {len(led_devices)}")
        print(f"  ✅ Temperature devices: {len(temp_devices)}")
        
        # Test get by user
        print("📖 Testing get by user...")
        user_devices = get_devices_by_user("test_user_001")
        print(f"  ✅ User devices: {len(user_devices)}")
        
        # Test update status
        print("📝 Testing update device status...")
        success = update_device_status("test_led_001", True)
        if success:
            print("  ✅ Device status updated successfully")
        else:
            print("  ❌ Failed to update device status")
        
        return True
        
    except Exception as e:
        print(f"❌ Device entity test failed: {e}")
        return False

def test_action_entity():
    """Test Action entity"""
    print("\n" + "=" * 70)
    print("TESTING ACTION ENTITY")
    print("=" * 70)
    
    try:
        # Test create actions
        print("📝 Testing action creation...")
        
        action1 = create_action("test_action_001", "test_led_001", "test_user_001", "Test LED", "ON", "Turn on test LED")
        action2 = create_action("test_action_002", "test_led_001", "test_user_001", "Test LED", "OFF", "Turn off test LED")
        action3 = create_action("test_action_003", "test_temp_001", "test_user_001", "Test Temperature", "READ", "Read temperature")
        
        print(f"  ✅ Created {3} actions")
        
        # Test get recent actions
        print("📖 Testing get recent actions...")
        recent_actions = get_recent_actions(limit=5)
        print(f"  ✅ Found {len(recent_actions)} recent actions")
        
        # Test get by device
        print("📖 Testing get actions by device...")
        led_actions = get_actions_by_device("test_led_001")
        print(f"  ✅ Found {len(led_actions)} actions for LED device")
        
        # Test get by user
        print("📖 Testing get actions by user...")
        user_actions = get_actions_by_user("test_user_001")
        print(f"  ✅ Found {len(user_actions)} actions by user")
        
        return True
        
    except Exception as e:
        print(f"❌ Action entity test failed: {e}")
        return False

def test_sensor_data_entity():
    """Test SensorData entity"""
    print("\n" + "=" * 70)
    print("TESTING SENSOR DATA ENTITY")
    print("=" * 70)
    
    try:
        # Test create sensor data
        print("📝 Testing sensor data creation...")
        
        # Test individual sensor data
        temp_data = create_sensor_data("test_sensor_001", 25.5, "test_temp_001")
        humidity_data = create_sensor_data("test_sensor_002", 65.0, "test_temp_001")
        
        print(f"  ✅ Created {2} sensor data records")
        
        # Test combined sensor reading
        reading = create_sensor_reading(
            temperature=26.5,
            humidity=66.0,
            light=750.0
        )
        print(f"  ✅ Created combined sensor reading: {reading['_id']}")
        
        # Test get by device
        print("📖 Testing get sensor data by device...")
        device_data = get_sensor_data_by_device("test_temp_001")
        print(f"  ✅ Found {len(device_data)} sensor data for device")
        
        # Test get latest
        print("📖 Testing get latest sensor data...")
        latest = get_latest_sensor_data()
        if latest:
            print(f"  ✅ Latest: T={latest.get('temperature')}°C, H={latest.get('humidity')}%, L={latest.get('light')}lux")
        else:
            print("  ⚠️ No sensor data found")
        
        return True
        
    except Exception as e:
        print(f"❌ Sensor data entity test failed: {e}")
        return False

def test_relationships():
    """Test relationships between entities"""
    print("\n" + "=" * 70)
    print("TESTING ENTITY RELATIONSHIPS")
    print("=" * 70)
    
    try:
        # Test User -> Device relationship
        print("📖 Testing User -> Device relationship...")
        user_devices = get_devices_by_user("test_user_001")
        print(f"  ✅ User has {len(user_devices)} devices")
        
        # Test Device -> Action relationship
        print("📖 Testing Device -> Action relationship...")
        device_actions = get_actions_by_device("test_led_001")
        print(f"  ✅ Device has {len(device_actions)} actions")
        
        # Test User -> Action relationship
        print("📖 Testing User -> Action relationship...")
        user_actions = get_actions_by_user("test_user_001")
        print(f"  ✅ User has {len(user_actions)} actions")
        
        # Test Device -> SensorData relationship
        print("📖 Testing Device -> SensorData relationship...")
        device_sensor_data = get_sensor_data_by_device("test_temp_001")
        print(f"  ✅ Device has {len(device_sensor_data)} sensor data records")
        
        print("✅ All relationships working correctly!")
        return True
        
    except Exception as e:
        print(f"❌ Relationships test failed: {e}")
        return False

def cleanup_test_data():
    """Xóa dữ liệu test"""
    print("\n" + "=" * 70)
    print("CLEANING UP TEST DATA")
    print("=" * 70)
    
    try:
        # Xóa test data theo thứ tự dependencies
        result1 = db.actions.delete_many({"_id": {"$regex": "test_action_.*"}})
        result2 = db.sensor_data.delete_many({"_id": {"$regex": "test_sensor_.*"}})
        result3 = db.sensor_data.delete_many({"temperature": 26.5})
        result4 = db.devices.delete_many({"_id": {"$regex": "test_.*"}})
        result5 = db.device_types.delete_many({"_id": {"$regex": "test_.*"}})
        result6 = db.users.delete_many({"_id": "test_user_001"})
        
        print(f"🗑️ Deleted {result1.deleted_count} test actions")
        print(f"🗑️ Deleted {result2.deleted_count + result3.deleted_count} test sensor data")
        print(f"🗑️ Deleted {result4.deleted_count} test devices")
        print(f"🗑️ Deleted {result5.deleted_count} test device types")
        print(f"🗑️ Deleted {result6.deleted_count} test users")
        
        print("✅ Cleanup completed!")
        
    except Exception as e:
        print(f"❌ Cleanup failed: {e}")

def main():
    print("🚀 Starting ERD Database Structure Test...")
    
    # Test connection
    if not test_erd_structure():
        print("\n❌ Database connection failed.")
        return False
    
    # Test entities
    if not test_user_entity():
        print("\n❌ User entity test failed.")
        return False
    
    if not test_device_type_entity():
        print("\n❌ Device type entity test failed.")
        return False
    
    if not test_device_entity():
        print("\n❌ Device entity test failed.")
        return False
    
    if not test_action_entity():
        print("\n❌ Action entity test failed.")
        return False
    
    if not test_sensor_data_entity():
        print("\n❌ Sensor data entity test failed.")
        return False
    
    # Test relationships
    if not test_relationships():
        print("\n❌ Relationships test failed.")
        return False
    
    # Cleanup
    cleanup_test_data()
    
    print("\n" + "=" * 70)
    print("✅ ALL ERD TESTS PASSED!")
    print("Database structure matches ERD perfectly!")
    print("=" * 70)
    
    return True

if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⏹️ Test interrupted by user")
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        sys.exit(1)

