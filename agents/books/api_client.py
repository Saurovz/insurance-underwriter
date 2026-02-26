"""
OpenLibrary API client — 100% free, no API key, no rate limits.
Docs: https://openlibrary.org/developers/api
"""
import requests

OPENLIBRARY_SEARCH = "https://openlibrary.org/search.json"
TIMEOUT = 10


def search_books(query: str, limit: int = 5) -> list:
    """
    Search OpenLibrary by any query (title, author, genre, topic).
    Returns a list of dicts with: title, author, year, subjects, rating.
    """
    params = {
        "q"      : query,
        "limit"  : limit,
        "fields" : "title,author_name,first_publish_year,subject,ratings_average,isbn",
    }
    try:
        resp = requests.get(OPENLIBRARY_SEARCH, params=params, timeout=TIMEOUT)
        resp.raise_for_status()
    except requests.RequestException as e:
        return [{"error": str(e)}]

    books = []
    for doc in resp.json().get("docs", []):
        books.append({
            "title"   : doc.get("title", "Unknown Title"),
            "author"  : ", ".join(doc.get("author_name", ["Unknown Author"])),
            "year"    : doc.get("first_publish_year", "N/A"),
            "subjects": doc.get("subject", [])[:5],          # top 5 subjects only
            "rating"  : doc.get("ratings_average", None),
        })
    return books


def format_books_for_llm(books: list) -> str:
    """Convert a list of book dicts into a readable string for the LLM prompt."""
    if not books:
        return "No books found."
    if "error" in books[0]:
        return f"OpenLibrary API error: {books[0]['error']}"

    lines = []
    for b in books:
        rating_str = f" | ⭐ {b['rating']:.1f}" if b["rating"] else ""
        subjects   = f" | Topics: {', '.join(b['subjects'])}" if b["subjects"] else ""
        lines.append(f"• '{b['title']}' by {b['author']} ({b['year']}){rating_str}{subjects}")
    return "\n".join(lines)
