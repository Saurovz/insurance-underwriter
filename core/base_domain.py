"""
BaseDomain — abstract contract every domain (books, products, courses) must follow.
The core engine ONLY depends on this interface, never on a specific domain.
"""
from abc import ABC, abstractmethod


class BaseDomain(ABC):

    @property
    @abstractmethod
    def domain_name(self) -> str:
        """Short identifier used as ChromaDB collection prefix. e.g. 'books'"""
        ...

    @abstractmethod
    def get_system_prompt(self) -> str:
        """Domain-specific personality + rules injected into the LLM prompt."""
        ...

    @abstractmethod
    def get_domain_tools(self) -> list:
        """
        Return a list of LangChain @tool functions specific to this domain.
        (e.g. search_book_api for books, search_product_api for products)
        The 6 base tools are added automatically by the agent engine.
        """
        ...

    @abstractmethod
    def format_item_for_embedding(self, item_name: str, list_type: str, comment: str) -> str:
        """
        How to stringify an item before embedding it.
        Books:    "Atomic Habits | liked | great for productivity"
        Products: "Sony WH-1000XM5 | liked | best noise cancellation"
        """
        ...
