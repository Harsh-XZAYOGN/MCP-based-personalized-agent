# config.py
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# API Keys
API_KEYS = {
    "anthropic": os.getenv("ANTHROPIC_API_KEY"),
    "jooble": os.getenv("JOOBLE_API_KEY", ""),
    "careerjet": os.getenv("CAREERJET_API_KEY", ""),
    # Add other API keys as needed
}

# MongoDB Configuration
MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017/")
MONGO_DB = os.getenv("MONGO_DB", "job_recommendations")
MONGO_COLLECTION = os.getenv("MONGO_COLLECTION", "user_context")

# FAISS Configuration
EMBEDDING_DIMENSION = 768
FAISS_SIMILARITY_THRESHOLD = 0.75

# API Endpoints
API_HOST = os.getenv("API_HOST", "http://127.0.0.1")
API_PORT = os.getenv("API_PORT", "8000")
API_BASE_URL = f"{API_HOST}:{API_PORT}"

# Streamlit Configuration
STREAMLIT_THEME = {
    "primaryColor": "#1E88E5",
    "backgroundColor": "#FFFFFF",
    "secondaryBackgroundColor": "#F8F9FA",
    "textColor": "#212121",
    "font": "sans-serif"
}
