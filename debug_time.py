from database.connection import db
from datetime import datetime
import pytz

VN_TZ = pytz.timezone('Asia/Ho_Chi_Minh')

# Get latest action
action = db.actions.find_one({}, sort=[('timestamp', -1)])
print('Latest action timestamp:', action['timestamp'])
print('Type:', type(action['timestamp']))

# Check if it has timezone info
if hasattr(action['timestamp'], 'tzinfo') and action['timestamp'].tzinfo:
    print('Has timezone:', action['timestamp'].tzinfo)
    # Convert to VN timezone for display
    vn_time = action['timestamp'].astimezone(VN_TZ)
    print('VN time:', vn_time.strftime('%H:%M:%S %d/%m/%Y'))
else:
    print('No timezone info')
    print('As is:', action['timestamp'].strftime('%H:%M:%S %d/%m/%Y'))