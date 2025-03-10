# main.py
from fastapi import FastAPI, Depends, HTTPException
from database import user_context_collection
from faiss_index import build_faiss_index, faiss_index, job_list
from job_fetcher import fetch_jobs_from_apis
from model import get_embedding
from context_manager import ContextManager
import numpy as np
import os
from typing import Dict, List

app = FastAPI()

# Initialize Jobs
jobs = fetch_jobs_from_apis()
build_faiss_index(jobs)

# Initialize Claude Context Manager
context_manager = ContextManager(api_key=os.environ.get("ANTHROPIC_API_KEY"))

@app.post("/save_user_context/")
async def save_user_context(user_id: str, preferences: str, skills: List[str] = None, 
                            experience: str = None, location: str = None):
    embedding = get_embedding(preferences)
    
    user_data = {
        "user_id": user_id,
        "preferences": preferences,
        "skills": skills or [],
        "experience": experience,
        "location": location,
        "embedding": embedding.tolist()
    }
    
    user_context_collection.update_one(
        {"user_id": user_id},
        {"$set": user_data},
        upsert=True
    )
    return {"message": "User context saved"}

@app.get("/recommendations/{user_id}")
async def get_recommendations(user_id: str):
    # Get user context
    user_data = user_context_collection.find_one({"user_id": user_id})
    if not user_data:
        raise HTTPException(status_code=404, detail="User context not found")

    # Get vector-based recommendations using FAISS
    user_embedding = np.array(user_data["embedding"]).astype(np.float32)
    D, I = faiss_index.search(user_embedding.reshape(1, -1), k=10)
    
    # Get the recommended jobs
    recommended_jobs = [job_list[i] for i in I[0]]
    
    # Enhance recommendations with Claude's context understanding
    enhanced_recommendations = context_manager.get_personalized_recommendations(
        user_context=user_data,
        job_listings=recommended_jobs
    )
    
    return enhanced_recommendations

# Run server: uvicorn main:app --reload
