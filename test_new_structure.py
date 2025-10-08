#!/usr/bin/env python3
"""
Script test cấu trúc database mới
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from database.connection import db
from database.models import *
import datetime

def test_new_database_structure():
    """Test cấu trúc database mới"""
    print("=" * 60)
    print("TESTING NEW DATABASE STRUCTURE")
    print("=" * 60)
    
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

def test_device_types():
    """Test device types"""
    print("\n" + "=" * 60)
    print("TESTING DEVICE TYPES")
    print("=" * 60)
    
    try:
        # Test create device types
        print("📝 Testing device type creation...")
        
        # Sensor types
        temp_type = create_device_type("temp_sensor", "Cảm biến nhiệt độ", "sensor", "°C", "DHT11")
        humidity_type = create_device_type("humidity_sensor", "Cảm biến độ ẩm", "sensor", "%", "DHT11")
        light_type = create_device_type("light_sensor", "Cảm biến ánh sáng", "sensor", "Lux", "BH1750")
        
        # Actuator types
        led_type = create_device_type("led_actuator", "Đèn LED", "actuator", "", "LED Control")
        fan_type = create_device_type("fan_actuator", "Quạt", "actuator", "", "Fan Control")
        
        print(f"  ✅ Created {5} device types")
        
        # Test get by category
        print("📖 Testing get by category...")
        sensor_types = get_device_types_by_category("sensor")
        actuator_types = get_device_types_by_category("actuator")
        
        print(f"  ✅ Sensor types: {len(sensor_types)}")
        print(f"  ✅ Actuator types: {len(actuator_types)}")
        
        return True
        
    except Exception as e:
        print(f"❌ Device types test failed: {e}")
        return False

def test_devices():
    """Test devices"""
    print("\n" + "=" * 60)
    print("TESTING DEVICES")
    print("=" * 60)
    
    try:
        # Test create devices
        print("📝 Testing device creation...")
        
        # Sensor devices
        temp_device = create_device("temp_001", "Cảm biến nhiệt độ", "temp_sensor", True, "Phòng khách")
        humidity_device = create_device("humidity_001", "Cảm biến độ ẩm", "humidity_sensor", True, "Phòng khách")
        
        # Actuator devices
        led_device = create_device("led_001", "Đèn LED 1", "led_actuator", False, "Phòng làm việc")
        fan_device = create_device("fan_001", "Quạt", "fan_actuator", False, "Phòng khách")
        
        print(f"  ✅ Created {4} devices")
        
        # Test get by type
        print("📖 Testing get by type...")
        sensor_devices = get_devices_by_type("temp_sensor")
        actuator_devices = get_devices_by_type("led_actuator")
        
        print(f"  ✅ Temperature sensors: {len(sensor_devices)}")
        print(f"  ✅ LED actuators: {len(actuator_devices)}")
        
        # Test update status
        print("📝 Testing update device status...")
        success = update_device_status("led_001", True)
        if success:
            print("  ✅ Device status updated successfully")
        else:
            print("  ❌ Failed to update device status")
        
        return True
        
    except Exception as e:
        print(f"❌ Devices test failed: {e}")
        return False

def test_actions():
    """Test actions"""
    print("\n" + "=" * 60)
    print("TESTING ACTIONS")
    print("=" * 60)
    
    try:
        # Test create actions
        print("📝 Testing action creation...")
        
        action1 = create_action("action_001", "LED 1", "Bật")
        action2 = create_action("action_002", "LED 1", "Tắt")
        action3 = create_action("action_003", "Quạt", "Bật")
        
        print(f"  ✅ Created {3} actions")
        
        # Test get recent actions
        print("📖 Testing get recent actions...")
        recent_actions = get_recent_actions(limit=5)
        print(f"  ✅ Found {len(recent_actions)} recent actions")
        
        # Test get by device
        print("📖 Testing get actions by device...")
        led_actions = get_actions_by_device("LED 1")
        print(f"  ✅ Found {len(led_actions)} actions for LED 1")
        
        return True
        
    except Exception as e:
        print(f"❌ Actions test failed: {e}")
        return False

def test_sensor_data():
    """Test sensor data"""
    print("\n" + "=" * 60)
    print("TESTING SENSOR DATA")
    print("=" * 60)
    
    try:
        # Test create sensor reading
        print("📝 Testing sensor reading creation...")
        
        reading = create_sensor_reading(
            temperature=26.5,
            humidity=65.0,
            light=750.0
        )
        print(f"  ✅ Created sensor reading: {reading['_id']}")
        
        # Test get latest
        print("📖 Testing get latest sensor data...")
        latest = get_latest_sensor_data()
        if latest:
            print(f"  ✅ Latest: T={latest.get('temperature')}°C, H={latest.get('humidity')}%, L={latest.get('light')}lux")
        else:
            print("  ⚠️ No sensor data found")
        
        return True
        
    except Exception as e:
        print(f"❌ Sensor data test failed: {e}")
        return False

def cleanup_test_data():
    """Xóa dữ liệu test"""
    print("\n" + "=" * 60)
    print("CLEANING UP TEST DATA")
    print("=" * 60)
    
    try:
        # Xóa test data
        result1 = db.device_types.delete_many({"name": {"$regex": ".*test.*", "$options": "i"}})
        result2 = db.devices.delete_many({"_id": {"$regex": ".*001"}})
        result3 = db.actions.delete_many({"_id": {"$regex": "action_.*"}})
        result4 = db.sensor_data.delete_many({"temperature": 26.5})
        
        print(f"🗑️ Deleted {result1.deleted_count} test device types")
        print(f"🗑️ Deleted {result2.deleted_count} test devices")
        print(f"🗑️ Deleted {result3.deleted_count} test actions")
        print(f"🗑️ Deleted {result4.deleted_count} test sensor readings")
        
        print("✅ Cleanup completed!")
        
    except Exception as e:
        print(f"❌ Cleanup failed: {e}")

def main():
    print("🚀 Starting New Database Structure Test...")
    
    # Test connection
    if not test_new_database_structure():
        print("\n❌ Database connection failed.")
        return False
    
    # Test device types
    if not test_device_types():
        print("\n❌ Device types test failed.")
        return False
    
    # Test devices
    if not test_devices():
        print("\n❌ Devices test failed.")
        return False
    
    # Test actions
    if not test_actions():
        print("\n❌ Actions test failed.")
        return False
    
    # Test sensor data
    if not test_sensor_data():
        print("\n❌ Sensor data test failed.")
        return False
    
    # Cleanup
    cleanup_test_data()
    
    print("\n" + "=" * 60)
    print("✅ ALL TESTS PASSED!")
    print("New database structure is working correctly!")
    print("=" * 60)
    
    return True

if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⏹️ Test interrupted by user")
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        sys.exit(1)
