from pymongo import MongoClient
from datetime import datetime
import uuid

# MongoDB Connection
client = MongoClient("mongodb://localhost:27017/")
db = client["sd3biot"]  
motion_events = db["motion_events"] 


def log_motion_event(motion_count, led_status):
    try:
        event = {
            "event_id": str(uuid.uuid4()), 
            "motion_count": motion_count,
            "led_status": led_status,
            "timestamp": datetime.now()
        }
        result = motion_events.insert_one(event)
        print(f"Inserted event ID: {result.inserted_id}") 
        return result
    except Exception as e:
        print(f"Error inserting event: {e}")  
        raise



def get_motion_events():
    return list(motion_events.find({}, {"_id": 0}))  


def get_filtered_events(led_status):
    return list(motion_events.find({"led_status": led_status}, {"_id": 0}))
