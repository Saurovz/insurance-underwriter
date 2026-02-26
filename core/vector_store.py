"""
ChromaDB vector store — persistent, domain-aware.
Collection naming: {domain}_{list_type}  e.g. books_liked, books_wishlist
"""
import uuid
from datetime import datetime
import chromadb
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from config import settings
from core.embeddings import embed

_client = None
LIST_TYPES = ["liked", "disliked", "wishlist", "not_interested"]


def _get_client() -> chromadb.PersistentClient:
    global _client
    if _client is None:
        _client = chromadb.PersistentClient(path=settings.CHROMA_PERSIST_DIR)
    return _client


def _get_collection(domain: str, list_type: str):
    return _get_client().get_or_create_collection(
        name=f"{domain}_{list_type}",
        metadata={"hnsw:space": "cosine"},   # cosine similarity
    )


# ── WRITE ─────────────────────────────────────────────────────────────────────
def add_item(domain: str, list_type: str, item_name: str, comment: str = "") -> str:
    """
    Embed and store an item in the correct collection.
    Document format: "Atomic Habits | liked | great for building habits"
    """
    if list_type not in LIST_TYPES:
        return f"❌ Invalid list_type: {list_type}. Choose from {LIST_TYPES}"

    document  = f"{item_name} | {list_type} | {comment}"
    embedding = embed(document)

    _get_collection(domain, list_type).add(
        ids        = [str(uuid.uuid4())],
        documents  = [document],
        embeddings = [embedding],
        metadatas  = [{
            "item_name" : item_name,
            "list_type" : list_type,
            "domain"    : domain,
            "comment"   : comment,
            "timestamp" : datetime.now().isoformat(),
        }],
    )
    return f"✅ '{item_name}' added to your {list_type} list."


# ── READ: vector search ───────────────────────────────────────────────────────
def search_preferences(domain: str, query: str, top_k: int = 5) -> list:
    """
    Semantic search across ALL list types for a domain.
    Returns top_k most relevant items sorted by cosine similarity.
    """
    query_embedding = embed(query)
    results = []

    for list_type in LIST_TYPES:
        col = _get_collection(domain, list_type)
        if col.count() == 0:
            continue
        res = col.query(
            query_embeddings = [query_embedding],
            n_results        = min(top_k, col.count()),
        )
        for doc, meta, dist in zip(
            res["documents"][0],
            res["metadatas"][0],
            res["distances"][0],
        ):
            results.append({"document": doc, "metadata": meta, "distance": dist})

    results.sort(key=lambda x: x["distance"])   # lower cosine distance = more similar
    return results[:top_k]


# ── READ: get full list ───────────────────────────────────────────────────────
def get_all_items(domain: str, list_type: str) -> list:
    """Return all metadata records from a given list."""
    col = _get_collection(domain, list_type)
    if col.count() == 0:
        return []
    return col.get()["metadatas"]
