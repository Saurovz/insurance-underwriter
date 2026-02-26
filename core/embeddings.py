"""
Embeddings module — loads all-MiniLM-L6-v2 ONCE and reuses it.
384-dimensional vectors. Runs 100% locally, no API cost.
"""
from sentence_transformers import SentenceTransformer
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from config import settings

_model = None

def get_model() -> SentenceTransformer:
    global _model
    if _model is None:
        _model = SentenceTransformer(settings.EMBEDDING_MODEL)
    return _model

def embed(text: str) -> list:
    """Convert a text string into a 384-dim embedding vector."""
    return get_model().encode(text, convert_to_numpy=True).tolist()
