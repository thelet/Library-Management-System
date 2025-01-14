# user.py
from typing import List, Any
from observer import Observer, Subject
from Classes.book import Book

# Default permissions
USER_DEFAULT_PERMISSIONS = ["borrow", "return"]
LIBRARIAN_DEFAULT_PERMISSIONS = ["borrow", "return", "manage_books"]


class User(Observer, Subject):
    user_id = 0
    users_ids = [0]
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
        self._id = User.user_id
        self.username = username
        self.__passwordHash = passwordHash
        self.__permissions = permissions or USER_DEFAULT_PERMISSIONS
        self._borrowedBooks: List[Book] = []
        self.__temp_borrowedBooks: List[int] = []
        self._observers: List[Observer] = []  # Observers observing this user
        self.role = "regular user"
        self.notifications : list[str] = []

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

    @property
    def temp_borrowedBooks(self) -> List[int]:
        return self.__temp_borrowedBooks

    @property
    def id(self) -> int:
        return self._id

    @id.setter
    def id(self, value: int):
        if not isinstance(value, int):
            raise ValueError("ID must be an integer.")
        self._id = value

    @permissions.setter
    def permissions(self, value: List[str]):
        if not isinstance(value, list):
            raise ValueError("Permissions must be a list.")
        self.__permissions = value

    @temp_borrowedBooks.setter
    def temp_borrowedBooks(self, value: List[int]):
        if not isinstance(value, list):
            raise ValueError("Temp borrowedBooks must be a list.")
        self.__temp_borrowedBooks.clear()
        for val in value:
            self.__temp_borrowedBooks.append(val)



    def __str__(self):
        return (f"user id = {self.id} | username: {self.username} | password: {self.passwordHash} | role: {self.role} |"
                f" borrowed books ids: {[book.id for book in self.borrowedBooks]}\n")

    @staticmethod
    def create_user(username: str, passwordHash: str, permissions: List[str] = None):
        while User.user_id in User.users_ids:
            User.user_id += 1
        User.users_ids.append(User.user_id)
        return User(username, passwordHash, permissions)

    @staticmethod
    def loaded_user(username: str, passwordHash: str, prev_id : int,  permissions: List[str] = None, temp_books : List[int] = None) -> 'User':
        new_user = User(username=username, passwordHash=passwordHash, permissions=permissions)
        new_user.id = prev_id
        User.users_ids.append(new_user.id)
        new_user.temp_borrowedBooks = temp_books
        return new_user

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
        self.notifications.append(notification)
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
        temp_books = [book.id for book in self._borrowedBooks]

        return {
            "id": self.id,
            "username": self.username,
            "passwordHash": self.__passwordHash,
            "role" : self.role,
            "borrowed_books": temp_books
            #"borrowedBooks": [book.to_json() for book in self._borrowedBooks],
            #"observers": [obs.to_json() for obs in self._observers],
        }

    @staticmethod
    def from_json(json: dict[str, Any]):
        if json["role"] == "regular user":
            print(f"loaded books: {json['borrowed_books']}")
            return User.loaded_user(username=str(json["username"]), passwordHash=str(json["passwordHash"]), prev_id=int(json["id"]), temp_books=json["borrowed_books"])

        elif json["role"] == "librarian":
            return Librarian.from_json_librarian(json)
        else:
            raise ValueError(f"Unknown role '{json['role']}'")

    def __eq__(self, other):
        if isinstance(other, Book):
            return self.id == other.id
        return False

    def __hash__(self):
        return hash(self.id)

    @borrowedBooks.setter
    def borrowedBooks(self, value):
        self._borrowedBooks = value


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

    @staticmethod
    def create_librarian(username: str, passwordHash: str, permissions: List[str] = None):
        while User.user_id in User.users_ids:
            User.user_id += 1
        User.users_ids.append(User.user_id)
        return Librarian(username= username,passwordHash= passwordHash,permissions= permissions or LIBRARIAN_DEFAULT_PERMISSIONS)

    def to_json(self) -> dict:
        """
        Returns a JSON-serializable dict of the librarian data, including role='librarian'.
        """
        data = super().to_json()
        data["role"] = "librarian"
        return data

    @staticmethod
    def from_json_librarian(json : dict[str, Any]):
        basic_user = User.loaded_user(username=str(json["username"]), passwordHash=str(json["passwordHash"]), prev_id=int(json["id"]), temp_books=json["borrowed_books"])
        basic_user.permissions = LIBRARIAN_DEFAULT_PERMISSIONS
        basic_user.role = "librarian"
        return basic_user

    # Optionally, you can add librarian-specific methods (addBook, removeBook) if you want
    # them on the user side. Currently they are in library or handled via role checks.
