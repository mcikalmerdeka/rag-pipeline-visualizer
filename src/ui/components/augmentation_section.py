"""Augmentation section component - shows prompt construction with source information"""

import streamlit as st
from src.config import DEFAULT_SYSTEM_PROMPT
from src.core.vector_store import format_sources_for_display, get_file_type_icon


def render_augmentation_section():
    """Render the augmentation section showing prompt construction with detailed source info"""
    st.header("🔧 2. Augmentation")
    st.markdown("View how retrieved context is integrated into the prompt sent to the LLM")

    if not st.session_state.get('query_results'):
        st.info("👆 Perform a query in the Indexing & Retrieval section first to see augmentation")
        return

    st.divider()

    # System Prompt Section
    st.subheader("📋 System Prompt")
    st.markdown("*This instructs the LLM on how to behave and use the context*")

    # Allow custom system prompt (default from settings)
    default_system_prompt = DEFAULT_SYSTEM_PROMPT.strip()

    if 'custom_system_prompt' not in st.session_state:
        st.session_state.custom_system_prompt = default_system_prompt

    use_custom = st.checkbox("Customize system prompt", value=False)

    if use_custom:
        st.session_state.custom_system_prompt = st.text_area(
            "Edit system prompt:",
            value=st.session_state.custom_system_prompt,
            height=150,
            key="system_prompt_input"
        )
    else:
        st.code(default_system_prompt, language="text")
        st.session_state.custom_system_prompt = default_system_prompt

    st.divider()

    # Retrieved Context Section with Sources
    query_results = st.session_state.query_results
    documents = query_results['documents'][0]
    num_results = len(documents)

    st.subheader("📚 Retrieved Context")
    st.markdown(f"*{num_results} chunks retrieved from vector database*")

    # Format sources for display (grouped by file)
    sources = format_sources_for_display(query_results)

    # Display sources in an expander similar to reference project's "View Sources"
    with st.expander("📚 View Sources", expanded=True):
        st.markdown("**Retrieved from:**")

        for i, source in enumerate(sources, 1):
            filename = source.get("filename", "Unknown file")
            file_type = source.get("file_type", "Document")
            chunks_used = source.get("chunks_used", 0)

            # Get icon based on file type
            icon = get_file_type_icon(file_type)

            # Display source header
            st.markdown(f"**{i}.** {icon} `{filename}` ({file_type})")

            # Display page range if available (PDFs)
            if source.get("page_range"):
                st.markdown(f"   - 📄 {source['page_range']}")

            # Display section info if available (Word docs)
            if source.get("sections"):
                st.markdown(f"   - 📋 {source['sections']}")

            st.markdown(f"   - 🔢 Chunks used: {chunks_used}")

            # Display individual chunks with content in expanders
            if "chunks" in source and source["chunks"]:
                st.markdown("   **📄 Content:**")
                for chunk in source["chunks"]:
                    chunk_num = chunk.get("chunk_number", 0)
                    page_num = chunk.get("page_number")
                    section_num = chunk.get("section_number")
                    content = chunk.get("content", "")
                    similarity = chunk.get("similarity", 0)

                    # Build expander label
                    expander_label = f"      Chunk {chunk_num}"
                    if page_num:
                        expander_label += f" (Page {page_num})"
                    elif section_num:
                        expander_label += f" (Section {section_num})"

                    # Show content preview in label
                    content_preview = content[:60].replace("\n", " ") + "..." if len(content) > 60 else content
                    expander_label += f": {content_preview}"

                    with st.expander(expander_label, expanded=False):
                        st.markdown(f"```\n{content}\n```")
                        st.caption(f"Similarity: {similarity:.3f}")

            st.markdown("---")

    st.divider()

    # Augmented User Message Section
    st.subheader("💬 Augmented User Message")
    st.markdown("*This is the final message sent to the LLM (System Prompt + Context + Query)*")

    # Construct the augmented message
    query_text = st.session_state.get('last_query', '')

    # Get metadata for augmented message construction
    metadatas = query_results.get('metadatas', [[]])[0] if query_results.get('metadatas') else [{}] * len(documents)

    # Build context text with source attribution
    context_parts = []
    for i, (doc, metadata) in enumerate(zip(documents, metadatas)):
        metadata = metadata or {}
        source_info = f"[Source: {metadata.get('filename', 'Unknown')}, Chunk {metadata.get('chunk_index', i) + 1}]"
        context_parts.append(f"[Context {i+1}] {source_info}:\n{doc}")

    context_text = "\n\n".join(context_parts)

    augmented_message = f"""Context Information:
{'='*80}
{context_text}
{'='*80}

User Question: {query_text}

Please answer the question based on the context provided above."""

    # Store for generation
    st.session_state.augmented_prompt = {
        "system_prompt": st.session_state.custom_system_prompt,
        "user_message": augmented_message,
        "query": query_text,
        "num_contexts": len(documents),
        "sources": sources
    }

    # Display in code block for clarity
    with st.expander("View Full Augmented Prompt", expanded=False):
        st.code(augmented_message, language="text")

    # Show token estimate
    estimated_tokens = len(augmented_message.split()) + len(st.session_state.custom_system_prompt.split())
    st.caption(f"📊 Estimated tokens: ~{estimated_tokens * 1.3:.0f} (prompt)")

    st.divider()

    # Action button
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        if st.button("🚀 Proceed to Generation →", type="primary", use_container_width=True):
            st.session_state.ready_for_generation = True
            st.success("✅ Ready for generation! Scroll to Generation section below.")
