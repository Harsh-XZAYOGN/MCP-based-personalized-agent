import faiss
import numpy as np
from model import get_embedding

# FAISS setup
dimension = 768  # Dimension of BERT embeddings
faiss_index = faiss.IndexFlatL2(dimension)  # L2 distance (Euclidean)
job_list = []  # Store job details for lookup after similarity search

def build_faiss_index(jobs):
    """
    Build a FAISS index from job descriptions
    
    Args:
        jobs: List of job dictionaries containing description field
    """
    global job_list
    job_list = jobs
    
    # Create embeddings for all job descriptions
    embeddings = np.vstack([get_embedding(job["description"]) for job in jobs])
    
    # Add vectors to the index
    faiss_index.add(embeddings)
    
    print(f"FAISS index built with {len(jobs)} job listings")
    return faiss_index

def search_similar_jobs(user_embedding, k=5):
    """
    Search for similar jobs given a user embedding
    
    Args:
        user_embedding: Numpy array of user preferences embedding
        k: Number of results to return
        
    Returns:
        List of tuples (distance, job_dict)
    """
    # Reshape to ensure correct dimensions
    if len(user_embedding.shape) == 1:
        user_embedding = user_embedding.reshape(1, -1)
        
    # Ensure type is float32 as required by FAISS
    user_embedding = user_embedding.astype(np.float32)
    
    # Search for similar vectors
    D, I = faiss_index.search(user_embedding, k)
    
    # Return job details with distances
    results = [(D[0][i], job_list[idx]) for i, idx in enumerate(I[0])]
    return results

def clear_index():
    """Reset the FAISS index and job list"""
    global faiss_index, job_list
    faiss_index = faiss.IndexFlatL2(dimension)
    job_list = []
