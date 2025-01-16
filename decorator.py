

from abc import ABC, abstractmethod
from typing import Any
from Classes.book import Book

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
    




if __name__ == "__main__":
    import GUI.JSON_manager as JS_mng
    from GUI.JSON_manager import format_json_dict

    undecorated = Book("book", "The Good", 2000, "gener1", 3)
    print(f"\nundecorated book:\n {undecorated.getDetails()}\n")
    description_decorated = DescriptionDecorator(undecorated, "A book about the good things.")
    print(f"\ndecorated book:\n {description_decorated.getDetails()}\n")
    cover_decorated = CoverDecorator(undecorated, "https://example.com/cover.jpg")
    print(f"\ndecorated book:\n {cover_decorated.getDetails()}\n")
    all_decorated = CoverDecorator(description_decorated, "https://example.com/cover2.jpg")
    print(f"\ndecorated book:\n {all_decorated.getDetails()}\n")
    all_decorated_json = JS_mng.format_json_dict(all_decorated.getDetails())
    print(f"\ndecorated book json:\n {all_decorated_json}\n")



