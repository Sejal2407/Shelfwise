import os
import certifi
from pymongo import MongoClient
from dotenv import load_dotenv
import cloudinary
import cloudinary.uploader

load_dotenv()

# Database Setup
try:
    client = MongoClient(os.getenv("MONGO_URI"), tlsCAFile=certifi.where())
    db = client.Shelfwise
    users_collection = db.users
    print("Connected to Database")
except Exception as e:
    print(f"Error connecting to Database: {e}")

# Cloudinary Setup
cloudinary.config(
    cloud_name=os.getenv("CLOUDINARY_CLOUD_NAME"),
    api_key=os.getenv("CLOUDINARY_API_KEY"),
    api_secret=os.getenv("CLOUDINARY_API_SECRET")
)