"""Input section component"""

import streamlit as st
from src.core.models import load_model
from src.core.text_processing import chunk_text
from src.core.vector_store import (
    create_chromadb_collection,
    add_documents_with_metadata
)
from src.core.document_processor import (
    load_document_from_memory,
    get_supported_file_types,
    get_file_type_label,
    get_file_type
)


def render_input_section(model_name: str, chunk_size: int, overlap: int, collection_name: str):
    """Render the input section for text upload and embedding generation

    Args:
        model_name: Name of the model to use
        chunk_size: Size of text chunks
        overlap: Overlap between chunks
        collection_name: Name of ChromaDB collection
    """
    st.subheader("📄 Input Text")

    # Initialize uploaded_file in session state if not present
    if 'current_uploaded_file' not in st.session_state:
        st.session_state.current_uploaded_file = None

    # Text input
    text_input = st.text_area(
        "Enter your text or upload a file:",
        value=st.session_state.get('sample_text', ''),
        height=300,
        placeholder="Paste your text here or upload a file below..."
    )

    # File upload with multi-format support
    supported_types = get_supported_file_types()
    uploaded_file = st.file_uploader(
        "Or upload a file (PDF, DOCX, TXT, or Image)",
        type=supported_types
    )

    # Track the uploaded file info for metadata
    if uploaded_file is not None:
        try:
            file_label = get_file_type_label(uploaded_file.name)
            text_input = load_document_from_memory(uploaded_file)
            st.success(f"✅ Loaded {len(text_input)} characters from {file_label}!")

            # Store file info in session state for metadata creation
            st.session_state.current_uploaded_file = {
                'name': uploaded_file.name,
                'file_type': get_file_type(uploaded_file.name).upper()
            }
        except Exception as e:
            st.error(f"❌ Error loading file: {str(e)}")
            st.session_state.current_uploaded_file = None
    elif text_input.strip() and not st.session_state.get('current_uploaded_file'):
        # Manual text input - mark as text type
        st.session_state.current_uploaded_file = {
            'name': 'manual_input.txt',
            'file_type': 'TEXT'
        }

    # Generate embeddings button
    if st.button("🚀 Generate Embeddings", type="primary", use_container_width=True):
        if not text_input.strip():
            st.error("Please enter some text first!")
        else:
            with st.spinner("Loading model and generating embeddings..."):
                # Load model
                model = load_model(model_name)

                # Chunk text
                chunks = chunk_text(text_input, chunk_size, overlap)
                st.session_state.chunks = chunks

                # Generate embeddings
                embeddings = model.encode(chunks, show_progress_bar=False)
                st.session_state.embeddings = embeddings

                # Create metadata for each chunk
                file_info = st.session_state.get('current_uploaded_file', {
                    'name': 'manual_input.txt',
                    'file_type': 'TEXT'
                })

                metadatas = []
                for i, chunk in enumerate(chunks):
                    metadata = {
                        "filename": file_info['name'],
                        "file_type": file_info['file_type'],
                        "chunk_index": i,
                        "total_chunks": len(chunks),
                        "source": file_info['name']
                    }
                    metadatas.append(metadata)

                st.session_state.chunk_metadatas = metadatas

                # Create ChromaDB collection
                collection = create_chromadb_collection(collection_name)

                # Add to ChromaDB with metadata
                add_documents_with_metadata(
                    collection=collection,
                    documents=chunks,
                    embeddings=embeddings.tolist(),
                    metadatas=metadatas
                )

                st.session_state.collection = collection
                st.session_state.embeddings_generated = True

                # Store document sources for display
                st.session_state.document_sources = [{
                    "filename": file_info['name'],
                    "file_type": file_info['file_type'],
                    "total_chunks": len(chunks)
                }]

            st.success(f"✅ Generated embeddings for {len(chunks)} chunks!")
