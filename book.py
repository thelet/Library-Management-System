# book.py
from typing import List
from observer import Subject, Observer

class Book(Subject):
    def __init__(self, title: str, author: str, year: int, category: str, copies: int):
        self.title = title
        self.author = author
        self.year = year
        self.category = category
        self.copies = copies
        self.isLoaned = False
        self.observers: List[Observer] = []
        self.borrow_count = 0  # To track popularity

    def getDetails(self) -> str:
        return f"'{self.title}' by {self.author}, {self.year} - {self.category} ({self.copies} copies available)"

    def updateCopies(self, count: int):
        previous_copies = self.copies
        self.copies += count
        print(f"Updated copies for '{self.title}': {previous_copies} -> {self.copies}")
        if previous_copies <= 0 and self.copies > 0:
            # Notify observers that the book is now available
            self.notifyObservers(f"Book '{self.title}' is now available for borrowing.")

    @staticmethod
    def createBook(title: str, author: str, year: int, category: str, copies: int) -> 'Book':
        if copies < 0:
            raise ValueError("Number of copies cannot be negative.")
        return Book(title, author, year, category, copies)

    # Subject interface methods
    def attach(self, observer: Observer):
        if observer not in self.observers:
            self.observers.append(observer)
            print(f"{observer.name} has subscribed to notifications for '{self.title}'.")

    def detach(self, observer: Observer):
        if observer in self.observers:
            self.observers.remove(observer)
            print(f"{observer.name} has unsubscribed from notifications for '{self.title}'.")

    def notifyObservers(self, notification: str):
        for observer in self.observers:
            observer.update(notification)
