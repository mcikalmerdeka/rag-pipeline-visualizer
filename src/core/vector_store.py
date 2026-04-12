"""ChromaDB vector store operations"""

import chromadb
import tempfile
from typing import List, Dict, Any, Optional
from src.config import logger_vector


def create_chromadb_collection(collection_name: str = "rag_embeddings"):
    """Create or get ChromaDB collection

    Args:
        collection_name: Name of the collection to create

    Returns:
        ChromaDB collection instance
    """
    logger_vector.info(f"Creating ChromaDB collection: {collection_name}")

    # Use the new EphemeralClient for in-memory storage
    # or PersistentClient for disk storage
    client = chromadb.EphemeralClient()

    # Delete existing collection if it exists
    try:
        client.delete_collection(collection_name)
        logger_vector.debug(f"Deleted existing collection: {collection_name}")
    except:
        pass

    collection = client.create_collection(
        name=collection_name,
        metadata={"hnsw:space": "cosine"}
    )

    logger_vector.info(f"Successfully created collection: {collection_name}")
    return collection


def add_documents_with_metadata(
    collection,
    documents: List[str],
    embeddings: List[List[float]],
    metadatas: Optional[List[Dict[str, Any]]] = None
):
    """Add documents with metadata to the collection

    Args:
        collection: ChromaDB collection instance
        documents: List of document texts
        embeddings: List of embedding vectors
        metadatas: Optional list of metadata dictionaries for each document
    """
    logger_vector.info(f"Adding {len(documents)} documents to collection with metadata")

    if not documents:
        logger_vector.error("No documents to add")
        raise ValueError("No documents to add")

    # Create IDs for each document
    ids = [f"chunk_{i}" for i in range(len(documents))]

    # Add to collection with metadata
    collection.add(
        embeddings=embeddings,
        documents=documents,
        ids=ids,
        metadatas=metadatas if metadatas else None
    )

    logger_vector.info(f"Successfully added {len(documents)} documents with metadata")


def query_with_metadata(collection, query_embeddings, n_results: int = 3):
    """Query the collection and return results with metadata

    Args:
        collection: ChromaDB collection instance
        query_embeddings: List of query embedding vectors
        n_results: Number of results to return

    Returns:
        Dictionary with documents, distances, ids, and metadatas
    """
    logger_vector.info(f"Querying collection for {n_results} results")

    results = collection.query(
        query_embeddings=query_embeddings,
        n_results=n_results,
        include=["documents", "distances", "metadatas"]
    )

    logger_vector.info(f"Retrieved {len(results['documents'][0])} results with metadata")
    return results


def format_sources_for_display(query_results: Dict[str, Any]) -> List[Dict[str, Any]]:
    """Format query results into structured source information

    Args:
        query_results: Results from query_with_metadata containing documents, distances, ids, metadatas

    Returns:
        List of formatted source information grouped by filename with chunk details
    """
    if not query_results or not query_results.get('documents'):
        return []

    documents = query_results['documents'][0]
    distances = query_results['distances'][0]
    ids = query_results['ids'][0]
    metadatas = query_results.get('metadatas', [[]])[0] if query_results.get('metadatas') else [{}] * len(documents)

    # Group chunks by filename
    file_chunks = {}

    for i, (doc, distance, chunk_id, metadata) in enumerate(zip(documents, distances, ids, metadatas)):
        metadata = metadata or {}
        filename = metadata.get("filename", "Unknown file")
        file_type = metadata.get("file_type", "Document")

        if filename not in file_chunks:
            file_chunks[filename] = {
                "chunks": [],
                "file_type": file_type,
                "pages": set(),
                "sections": set()
            }

        # Calculate similarity
        similarity = 1 - distance

        # Add chunk with its content and metadata
        file_chunks[filename]["chunks"].append({
            "chunk_number": i + 1,
            "content": doc,
            "page_number": metadata.get("page_number"),
            "section_number": metadata.get("section_number"),
            "chunk_index": metadata.get("chunk_index"),
            "total_chunks": metadata.get("total_chunks"),
            "similarity": similarity,
            "chunk_id": chunk_id
        })

        # Track pages and sections
        if metadata.get("page_number"):
            file_chunks[filename]["pages"].add(metadata["page_number"])
        if metadata.get("section_number"):
            file_chunks[filename]["sections"].add(metadata["section_number"])

    # Format each source file with its chunks
    formatted = []
    for filename, data in file_chunks.items():
        source_data = {
            "filename": filename,
            "file_type": data["file_type"],
            "chunks_used": len(data["chunks"]),
            "chunks": data["chunks"]
        }

        # Add page range if available
        if data["pages"]:
            pages = sorted(data["pages"])
            source_data["page_range"] = f"Pages {min(pages)}-{max(pages)}"

        # Add sections if available
        if data["sections"]:
            sections = sorted(data["sections"])
            source_data["sections"] = f"Sections {min(sections)}-{max(sections)}"

        formatted.append(source_data)

    logger_vector.info(f"Formatted {len(formatted)} source files from query results")
    return formatted


def get_file_type_icon(file_type: str) -> str:
    """Get emoji icon based on file type

    Args:
        file_type: File type string (e.g., "PDF", "WORD", "IMAGE")

    Returns:
        Emoji icon for the file type
    """
    file_type = file_type.upper()
    if "PDF" in file_type:
        return "📑"
    elif "WORD" in file_type or "DOC" in file_type:
        return "📝"
    elif "IMAGE" in file_type:
        return "🖼️"
    elif "TEXT" in file_type or "TXT" in file_type:
        return "📄"
    else:
        return "📄"

