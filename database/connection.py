from pymongo import MongoClient
from config import Config
import logging

class Database:
    def __init__(self):
        try:
            self.client = MongoClient(Config.MONGO_URI)
            # Test connection
            self.client.admin.command('ping')
            print("✅ Connected to MongoDB successfully!")
            
            self.db = self.client['iotsystem']
            
            # Collections
            self.users = self.db['users']
            self.devices = self.db['devices']  # Thay thế sensors
            self.sensor_data = self.db['sensor_data']  # Giữ nguyên
            self.device_types = self.db['device_types']  # Thay thế sensor_types
            self.actions = self.db['actions']  # Giữ nguyên
            
            # Create indexes for better performance
            self._create_indexes()
            
        except Exception as e:
            print(f"❌ Failed to connect to MongoDB: {e}")
            raise e
        
    def _create_indexes(self):
        """Create database indexes for better performance"""
        try:
            # Index for sensor_data by timestamp
            self.sensor_data.create_index([("timestamp", -1)])
            # Index for actions by timestamp
            self.actions.create_index([("timestamp", -1)])
            # Index for users by username
            self.users.create_index([("username", 1)], unique=True)
            # Index for devices by device_type
            self.devices.create_index([("device_type", 1)])
            print("✅ Database indexes created successfully!")
        except Exception as e:
            print(f"⚠️ Warning: Could not create indexes: {e}")
        
    def get_collection(self, name):
        return self.db[name]
    
    def test_connection(self):
        """Test database connection"""
        try:
            self.client.admin.command('ping')
            return True
        except Exception as e:
            print(f"Database connection test failed: {e}")
            return False

# Global database instance
db = Database()
