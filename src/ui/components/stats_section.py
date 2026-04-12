"""Stats section component"""

import streamlit as st
from src.core.vector_store import get_file_type_icon


def render_stats_section(reduction_method: str):
    """Render statistics cards

    Args:
        reduction_method: The reduction method being used
    """
    # First row - basic stats
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.markdown(f"""
        <div class="stat-card">
            <p class="stat-number">{len(st.session_state.chunks)}</p>
            <p class="stat-label">Total Chunks</p>
        </div>
        """, unsafe_allow_html=True)

    with col2:
        st.markdown(f"""
        <div class="stat-card">
            <p class="stat-number">{st.session_state.embeddings.shape[1]}</p>
            <p class="stat-label">Embedding Dimensions</p>
        </div>
        """, unsafe_allow_html=True)

    with col3:
        st.markdown(f"""
        <div class="stat-card">
            <p class="stat-number">{reduction_method}</p>
            <p class="stat-label">Reduction Method</p>
        </div>
        """, unsafe_allow_html=True)

    with col4:
        st.markdown(f"""
        <div class="stat-card">
            <p class="stat-number">3D</p>
            <p class="stat-label">Visualization Space</p>
        </div>
        """, unsafe_allow_html=True)

    # Second row - document sources if available
    document_sources = st.session_state.get('document_sources', [])
    if document_sources:
        st.divider()
        st.caption("📄 **Document Sources:**")

        source_cols = st.columns(min(len(document_sources), 4))
        for i, source in enumerate(document_sources):
            with source_cols[i % 4]:
                filename = source.get('filename', 'Unknown')
                file_type = source.get('file_type', 'Document')
                total_chunks = source.get('total_chunks', 0)
                icon = get_file_type_icon(file_type)

                st.markdown(f"""
                <div style="
                    background-color: #f0f2f6;
                    border-radius: 8px;
                    padding: 10px;
                    margin: 5px 0;
                    border-left: 3px solid #ff4b4b;
                ">
                    <p style="margin: 0; font-size: 14px;">{icon} <strong>{filename}</strong></p>
                    <p style="margin: 2px 0 0 0; font-size: 12px; color: #666;">
                        {file_type} • {total_chunks} chunks
                    </p>
                </div>
                """, unsafe_allow_html=True)
