from pymongo import MongoClient
import os
MONGO_URI = os.environ.get("MONGO_URI")

client = None
db     = None

def get_db():
    global client, db
    if db is None:
        try:
            client = MongoClient(MONGO_URI, serverSelectionTimeoutMS=5000)
            client.server_info()  # test connection
            db = client['smarttrip']
            print("MongoDB connected successfully")
        except Exception as e:
            print(f"MongoDB connection error: {e}")
            db = None
    return db

def get_users_collection():
    database = get_db()
    if database is not None:
        return database['users']
    return None

def get_trips_collection():
    database = get_db()
    if database is not None:
        return database['trips']
    return None