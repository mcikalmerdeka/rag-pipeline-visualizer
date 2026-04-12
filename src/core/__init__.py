"""Core functionality package"""

from .models import load_model
from .text_processing import chunk_text
from .vector_store import (
    create_chromadb_collection,
    add_documents_with_metadata,
    query_with_metadata,
    format_sources_for_display,
    get_file_type_icon
)
from .visualization import reduce_dimensions, create_3d_plot
from .session_state import initialize_session_state, reset_embeddings_state
from .llm import generate_response, construct_rag_prompt, validate_api_key
from .document_processor import (
    load_document_from_memory,
    get_supported_file_types,
    get_file_type_label,
    get_file_type
)

__all__ = [
    'load_model',
    'chunk_text',
    'create_chromadb_collection',
    'add_documents_with_metadata',
    'query_with_metadata',
    'format_sources_for_display',
    'get_file_type_icon',
    'reduce_dimensions',
    'create_3d_plot',
    'initialize_session_state',
    'reset_embeddings_state',
    'generate_response',
    'construct_rag_prompt',
    'validate_api_key',
    'load_document_from_memory',
    'get_supported_file_types',
    'get_file_type_label',
    'get_file_type'
]

