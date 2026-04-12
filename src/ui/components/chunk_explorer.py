"""Chunk explorer component"""

import streamlit as st
from src.core.vector_store import get_file_type_icon


def render_chunk_explorer():
    """Render the chunk explorer section for viewing individual chunks with metadata"""
    st.subheader("📋 Chunk Explorer")

    # Add informational box
    st.info(
        f"ℹ️ **Understanding Embeddings:** Each chunk has a **{st.session_state.embeddings.shape[1]}-dimensional** "
        f"embedding vector that captures its semantic meaning. The 3D visualization above uses **all {st.session_state.embeddings.shape[1]} dimensions** "
        f"(reduced via PCA/UMAP), not just the preview shown below. Dimensionality reduction preserves the most important "
        f"patterns so you can visualize high-dimensional relationships in 3D space."
    )

    chunk_idx = st.selectbox(
        "Select a chunk to view details:",
        range(len(st.session_state.chunks)),
        format_func=lambda x: f"Chunk {x}"
    )

    # Get metadata for this chunk
    metadatas = st.session_state.get('chunk_metadatas', [])
    chunk_metadata = metadatas[chunk_idx] if chunk_idx < len(metadatas) else {}

    col1, col2 = st.columns([2, 1])

    with col1:
        st.text_area("Chunk Content", st.session_state.chunks[chunk_idx], height=150)

    with col2:
        st.write("**Embedding Vector (first 10 dims):**")
        st.caption(f"Preview of {st.session_state.embeddings.shape[1]}D vector")
        embedding_preview = st.session_state.embeddings[chunk_idx][:10]
        for i, val in enumerate(embedding_preview):
            st.text(f"[{i}]: {val:.4f}")

        # Display metadata if available
        if chunk_metadata:
            st.divider()
            st.write("**📄 Source Metadata:**")

            filename = chunk_metadata.get('filename', 'Unknown')
            file_type = chunk_metadata.get('file_type', 'Document')
            icon = get_file_type_icon(file_type)

            st.markdown(f"{icon} **{filename}**")
            st.caption(f"Type: {file_type}")

            if chunk_metadata.get('chunk_index') is not None:
                chunk_num = chunk_metadata['chunk_index'] + 1
                total = chunk_metadata.get('total_chunks', '?')
                st.caption(f"Chunk: {chunk_num} of {total}")

            if chunk_metadata.get('page_number'):
                st.caption(f"Page: {chunk_metadata['page_number']}")

            if chunk_metadata.get('section_number'):
                st.caption(f"Section: {chunk_metadata['section_number']}")
