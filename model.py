from transformers import AutoTokenizer, AutoModel
import torch
import numpy as np
import os
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Set up model constants
MODEL_NAME = "bert-base-uncased"
MAX_LENGTH = 512
EMBEDDING_DIMENSION = 768

# Initialize tokenizer and model
try:
    tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)
    model = AutoModel.from_pretrained(MODEL_NAME)
    logger.info(f"Successfully loaded {MODEL_NAME} model and tokenizer")
except Exception as e:
    logger.error(f"Error loading model: {str(e)}")
    raise

def get_embedding(text, pooling_strategy="mean"):
    """
    Generate embeddings for the given text using BERT
    
    Args:
        text: Input text to generate embeddings for
        pooling_strategy: Method to combine token embeddings ('mean', 'cls', or 'max')
        
    Returns:
        numpy array of shape (EMBEDDING_DIMENSION,)
    """
    if not text or not isinstance(text, str):
        logger.warning(f"Invalid text input: {text}")
        # Return zero vector for invalid input
        return np.zeros(EMBEDDING_DIMENSION)
    
    # Truncate long text to prevent excessive processing
    if len(text) > 5000:
        text = text[:5000]
        
    # Tokenize the text
    try:
        inputs = tokenizer(
            text,
            return_tensors="pt",
            truncation=True,
            padding="max_length",
            max_length=MAX_LENGTH
        )
        
        # Generate embeddings
        with torch.no_grad():
            outputs = model(**inputs)
            
        # Get the hidden states
        hidden_states = outputs.last_hidden_state
        attention_mask = inputs["attention_mask"]
        
        # Apply pooling strategy
        if pooling_strategy == "cls":
            # Use [CLS] token embedding (first token)
            embeddings = hidden_states[:, 0, :].numpy()
        elif pooling_strategy == "max":
            # Max pooling
            input_mask_expanded = attention_mask.unsqueeze(-1).expand(hidden_states.size()).float()
            hidden_states[input_mask_expanded == 0] = -1e9  # Set padding tokens to large negative value
            embeddings = torch.max(hidden_states, 1)[0].numpy()
        else:  # Default to mean pooling
            # Mean pooling - take average of all token embeddings
            input_mask_expanded = attention_mask.unsqueeze(-1).expand(hidden_states.size()).float()
            sum_embeddings = torch.sum(hidden_states * input_mask_expanded, 1)
            sum_mask = torch.clamp(input_mask_expanded.sum(1), min=1e-9)
            embeddings = (sum_embeddings / sum_mask).numpy()
            
        return embeddings[0]  # Return the first (and only) embedding
        
    except Exception as e:
        logger.error(f"Error generating embedding: {str(e)}")
        return np.zeros(EMBEDDING_DIMENSION)  # Return zero vector on error

def batch_get_embeddings(texts, batch_size=32):
    """
    Generate embeddings for a batch of texts
    
    Args:
        texts: List of text strings
        batch_size: Number of texts to process in each batch
        
    Returns:
        numpy array of shape (len(texts), EMBEDDING_DIMENSION)
    """
    embeddings = []
    
    for i in range(0, len(texts), batch_size):
        batch = texts[i:i+batch_size]
        batch_embeddings = [get_embedding(text) for text in batch]
        embeddings.extend(batch_embeddings)
        
    return np.array(embeddings)

def calculate_similarity(embedding1, embedding2):
    """
    Calculate cosine similarity between two embeddings
    
    Args:
        embedding1: First embedding vector
        embedding2: Second embedding vector
        
    Returns:
        Similarity score between 0 and 1
    """
    if embedding1.shape != embedding2.shape:
        raise ValueError(f"Embedding dimensions don't match: {embedding1.shape} vs {embedding2.shape}")
        
    norm1 = np.linalg.norm(embedding1)
    norm2 = np.linalg.norm(embedding2)
    
    if norm1 == 0 or norm2 == 0:
        return 0  # Handle zero vectors
        
    return np.dot(embedding1, embedding2) / (norm1 * norm2)
