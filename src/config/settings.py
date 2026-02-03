"""Configuration settings for RAG Visualizer"""

import os
from pathlib import Path

# Embedding model options (only 2: local fast vs cloud)
MODEL_OPTIONS = {
    "all-MiniLM-L6-v2 (Fast)": "sentence-transformers/all-MiniLM-L6-v2",
    "OpenAI text-embedding-3-small (Cloud)": "openai:text-embedding-3-small",
}

# Get the project root directory (assuming settings.py is in src/config/)
PROJECT_ROOT = Path(__file__).parent.parent.parent
DATA_DIR = PROJECT_ROOT / "data"

# Load sample text from data directory
def load_sample_text(filename: str) -> str:
    """Load sample text from data directory
    
    Args:
        filename: Name of the text file in data directory
        
    Returns:
        Content of the file as string
    """
    file_path = DATA_DIR / filename
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return f.read()
    except FileNotFoundError:
        return f"Error: File {filename} not found in data directory."
    except Exception as e:
        return f"Error loading {filename}: {str(e)}"


# Sample texts loaded from files
SAMPLE_TEXTS = {
    "AI & Machine Learning": load_sample_text("AI_Machine_Learning.txt"),
    "Climate & Environment": load_sample_text("Climate_Environment.txt"),
    "Space Exploration": load_sample_text("Space_Exploration.txt"),
    "Elon Musk Biography": load_sample_text("Elon_Musk_Overview.txt"),
    "LangGraph Framework": load_sample_text("LangGraph_Overview.txt")
}

# Default values for the RAG pipeline
DEFAULT_CHUNK_SIZE = 100
DEFAULT_OVERLAP = 20
DEFAULT_COLLECTION_NAME = "rag_embeddings"
DEFAULT_N_RESULTS = 3
DEFAULT_REDUCTION_METHOD = "PCA"

# LLM related defaults
DEFAULT_MODEL = "gpt-4.1-nano"
DEFAULT_TEMPERATURE = 0.2
DEFAULT_SYSTEM_PROMPT = """
You are a helpful assistant that can answer questions about the provided text.
You are given a question and a context.
You need to answer the question based on the context.
"""