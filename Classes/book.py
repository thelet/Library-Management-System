# book.py
import time
from typing import List, Any
from observer import Subject, Observer

class Book(Subject):
    book_id = 0
    book_ids = [0]
    def __init__(self, title: str, author: str, year: int, category: str, copies: int):
        self.id = Book.book_id
        self.title = title
        self.author = author
        self.year = year
        self.category = category
        self.copies = copies
        self.isLoaned = False
        self.user_observers: List['User'] = []
        self.borrow_count = 0  # To track popularity
        self.temp_followers = None

    def __str__(self):
        return (f'book id: {self.id} | title: {self.title} | author: {self.author} | year: {self.year} | category: {self.category}'
                f' | followers users ids: {[user.id for user in self.user_observers]}\n')

    def getDetails(self) -> str:
        return f"'{self.title}' by {self.author}, {self.year} - {self.category} ({self.copies} copies available)"

    def updateCopies(self, count: int):
        previous_copies = self.copies
        self.copies += count
        print(f"Updated copies for '{self.title}': {previous_copies} -> {self.copies}")
        if previous_copies <= 0 < self.copies:
            # Notify observers that the book is now available
            self.notifyObservers(f"{time.time()} | Book '{self.title}' is now available for borrowing.")

    @staticmethod
    def createBook(title: str, author: str, year: int, category: str, copies: int) -> 'Book':
        if copies < 0:
            raise ValueError("Number of copies cannot be negative.")
        while Book.book_id in Book.book_ids:
            Book.book_id += 1
        Book.book_ids.append(Book.book_id)
        return Book(title, author, year, category, copies)

    @staticmethod
    def loaded_book(title: str, author: str, year: int, category: str, copies: int, prev_id, followers_ids : List[int], borrow_count : int) -> 'Book':
        new_book =  Book(title, author, year, category, copies)
        new_book.set_id(prev_id)
        Book.book_ids.append(new_book.id)
        new_book.temp_followers = followers_ids
        new_book.borrow_count = borrow_count
        return new_book

    # Subject interface methods
    def attach(self, observer: Observer):
        if observer not in self.user_observers:
            self.user_observers.append(observer)
            print(f"{observer.name} has subscribed to notifications for '{self.title}'.")

    def detach(self, observer: Observer):
        if observer in self.user_observers:
            self.user_observers.remove(observer)
            print(f"{observer.name} has unsubscribed from notifications for '{self.title}'.")

    def notifyObservers(self, notification: str):
        for observer in self.user_observers:
            observer.update(notification)

    def to_json(self):
        from Classes.user import User

        observers_ids = [user.id for user in self.user_observers]

        return {
            "id": self.id,
            "title": self.title,
            "author": self.author,
            "year": self.year,
            "category": self.category,
            "copies": self.copies,
            "isLoaned": self.isLoaned,
            "borrow_count": self.borrow_count,
            "user_observers": observers_ids
        }

    @staticmethod
    def from_json(json: dict[str, Any]):
        return Book.loaded_book(title= json["title"], author= json["author"], category=json["category"],
                                copies=json["copies"], prev_id = json["id"], year=json["year"],
                                followers_ids=json["user_observers"],borrow_count=json["borrow_count"])


    def set_id(self, id: int):
        self.id = id

    def set_borrow_count(self, count: int):
        self.borrow_count = count



