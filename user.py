# user.py
from typing import List
from observer import Observer, Subject
from book import Book

class User(Observer, Subject):
    def __init__(self, username: str, passwordHash: str, permissions: List[str]):
        self.username = username
        self.passwordHash = passwordHash
        self.permissions = permissions
        self.borrowedBooks: List[Book] = []
        self.observers: List[Observer] = []

    @property
    def name(self) -> str:
        return self.username

    def register(self, password: str):
        # Registration logic (e.g., hashing password, storing user data)
        print(f"{self.username} has registered.")
        self.notifyObservers(f"User registered: {self.username}")

    def login(self, password: str) -> bool:
        # Login logic (e.g., verifying password)
        print(f"{self.username} has logged in.")
        self.notifyObservers(f"User logged in: {self.username}")
        return True  # Placeholder for actual authentication

    def borrowBook(self, book: Book):
        if book.copies > 0:
            book.updateCopies(-1)
            self.borrowedBooks.append(book)
            # Attach to the book to receive notifications
            book.attach(self)
            from library import Library  # Import inside method to prevent circular import
            library = Library.getInstance()
            library.notifyObservers(f"{self.username} borrowed '{book.title}'.")
            print(f"{self.username} borrowed '{book.title}'.")
            book.borrow_count += 1  # Increment borrow count
        else:
            print(f"No copies available for '{book.title}'. {self.username} can subscribe for notifications.")
            # Automatically subscribe to notifications for availability
            book.attach(self)

    def returnBook(self, book: Book):
        if book in self.borrowedBooks:
            book.updateCopies(1)
            self.borrowedBooks.remove(book)
            # Detach from the book
            book.detach(self)
            from library import Library  # Import inside method to prevent circular import
            library = Library.getInstance()
            library.notifyObservers(f"{self.username} returned '{book.title}'.")
            print(f"{self.username} returned '{book.title}'.")
        else:
            print(f"{self.username} does not have '{book.title}' borrowed.")

    def update(self, notification: str):
        print(f"Notification for {self.username}: {notification}")
        # Optionally, display notification in GUI
        # This requires further integration with the GUI

    # Subject interface methods
    def attach(self, observer: Observer):
        if observer not in self.observers:
            self.observers.append(observer)
            print(f"{observer.name} is now observing user '{self.username}'.")

    def detach(self, observer: Observer):
        if observer in self.observers:
            self.observers.remove(observer)
            print(f"{observer.name} has stopped observing user '{self.username}'.")

    def notifyObservers(self, notification: str):
        for observer in self.observers:
            observer.update(notification)
