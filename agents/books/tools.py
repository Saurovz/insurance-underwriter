"""
Books domain tools — 7 LangChain @tool functions.
6 base tools (add/search/get) + 1 domain-specific (search_book_api).
"""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", ".."))

from langchain.tools import tool
from core.vector_store import add_item, search_preferences as vs_search, get_all_items
from agents.books.api_client import search_books, format_books_for_llm

DOMAIN = "books"

# ── 6 Base Tools (same pattern for every domain) ─────────────────────────────

@tool
def add_to_liked(book_name: str, comment: str = "") -> str:
    """Add a book to the liked list. Call this when the user says they loved,
    enjoyed, finished, or really liked a book. Args: book_name (str), comment (str)."""
    return add_item(DOMAIN, "liked", book_name, comment)


@tool
def add_to_disliked(book_name: str, comment: str = "") -> str:
    """Add a book to the disliked list. Call this when the user says they
    did not like, hated, or abandoned a book. Args: book_name (str), comment (str)."""
    return add_item(DOMAIN, "disliked", book_name, comment)


@tool
def add_to_wishlist(book_name: str, comment: str = "") -> str:
    """Add a book to the wishlist. Call this when the user says they want to
    read a book in the future. Args: book_name (str), comment (str)."""
    return add_item(DOMAIN, "wishlist", book_name, comment)


@tool
def mark_not_interested(book_name: str, comment: str = "") -> str:
    """Mark a book as not interested. Call this when the user explicitly says
    they are not interested in a book. Args: book_name (str), comment (str)."""
    return add_item(DOMAIN, "not_interested", book_name, comment)


@tool
def search_preferences(query: str) -> str:
    """Search the user's personal reading history and preferences using semantic
    similarity. ALWAYS call this before making recommendations.
    Args: query (str) — topic, genre, or concept to search for."""
    results = vs_search(DOMAIN, query, top_k=5)
    if not results:
        return "No reading history found yet. Ask the user what genres they enjoy."
    lines = ["User's relevant reading history:"]
    for r in results:
        lines.append(f"  - {r['document']} (similarity score: {1 - r['distance']:.2f})")
    return "\n".join(lines)


@tool
def get_my_list(list_type: str) -> str:
    """Get all books in a specific list.
    Args: list_type (str) — must be one of: liked, disliked, wishlist, not_interested."""
    valid = ["liked", "disliked", "wishlist", "not_interested"]
    if list_type not in valid:
        return f"Invalid list_type. Choose from: {valid}"

    items = get_all_items(DOMAIN, list_type)
    if not items:
        return f"Your {list_type} list is empty."

    lines = [f"Your {list_type} books ({len(items)} total):"]
    for item in items:
        comment = f" — {item['comment']}" if item.get("comment") else ""
        lines.append(f"  • {item['item_name']}{comment}")
    return "\n".join(lines)


# ── 1 Domain-Specific Tool ───────────────────────────────────────────────────

@tool
def search_book_api(query: str) -> str:
    """Search OpenLibrary for books by title, author, genre, or topic.
    Use this to get real-time, accurate book details including ratings and subjects.
    Args: query (str) — book title, author name, or genre/topic."""
    books = search_books(query, limit=5)
    return format_books_for_llm(books)


# ── Exported list ─────────────────────────────────────────────────────────────
def get_all_tools() -> list:
    return [
        add_to_liked,
        add_to_disliked,
        add_to_wishlist,
        mark_not_interested,
        search_preferences,
        get_my_list,
        search_book_api,
    ]
