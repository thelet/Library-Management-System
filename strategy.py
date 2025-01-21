# strategy.py
from abc import ABC, abstractmethod
from typing import List, TYPE_CHECKING
from Classes.book import Book

if TYPE_CHECKING:
    from Classes.library import Library

class SearchStrategy(ABC):
    @abstractmethod
    def search(self, books: List[Book], criteria: str) -> tuple[List[Book], str]:
        """Search for books based on the given criteria."""
        pass

class SearchByTitle(SearchStrategy):
    def search(self, books: List[Book], criteria: str) -> tuple[List[Book],str]:
        results = [book for book in books if criteria.lower() in book.title.lower()]
        print(f"Search by Title '{criteria}': Found {len(results)} book(s).")
        return results, f"Search by Title '{criteria}': Found {len(results)} book(s)."

class SearchByAuthor(SearchStrategy):
    def search(self, books: List[Book], criteria: str) -> tuple[List[Book],str]:
        results = [book for book in books if criteria.lower() in book.author.lower()]
        print(f"Search by Author '{criteria}': Found {len(results)} book(s).")
        return results, f"Search by Author'{criteria}': Found {len(results)} book(s)."

class SearchByCategory(SearchStrategy):
    def search(self, books: List[Book], criteria: str) -> tuple[List[Book],str]:
        results = [book for book in books if criteria.lower() in book.category.lower()]
        print(f"Search by Category '{criteria}': Found {len(results)} book(s).")
        return results, f"Search by Category'{criteria}': Found {len(results)} book(s)."
