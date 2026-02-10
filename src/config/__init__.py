"""Configuration package"""

from .settings import (
    MODEL_OPTIONS,
    SAMPLE_TEXTS,
    DEFAULT_CHUNK_SIZE,
    DEFAULT_OVERLAP,
    DEFAULT_COLLECTION_NAME,
    DEFAULT_N_RESULTS,
    DEFAULT_REDUCTION_METHOD,
    DEFAULT_MODEL,
    DEFAULT_TEMPERATURE,
    DEFAULT_SYSTEM_PROMPT,
)
from .logging_config import (
    setup_logger,
    get_logger,
    logger_core,
    logger_vector,
    logger_llm,
    logger_text,
    logger_ui,
    logger_viz,
)

__all__ = [
    'MODEL_OPTIONS',
    'SAMPLE_TEXTS',
    'DEFAULT_CHUNK_SIZE',
    'DEFAULT_OVERLAP',
    'DEFAULT_COLLECTION_NAME',
    'DEFAULT_N_RESULTS',
    'DEFAULT_REDUCTION_METHOD',
    'DEFAULT_MODEL',
    'DEFAULT_TEMPERATURE',
    'DEFAULT_SYSTEM_PROMPT',
    'setup_logger',
    'get_logger',
    'logger_core',
    'logger_vector',
    'logger_llm',
    'logger_text',
    'logger_ui',
    'logger_viz',
]

