import os
from dotenv import load_dotenv

load_dotenv()

# ── HuggingFace ──────────────────────────────────────────────────────────────
HF_API_TOKEN   = os.getenv("HF_API_TOKEN", "")
LLM_MODEL      = "mistralai/Mistral-7B-Instruct-v0.3"

HF_ROUTER_BASE = "https://router.huggingface.co/hf-inference/models"

# ── Embeddings (runs fully LOCAL, no API needed) ─────────────────────────────
EMBEDDING_MODEL = "sentence-transformers/all-MiniLM-L6-v2"

# ── ChromaDB (persistent on disk) ────────────────────────────────────────────
CHROMA_PERSIST_DIR = os.path.join(os.path.dirname(__file__), "..", "data", "chromadb")

# ── Whisper ───────────────────────────────────────────────────────────────────
WHISPER_MODEL = "tiny"          # CPU-friendly: tiny | base | small

# ── Agent ports ───────────────────────────────────────────────────────────────
BOOKS_AGENT_PORT   = 8001
# PRODUCTS_AGENT_PORT = 8002    # uncomment when adding products domain
# COURSES_AGENT_PORT  = 8003    # uncomment when adding courses domain

# ── Domain names ─────────────────────────────────────────────────────────────
DOMAIN_BOOKS    = "books"
DOMAIN_PRODUCTS = "products"
DOMAIN_COURSES  = "courses"
