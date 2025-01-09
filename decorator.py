# decorator.py
from abc import ABC, abstractmethod
from Classes.book import Book

class BookDecorator(ABC, Book):
    def __init__(self, book: Book):
        self.book = book

    @abstractmethod
    def getDetails(self) -> str:
        pass

class ExtendedBookInfo(BookDecorator):
    def __init__(self, book: Book):
        super().__init__(book)
        self.additional_info = ""

    def addAdditionalInfo(self, info: str):
        self.additional_info += info + " "

    def getDetails(self) -> str:
        base_details = self.book.getDetails()
        return f"{base_details} Additional Info: {self.additional_info.strip()}"
