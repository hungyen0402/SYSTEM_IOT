#!/usr/bin/env python3
"""
Script để chạy IoT System Dashboard
"""

import os
import sys
from app import app, socketio

def main():
    print("=" * 50)
    print("IoT System Dashboard")
    print("=" * 50)
    print("Starting server...")
    print("Dashboard: http://localhost:5000")
    print("Press Ctrl+C to stop")
    print("=" * 50)
    
    try:
        # Chạy ứng dụng với SocketIO
        socketio.run(app, debug=True, host='0.0.0.0', port=5000)
    except KeyboardInterrupt:
        print("\nShutting down server...")
        sys.exit(0)
    except Exception as e:
        print(f"Error starting server: {e}")
        sys.exit(1)

if __name__ == '__main__':
    main()
