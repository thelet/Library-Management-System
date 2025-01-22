# user.py

from typing import List, Any
from werkzeug.security import generate_password_hash, check_password_hash
import ast

from design_patterns.exceptions import BookNotFoundException
from design_patterns.observer import Observer, Subject
from Classes.book import Book
from design_patterns.function_decorator import permission_required

# Default permissions
USER_DEFAULT_PERMISSIONS = ["borrow", "return"]
LIBRARIAN_DEFAULT_PERMISSIONS = ["borrow", "return", "manage_books"]


class User(Observer, Subject):
    user_id = 0
    users_ids = [0]
    def __init__(self, username: str, password: str, permissions: List[str] = None):
        """
        :param username: str - The username of the user.
        :param password: str - The plain-text password for the user. It will be hashed internally.
        :param permissions: List[str] - List of permissions. Defaults to USER_DEFAULT_PERMISSIONS if not provided.
        """
        self._id = User.user_id
        self.username = username
        self.__passwordHash = self.set_password(password)
        self.__permissions = permissions or USER_DEFAULT_PERMISSIONS
        self._borrowedBooks: List[Book] = []
        self.__temp_borrowedBooks: List[int] = []
        self._observers: List[Observer] = []  # Observers observing this user
        self.role = "regular user"
        self.notifications: list[str] = []
        self.__previously_borrowed_books: list[int] = []

    def set_password(self, password: str) -> str:
        """
        Generates a hashed password using Werkzeug and stores it.

        :param password: str - The plain-text password.
        :return: str - The hashed password.
        """
        return generate_password_hash(password)

    def verify_password(self, password: str) -> bool:
        """
        Verifies a plain-text password against the stored hashed password.

        :param password: str - The plain-text password to verify.
        :return: bool - True if the password matches, False otherwise.
        """
        return check_password_hash(self.__passwordHash, password)

#------------property------------
    @property
    def name(self) -> str:
        return self.username

    @property
    def borrowedBooks(self) -> List[Book]:
        return self._borrowedBooks

    @property
    def previously_borrowed_books(self) -> List[int]:
        return self.__previously_borrowed_books

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
                f" borrowed books ids: {[book.id for book in self.borrowedBooks]} "
                f"| past borrowed books id's: {self.__previously_borrowed_books}\n")


#------------- creating\loading users ----------------
    @staticmethod
    def create_user(username: str, password: str, permissions: List[str] = None):
        """
        Creates a new user with a hashed password.

        :param username: str - The username of the user.
        :param password: str - The plain-text password for the user.
        :param permissions: List[str] - Optional permissions list.
        :return: User instance.
        """
        while User.user_id in User.users_ids:
            User.user_id += 1
        User.users_ids.append(User.user_id)
        return User(username, password, permissions)

    @staticmethod
    def loaded_user(username: str, passwordHash: str, prev_id: int, permissions: List[str] = None,
                    temp_books: List[int] = None, prev_borrowed: List[int] = None) -> 'User':
        """
        Loads a user from stored data with an existing hashed password.

        :param username: str - The username of the user.
        :param passwordHash: str - The hashed password.
        :param prev_id: int - The previous user ID.
        :param permissions: List[str] - Optional permissions list.
        :param temp_books: List[int] - List of currently borrowed book IDs.
        :param prev_borrowed: List[int] - List of previously borrowed book IDs.
        :return: User instance.
        """
        new_user = User(username=username, password=passwordHash, permissions=permissions)
        new_user.id = prev_id
        User.users_ids.append(new_user.id)
        new_user.temp_borrowedBooks = temp_books or []
        new_user.previously_borrowed_books = prev_borrowed or []
        # Directly set the password hash since it's already hashed
        new_user._User__passwordHash = passwordHash
        return new_user


    def has_permission(self, permission: str) -> bool:
        """
        Checks if the user has a specific permission.
        """
        return permission in self.__permissions

 #------------ books management ----------------

    @permission_required("borrow")
    def borrowBook(self, book: Book) -> bool:
        """
        Borrow the specified book if copies are available.
        Book attaches user as an observer to notify about availability changes.
        """
        try:
            if book.available_copies > 0:
                self._borrowedBooks.append(book)
                return True
            else:
                return False
        except Exception as e:
            print(f"Error: in user class, borrow book method : {e}")
            return False

    @permission_required("return")
    def returnBook(self, book: Book):
        """
        Return the specified book if the user actually has it borrowed.
        Detaches user from the book's observer list.
        """
        if book in self._borrowedBooks:
            try:
                self._borrowedBooks.remove(book)
                self.__previously_borrowed_books.append(book.id)
            except Exception as e:
                print(f"Error: in user class, return book method : {e}")
                return False
            return True
        else:
            raise BookNotFoundException(f"{self.username} does not have '{book.title}' borrowed.")

#------------ observer method ----------------
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


#------------------- json methods ----------------------
        # user.py

    def to_json(self) -> dict:
        """
        Returns a JSON-serializable dict of the user data.
        """
        temp_books = [book.id for book in self._borrowedBooks]
        prev_borrowed = [book_id for book_id in self.__previously_borrowed_books]

        return {
            "id": self.id,
            "username": self.username,
            "passwordHash": self.__passwordHash,  # Already hashed
            "role": self.role,
            "borrowed_books": temp_books,
            "previously_borrowed_books": prev_borrowed
        }

    @staticmethod
    def from_json(json: dict[str, Any]):
        if json["role"] == "regular user":
            return User.loaded_user(
                username=str(json["username"]),
                passwordHash=str(json["passwordHash"]),  # Assuming this is already hashed
                prev_id=int(json["id"]),
                temp_books=ast.literal_eval(json["borrowed_books"]),
                prev_borrowed=ast.literal_eval(json["previously_borrowed_books"])
            )
        elif json["role"] == "librarian":
            return Librarian.from_json_librarian(json)
        else:
            raise ValueError(f"Unknown role '{json['role']}'")

    #------------ other -----------------
    def __eq__(self, other):
        if isinstance(other, Book):
            return self.id == other.id
        return False

    def __hash__(self):
        return hash(self.id)

    @borrowedBooks.setter
    def borrowedBooks(self, value):
        self._borrowedBooks = value

    @previously_borrowed_books.setter
    def previously_borrowed_books(self, value):
        if value is None:
            value = []
        elif not isinstance(value, list):
            raise ValueError(f"previously_borrowed_books must be a list")
        self.__previously_borrowed_books.clear()
        for val in value:
            self.__previously_borrowed_books.append(val)


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
        self.role = "librarian"

    @staticmethod
    def create_librarian(username: str, passwordHash: str, permissions: List[str] = None):
        while User.user_id in User.users_ids:
            User.user_id += 1
        User.users_ids.append(User.user_id)
        return Librarian(username= username,passwordHash= passwordHash,permissions= permissions or LIBRARIAN_DEFAULT_PERMISSIONS)


    #------------- json methods --------------------

    def to_json(self) -> dict:
        """
        Returns a JSON-serializable dict of the librarian data, including role='librarian'.
        """
        data = super().to_json()
        data["role"] = "librarian"
        return data

    @staticmethod
    def from_json_librarian(json : dict[str, Any]):
        basic_user = User.loaded_user(username=str(json["username"]), passwordHash=str(json["passwordHash"]),
                                      prev_id=int(json["id"]), temp_books=ast.literal_eval(json["borrowed_books"]), prev_borrowed = ast.literal_eval(json["previously_borrowed_books"]))
        basic_user.permissions = LIBRARIAN_DEFAULT_PERMISSIONS
        basic_user.role = "librarian"
        return basic_user
