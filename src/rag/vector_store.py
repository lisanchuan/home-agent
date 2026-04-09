"""Family Memory Center — Vector Store (ChromaDB)"""
import chromadb
from chromadb.config import Settings
from pathlib import Path
from typing import List, Dict, Optional, Any

# ChromaDB persist directory
CHROMA_DIR = Path(__file__).parent.parent.parent / "data" / "memory" / "chroma"

# Embedding model
EMBEDDING_MODEL = "text-embedding-3-small"
EMBEDDING_DIM = 384  # Compressed dimension


def get_chroma_client():
    """Get ChromaDB client"""
    CHROMA_DIR.mkdir(parents=True, exist_ok=True)
    return chromadb.Client(Settings(
        chroma_db_impl="duckdb+parquet",
        persist_directory=str(CHROMA_DIR),
        anonymized_telemetry=False
    ))


def get_collection(name: str = "family_memory"):
    """Get or create collection"""
    client = get_chroma_client()
    return client.get_or_create_collection(
        name=name,
        metadata={"description": "Family Memory Center semantic index"}
    )


def get_embedding(text: str) -> List[float]:
    """Get embedding for text using OpenAI API"""
    # Lazy import to avoid requiring API key if not used
    import openai
    import os
    
    api_key = os.environ.get("OPENAI_API_KEY")
    if not api_key:
        # Return dummy embedding for testing
        import hashlib
        h = int(hashlib.md5(text.encode()).hexdigest(), 16)
        return [((h >> (i * 4)) & 0xFFFF) / 32767 - 1 for i in range(EMBEDDING_DIM)]
    
    response = openai.Embedding.create(
        model=EMBEDDING_MODEL,
        input=text,
        dimensions=EMBEDDING_DIM
    )
    return response["data"][0]["embedding"]


def add_knowledge_vector(
    knowledge_id: str,
    content: str,
    metadata: Dict[str, Any]
):
    """Add knowledge to vector index"""
    collection = get_collection()
    
    embedding = get_embedding(content)
    vec_id = f"vec_{knowledge_id}"
    
    collection.add(
        embeddings=[embedding],
        documents=[content],
        metadatas=[metadata],
        ids=[vec_id]
    )


def search_vectors(
    query: str,
    n_results: int = 10,
    filter_metadata: Optional[Dict] = None
) -> List[Dict]:
    """Search vectors"""
    collection = get_collection()
    
    query_embedding = get_embedding(query)
    
    where = filter_metadata or {}
    
    results = collection.query(
        query_embeddings=[query_embedding],
        n_results=n_results,
        where=where if where else None,
        include=["documents", "metadatas", "distances"]
    )
    
    # Format results
    formatted = []
    if results["ids"] and results["ids"][0]:
        for i, vid in enumerate(results["ids"][0]):
            formatted.append({
                "vec_id": vid,
                "knowledge_id": results["metadatas"][0][i].get("knowledge_id", vid.replace("vec_", "")),
                "content": results["documents"][0][i],
                "metadata": results["metadatas"][0][i],
                "distance": results["distances"][0][i],
                "similarity": 1 - results["distances"][0][i]
            })
    
    return formatted


def delete_vector(vec_id: str):
    """Delete vector"""
    collection = get_collection()
    collection.delete(ids=[vec_id])


def rebuild_index(knowledge_list: List[Dict]):
    """Rebuild entire index"""
    client = get_chroma_client()
    
    # Delete existing collection
    try:
        client.delete_collection("family_memory")
    except:
        pass
    
    collection = client.get_or_create_collection(
        name="family_memory",
        metadata={"description": "Family Memory Center semantic index"}
    )
    
    if not knowledge_list:
        return
    
    # Add all knowledge
    embeddings = [get_embedding(k["content"]) for k in knowledge_list]
    ids = [f"vec_{k['id']}" for k in knowledge_list]
    documents = [k["content"] for k in knowledge_list]
    metadatas = [{
        "knowledge_id": k["id"],
        "type": k["type"],
        "category": k["category"],
        "visibility": k["visibility"],
        "owner_member_id": k.get("owner_member_id"),
        "confidence": k.get("confidence", 0.5)
    } for k in knowledge_list]
    
    collection.add(
        embeddings=embeddings,
        documents=documents,
        metadatas=metadatas,
        ids=ids
    )
