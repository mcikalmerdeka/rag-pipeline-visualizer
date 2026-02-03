"""Model loading and embedding generation (SentenceTransformers + OpenAI)"""

import numpy as np
import streamlit as st
from sentence_transformers import SentenceTransformer

from src.core.llm import get_api_key


def _is_openai_model(model_name: str) -> bool:
    return model_name.startswith("openai:")


def _openai_model_id(model_name: str) -> str:
    """e.g. 'openai:text-embedding-3-small' -> 'text-embedding-3-small'"""
    return model_name.split(":", 1)[1]


class _OpenAIEmbeddingWrapper:
    """Wrapper that exposes .encode(texts) for OpenAI embeddings API."""

    def __init__(self, model_id: str, api_key: str):
        self._model_id = model_id
        self._client = __import__("openai", fromlist=["OpenAI"]).OpenAI(api_key=api_key)

    def encode(self, texts: list[str], show_progress_bar: bool = False) -> np.ndarray:
        del show_progress_bar  # no-op for API
        if not texts:
            return np.zeros((0, 1536), dtype=np.float32)  # text-embedding-3-small dim
        response = self._client.embeddings.create(model=self._model_id, input=texts)
        # response.data order matches input order
        embeddings = [d.embedding for d in response.data]
        return np.array(embeddings, dtype=np.float32)


@st.cache_resource
def load_model(model_name: str):
    """Load embedding model: SentenceTransformer (local) or OpenAI (cloud)."""
    if _is_openai_model(model_name):
        api_key = get_api_key()
        if not api_key:
            raise ValueError(
                "OpenAI embedding model selected but OPENAI_API_KEY not set "
                "(environment or Streamlit secrets)."
            )
        return _OpenAIEmbeddingWrapper(_openai_model_id(model_name), api_key)
    return SentenceTransformer(model_name)
