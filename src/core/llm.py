"""LLM integration for RAG generation using LangChain OpenAI"""

import os
import streamlit as st
from typing import List, Dict, Optional
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain_core.messages import SystemMessage, HumanMessage

from src.config import DEFAULT_MODEL, DEFAULT_TEMPERATURE, DEFAULT_SYSTEM_PROMPT

# Load environment variables (for local development)
load_dotenv()


def get_api_key() -> Optional[str]:
    """Get OpenAI API key from environment or Streamlit secrets
    
    Supports both local .env files and Streamlit Cloud secrets
    
    Returns:
        API key if found, None otherwise
    """
    # Try Streamlit secrets first (for cloud deployment)
    try:
        return st.secrets["OPENAI_API_KEY"]
    except (KeyError, FileNotFoundError):
        # Fall back to environment variable (for local .env)
        return os.getenv("OPENAI_API_KEY")


def validate_api_key() -> None:
    """Validate that OpenAI API key is configured
    
    Raises:
        ValueError: If OPENAI_API_KEY is not found
    """
    if not get_api_key():
        raise ValueError("OPENAI_API_KEY not found in environment variables or Streamlit secrets")


def get_llm(model: str = None, temperature: float = None) -> ChatOpenAI:
    """Get LangChain ChatOpenAI instance
    
    Args:
        model: OpenAI model to use
        temperature: Temperature for generation
        
    Returns:
        Configured ChatOpenAI instance
    """
    if model is None:
        model = DEFAULT_MODEL
    if temperature is None:
        temperature = DEFAULT_TEMPERATURE
    api_key = get_api_key()
    if not api_key:
        raise ValueError("OPENAI_API_KEY not found in environment variables or Streamlit secrets")
    
    return ChatOpenAI(
        model=model,
        temperature=temperature,
        api_key=api_key,
        max_tokens=1000
    )


def construct_rag_prompt(query: str, retrieved_chunks: List[str], system_prompt: str = None) -> Dict[str, any]:
    """Construct augmented prompt with retrieved context
    
    Args:
        query: User query
        retrieved_chunks: List of retrieved text chunks
        system_prompt: Optional custom system prompt
        
    Returns:
        Dictionary with system_prompt, context, user_query, and full_prompt
    """
    if system_prompt is None:
        system_prompt = DEFAULT_SYSTEM_PROMPT.strip()
    
    # Format retrieved context
    context_text = "\n\n".join([
        f"[Context {i+1}]:\n{chunk}" 
        for i, chunk in enumerate(retrieved_chunks)
    ])
    
    # Construct full prompt
    user_message = f"""Context Information:
{'='*80}
{context_text}
{'='*80}

User Question: {query}

Please answer the question based on the context provided above."""
    
    return {
        "system_prompt": system_prompt,
        "context": context_text,
        "user_query": query,
        "full_user_message": user_message,
        "num_chunks": len(retrieved_chunks)
    }


def generate_response(query: str, retrieved_chunks: List[str], system_prompt: str = None, model: str = None) -> Dict[str, any]:
    """Generate response using LangChain OpenAI with retrieved context
    
    Args:
        query: User query
        retrieved_chunks: List of retrieved text chunks
        system_prompt: Optional custom system prompt
        model: OpenAI model to use
        
    Returns:
        Dictionary with prompt_data and response
    """
    if model is None:
        model = DEFAULT_MODEL
    llm = get_llm(model=model, temperature=DEFAULT_TEMPERATURE)
    
    # Construct augmented prompt
    prompt_data = construct_rag_prompt(query, retrieved_chunks, system_prompt)
    
    # Create LangChain messages
    messages = [
        SystemMessage(content=prompt_data["system_prompt"]),
        HumanMessage(content=prompt_data["full_user_message"])
    ]
    
    # Call LangChain OpenAI
    response = llm.invoke(messages)
    
    # Extract usage information from response metadata
    usage_metadata = response.response_metadata.get('token_usage', {})
    
    return {
        "prompt_data": prompt_data,
        "response": response.content,
        "model": model,
        "usage": {
            "prompt_tokens": usage_metadata.get('prompt_tokens', 0),
            "completion_tokens": usage_metadata.get('completion_tokens', 0),
            "total_tokens": usage_metadata.get('total_tokens', 0)
        }
    }

