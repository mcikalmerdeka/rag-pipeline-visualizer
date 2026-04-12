"""Query section component"""

import streamlit as st
from src.core.models import load_model
from src.core.vector_store import query_with_metadata


def render_query_section(model_name: str):
    """Render the query section for semantic search

    Args:
        model_name: Name of the model to use for query encoding
    """
    st.subheader("🔎 Query & Search")

    # Query input
    query_text = st.text_input(
        "Enter a query to find similar chunks:",
        placeholder="e.g., 'What is machine learning?'"
    )

    n_results = st.slider("Number of results", 1, 10, 3)

    query_button = st.button("Search Similar Chunks", use_container_width=True)

    # Display results
    if query_button and st.session_state.embeddings_generated:
        if not query_text.strip():
            st.warning("Please enter a query!")
        else:
            with st.spinner("Searching..."):
                model = load_model(model_name)
                query_embedding = model.encode([query_text])[0]

                # Query ChromaDB with metadata
                results = query_with_metadata(
                    collection=st.session_state.collection,
                    query_embeddings=[query_embedding.tolist()],
                    n_results=n_results
                )

                st.session_state.query_results = results
                st.session_state.query_embedding = query_embedding
                st.session_state.last_query = query_text

            st.success(f"✅ Found {len(results['documents'][0])} similar chunks! Proceed to Augmentation section below.")

            # Display results with metadata
            documents = results['documents'][0]
            distances = results['distances'][0]
            ids = results['ids'][0]
            metadatas = results.get('metadatas', [[]])[0] if results.get('metadatas') else [{}] * len(documents)

            for i, (doc, distance, chunk_id, metadata) in enumerate(zip(
                documents,
                distances,
                ids,
                metadatas
            )):
                similarity = 1 - distance
                metadata = metadata or {}

                # Build expander title with metadata info
                chunk_num = int(chunk_id.split('_')[1]) if '_' in chunk_id else i
                filename = metadata.get('filename', 'Unknown')

                title = f"Result {i+1} - Chunk {chunk_num} - Similarity: {similarity:.3f}"
                if filename != 'Unknown':
                    title += f" | 📄 {filename}"

                with st.expander(title):
                    st.write(doc)

                    # Show metadata in a more compact way
                    meta_info = []
                    if metadata.get('file_type'):
                        meta_info.append(f"Type: {metadata['file_type']}")
                    if metadata.get('chunk_index') is not None:
                        meta_info.append(f"Chunk: {metadata['chunk_index'] + 1}/{metadata.get('total_chunks', '?')}")

                    if meta_info:
                        st.caption(" | ".join(meta_info))
