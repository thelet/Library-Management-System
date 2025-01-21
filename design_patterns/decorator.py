from abc import ABC, abstractmethod
from typing import Any, Dict
from Classes.book import Book


"""
Class to add decorators for books. 
implements description decorator and cover image decorator
"""

json_headers = ["id","type","decorator"]

class BookDecorator(ABC):
    """
    Abstract decorator that holds a reference to a 'Book' but does not
    inherit from the Book class.
    """
    def __init__(self, wrapped_book: Book):
        self._wrapped_book = wrapped_book
        self.id = int(self._wrapped_book.id)

    @abstractmethod
    def getDetails(self) -> Dict[str, Any]:
        """Must be implemented by concrete decorators."""
        pass

    @abstractmethod
    def to_json(self) -> Dict[str, Any]:
        """Must be implemented by concrete decorators."""
        pass

    def construct_base_json(self):
        base_json = {}
        wrapped_json = self._wrapped_book.to_json()
        for key in json_headers:
            if key in wrapped_json.keys():
                base_json.update({key : wrapped_json[key]})
            else:
                base_json.update({key : ""})
        return base_json


class DescriptionDecorator(BookDecorator):
    """
    Adds a 'description' field to a Book.
    """
    def __init__(self, wrapped_book: Book, description: str):
        super().__init__(wrapped_book)
        self.description = description

    def getDetails(self) -> Dict[str, Any]:
        base_details = self._wrapped_book.getDetails()
        base_details.update(
            {
                "description": self.description
            }
        )
        return base_details

    def to_json(self) -> Dict[str, Any]:
        base_json = self.construct_base_json()
        base_json["decorator"] += f"###{self.description}"
        base_json["type"] += f"###description"
        base_json["id"] = self.id
        return base_json


class CoverDecorator(BookDecorator):
    """
    Adds a 'cover_image' field to a Book.
    """
    def __init__(self, wrapped_book: Book, cover_image: str):
        super().__init__(wrapped_book)
        self.cover_image = cover_image

    def getDetails(self) -> Dict[str, Any]:
        base_details = self._wrapped_book.getDetails()
        base_details.update({"cover_image": self.cover_image})
        return base_details

    def to_json(self) -> Dict[str, Any]:
        base_json = self.construct_base_json()
        base_json["decorator"] += f"###{self.cover_image}"
        base_json["type"] += f"###cover_image"
        base_json["id"] = self.id
        return base_json


def main():
    # Create a book instance
    book1 = Book.createBook("aaa", "bbbb", 3333, "both", 4)

    # Decorate the book with a cover image
    img_d = CoverDecorator(book1, "cover.jpg")
    print("Cover Decorated Book Details:")
    print(img_d.getDetails())
    print("Cover Decorated Book JSON:")
    print(img_d.to_json())

    # Access 'id' from the instance

    # Decorate the already cover-decorated book with a description
    both_d = DescriptionDecorator(img_d, "An amazing journey through...")
    print("\nFully Decorated Book Details:")
    print(both_d.getDetails())
    print("Fully Decorated Book JSON:")
    print(both_d.to_json())

    type1 = img_d.to_json()["type"].split("###")[1]
    types = [typ for typ in both_d.to_json()["type"].split("###") if typ not in ["", " ", None]]
    print(f"type1: {type1}")
    print(f"types: {types}")


if __name__ == "__main__":
    main()
