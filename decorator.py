

from abc import ABC, abstractmethod
from typing import Any
from Classes.book import Book


"""
Class to add decorators for books. 
implements description decorator and cover image decorator
"""

class BookDecorator(ABC):
    """
    Abstract decorator that holds a reference to a 'Book' but does not
    inherit from the Book class.
    """
    def __init__(self, wrapped_book: Book):
        self._wrapped_book = wrapped_book

    @abstractmethod
    def getDetails(self) -> dict[str, Any]:
        """Must be implemented by concrete decorators."""
        pass



class DescriptionDecorator(BookDecorator):
    """
    Adds a 'description' field to a Book.
    """
    def __init__(self, wrapped_book: Book, description: str):
        super().__init__(wrapped_book)
        self.description = description

    def getDetails(self) -> dict[str, Any]:
        base_details = self._wrapped_book.getDetails()
        base_details.update(
            {
                "description": self.description
            })
        return base_details



class CoverDecorator(BookDecorator):
    """
    Adds a 'cover_image' field to a Book.
    """
    def __init__(self, wrapped_book: Book, cover_image: str):
        super().__init__(wrapped_book)
        self.cover_image = cover_image

    def getDetails(self) -> dict[str, Any]:
        base_details = self._wrapped_book.getDetails()
        base_details.update({"cover_image": self.cover_image})
        return base_details




