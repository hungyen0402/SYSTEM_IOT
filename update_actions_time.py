from database.connection import db
from datetime import datetime, timedelta
import pytz
import random

VN_TZ = pytz.timezone('Asia/Ho_Chi_Minh')

# Update existing actions with correct VN timezone
print('Updating actions with correct VN timezone...')
actions = list(db.actions.find())
for i, action in enumerate(actions):
    # Create new timestamp with VN timezone (recent to old)
    new_timestamp = datetime.now(VN_TZ) - timedelta(minutes=i*3)
    
    db.actions.update_one(
        {'_id': action['_id']},
        {'$set': {'timestamp': new_timestamp}}
    )

print(f'Updated {len(actions)} actions with VN timezone')