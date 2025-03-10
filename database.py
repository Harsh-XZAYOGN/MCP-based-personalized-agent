from pymongo import MongoClient
import os

# Load MongoDB Connection String from Environment Variables
MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017")

# Initialize MongoDB Client
client = MongoClient(MONGO_URI)

# Access Database
db = client["personalized_agent"]

# Define Collections
users_collection = db["users"]
jobs_collection = db["jobs"]
chat_collection = db["chat_history"]

# Function to add a user
def add_user(user_data):
    users_collection.insert_one(user_data)

# Function to get user by ID
def get_user(user_id):
    return users_collection.find_one({"_id": user_id})

# Function to store chat message
def save_chat_message(user_id, message, role="user"):
    chat_collection.update_one(
        {"user_id": user_id},
        {"$push": {"chat": {"role": role, "message": message}}},
        upsert=True
    )

# Function to fetch chat history
def get_chat_history(user_id):
    chat = chat_collection.find_one({"user_id": user_id})
    return chat["chat"] if chat else []

