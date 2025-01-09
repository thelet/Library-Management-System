# user.py
from typing import List
from observer import Observer, Subject
from Classes.book import Book

# Default permissions
USER_DEFAULT_PERMISSIONS = ["borrow", "return"]
LIBRARIAN_DEFAULT_PERMISSIONS = ["borrow", "return", "manage_books"]

class User(Observer, Subject):
    """
    Represents a regular user in the library system.
    Inherits from Observer (to get notifications) and Subject (can be observed, e.g., by other users or systems).
    """

    def __init__(self, username: str, passwordHash: str, permissions: List[str] = None):
        """
        :param username: str - The username of the user.
        :param passwordHash: str - The hashed password for the user.
        :param permissions: List[str] - List of permissions. Defaults to USER_DEFAULT_PERMISSIONS if not provided.
        """
        self.username = username
        self.__passwordHash = passwordHash
        self.__permissions = permissions or USER_DEFAULT_PERMISSIONS
        self._borrowedBooks: List[Book] = []
        self._observers: List[Observer] = []  # Observers observing this user

    @property
    def name(self) -> str:
        return self.username

    @property
    def borrowedBooks(self) -> List[Book]:
        return self._borrowedBooks

    @property
    def passwordHash(self) -> str:
        return self.__passwordHash

    @property
    def permissions(self) -> List[str]:
        return self.__permissions

    def has_permission(self, permission: str) -> bool:
        """
        Checks if the user has a specific permission.
        """
        return permission in self.__permissions

    def register(self, password: str):
        # Registration logic (could be hashing password, storing user data, etc.)
        print(f"{self.username} has registered.")
        self.notifyObservers(f"User registered: {self.username}")

    def login(self, password: str) -> bool:
        # Login logic (verifying password, etc.)
        print(f"{self.username} has logged in.")
        self.notifyObservers(f"User logged in: {self.username}")
        return True  # For real usage, verify password properly

    def borrowBook(self, book: Book):
        """
        Borrow the specified book if copies are available.
        Book attaches user as an observer to notify about availability changes.
        """
        if book.copies > 0:
            self._borrowedBooks.append(book)
            book.attach(self)
            from Classes.library import Library
            library = Library.getInstance()
            library.notifyObservers(f"{self.username} borrowed '{book.title}'.")
            print(f"{self.username} borrowed '{book.title}'.")
            book.borrow_count += 1
        else:
            print(f"No copies available for '{book.title}'. {self.username} can subscribe for notifications.")
            book.attach(self)

    def returnBook(self, book: Book):
        """
        Return the specified book if the user actually has it borrowed.
        Detaches user from the book's observer list.
        """
        if book in self._borrowedBooks:
            book.updateCopies(1)
            self._borrowedBooks.remove(book)
            book.detach(self)
            from Classes.library import Library
            library = Library.getInstance()
            library.notifyObservers(f"{self.username} returned '{book.title}'.")
            print(f"{self.username} returned '{book.title}'.")
        else:
            print(f"{self.username} does not have '{book.title}' borrowed.")

    # Observer Method
    def update(self, notification: str):
        """
        Called when the user is notified by a subject they observe (e.g., a Book).
        """
        print(f"Notification for {self.username}: {notification}")

    # Subject Interface Methods
    def attach(self, observer: Observer):
        if observer not in self._observers:
            self._observers.append(observer)
            print(f"{observer.name} is now observing user '{self.username}'.")

    def detach(self, observer: Observer):
        if observer in self._observers:
            self._observers.remove(observer)
            print(f"{observer.name} has stopped observing user '{self.username}'.")

    def notifyObservers(self, notification: str):
        for obs in self._observers:
            obs.update(notification)

    def to_json(self) -> dict:
        """
        Returns a JSON-serializable dict of the user data.
        """
        return {
            "username": self.username,
            "passwordHash": self.__passwordHash,
            "permissions": self.__permissions,
            "borrowedBooks": [book.to_json() for book in self._borrowedBooks],
            "observers": [obs.to_json() for obs in self._observers],
        }


class Librarian(User):
    """
    A special kind of User with additional default permissions: "manage_books".
    """

    def __init__(self, username: str, passwordHash: str, permissions: List[str] = None):
        super().__init__(
            username,
            passwordHash,
            permissions or LIBRARIAN_DEFAULT_PERMISSIONS
        )

    def to_json(self) -> dict:
        """
        Returns a JSON-serializable dict of the librarian data, including role='librarian'.
        """
        data = super().to_json()
        data["role"] = "librarian"
        return data

    # Optionally, you can add librarian-specific methods (addBook, removeBook) if you want
    # them on the user side. Currently they are in library or handled via role checks.
