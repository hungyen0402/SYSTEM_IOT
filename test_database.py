#!/usr/bin/env python3
"""
Script test kết nối database và khởi tạo collections
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from database.connection import db
from database.models import *
import datetime

def test_database_connection():
    """Test kết nối database"""
    print("=" * 50)
    print("TESTING DATABASE CONNECTION")
    print("=" * 50)
    
    try:
        # Test connection
        if db.test_connection():
            print("✅ Database connection: SUCCESS")
        else:
            print("❌ Database connection: FAILED")
            return False
            
        # Test collections
        collections = ['users', 'sensors', 'sensor_data', 'sensor_types', 'actions', 'devices']
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

def test_database_operations():
    """Test các thao tác database cơ bản"""
    print("\n" + "=" * 50)
    print("TESTING DATABASE OPERATIONS")
    print("=" * 50)
    
    try:
        # Test create sensor reading
        print("📝 Testing sensor data creation...")
        reading = create_sensor_reading(
            temperature=25.5,
            humidity=60.0,
            light=500.0
        )
        print(f"  ✅ Created sensor reading: {reading['_id']}")
        
        # Test create action
        print("📝 Testing action creation...")
        action = create_action(
            action_id=f"test_{int(datetime.datetime.now().timestamp())}",
            device_name="Test LED",
            action_type="Test Action"
        )
        print(f"  ✅ Created action: {action['_id']}")
        
        # Test create device
        print("📝 Testing device creation...")
        device = create_device(
            device_id="test_device_001",
            name="Test Device",
            device_type="test",
            status=True,
            location="Test Location"
        )
        print(f"  ✅ Created device: {device['_id']}")
        
        # Test get latest sensor data
        print("📖 Testing get latest sensor data...")
        latest = get_latest_sensor_data()
        if latest:
            print(f"  ✅ Latest sensor data: T={latest.get('temperature')}°C, H={latest.get('humidity')}%")
        else:
            print("  ⚠️ No sensor data found")
            
        # Test get recent actions
        print("📖 Testing get recent actions...")
        actions = get_recent_actions(limit=3)
        print(f"  ✅ Found {len(actions)} recent actions")
        
        # Test get all devices
        print("📖 Testing get all devices...")
        devices = get_all_devices()
        print(f"  ✅ Found {len(devices)} devices")
        
        return True
        
    except Exception as e:
        print(f"❌ Database operations test failed: {e}")
        return False

def cleanup_test_data():
    """Xóa dữ liệu test"""
    print("\n" + "=" * 50)
    print("CLEANING UP TEST DATA")
    print("=" * 50)
    
    try:
        # Xóa sensor data test (chỉ xóa những cái có temperature = 25.5)
        result1 = db.sensor_data.delete_many({"temperature": 25.5})
        print(f"🗑️ Deleted {result1.deleted_count} test sensor readings")
        
        # Xóa actions test
        result2 = db.actions.delete_many({"device_name": "Test LED"})
        print(f"🗑️ Deleted {result2.deleted_count} test actions")
        
        # Xóa devices test
        result3 = db.devices.delete_many({"_id": "test_device_001"})
        print(f"🗑️ Deleted {result3.deleted_count} test devices")
        
        print("✅ Cleanup completed!")
        
    except Exception as e:
        print(f"❌ Cleanup failed: {e}")

def main():
    print("🚀 Starting Database Test...")
    
    # Test connection
    if not test_database_connection():
        print("\n❌ Database connection failed. Please check MongoDB is running.")
        return False
    
    # Test operations
    if not test_database_operations():
        print("\n❌ Database operations failed.")
        return False
    
    # Cleanup
    cleanup_test_data()
    
    print("\n" + "=" * 50)
    print("✅ ALL TESTS PASSED!")
    print("Database is ready to use.")
    print("=" * 50)
    
    return True

if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⏹️ Test interrupted by user")
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        sys.exit(1)
