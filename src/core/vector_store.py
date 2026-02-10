"""ChromaDB vector store operations"""

import chromadb
import tempfile
from src.config import logger_vector


def create_chromadb_collection(collection_name: str = "rag_embeddings"):
    """Create or get ChromaDB collection
    
    Args:
        collection_name: Name of the collection to create
        
    Returns:
        ChromaDB collection instance
    """
    logger_vector.info(f"Creating ChromaDB collection: {collection_name}")
    
    # Use the new EphemeralClient for in-memory storage
    # or PersistentClient for disk storage
    client = chromadb.EphemeralClient()
    
    # Delete existing collection if it exists
    try:
        client.delete_collection(collection_name)
        logger_vector.debug(f"Deleted existing collection: {collection_name}")
    except:
        pass
    
    collection = client.create_collection(
        name=collection_name,
        metadata={"hnsw:space": "cosine"}
    )
    
    logger_vector.info(f"Successfully created collection: {collection_name}")
    return collection

