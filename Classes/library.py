# library.py

import json
import csv
import os
from typing import List, Optional
from function_decorator import permission_required
from observer import Subject, Observer
from Classes.book import Book
from strategy import SearchStrategy
from exceptions import LibraryException, PermissionDeniedException, BookNotFoundException, SignUpError
import GUI.JSON_manager as JS_mng
from GUI.JSON_manager import *

# Forward references to avoid circular imports
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from user import User, Librarian
    from decorator import BookDecorator


class Library(Subject, Observer):
    """
    The Library is a singleton that manages books, regular users, and librarian users.
    Implements Subject (can attach/detach/notify observers)
    and also Observer (can get notifications from other subjects).
    """

    __instance = None
    json_dirs = r"C:\Users\thele\Documents\PythonProject\oop_ex_3\data_files\JSON_data"

    def __init__(self):
        if Library.__instance is not None:
            raise RuntimeError("Library is a singleton! Use Library.getInstance() instead.")

        # Collections
        self.books: dict[int, 'Book'] = {}
        self.users: dict[int ,'User'] = {}
        self.decorated_books: dict[int, 'BookDecorator'] = {}
        self.librarian_observers: List[Observer] = []

        Library.__instance = self

    @staticmethod
    def getInstance() -> 'Library':
        if Library.__instance is None:
            Library()
        return Library.__instance

    @property
    def name(self) -> str:
        return "Library"

    def has_permission(self, permission: str) -> bool:
        permissions = ["borrow", "return", "manage_books", "manage_users"]
        return permission in permissions

    # ------------- Users Management -------------
    @permission_required("manage_users")
    def validateSignUp(self, user_params : dict[str,Any]):
        required_fields = ["username", "password", "role"]
        if required_fields.sort() != list(user_params.keys()).sort():
            raise SignUpError([param for param in required_fields if param not in user_params.keys()])
        elif any(user.username == user_params["username"] for user in self.users.values()):
            raise SignUpError(f"Username '{user_params['username']}' is already taken.")

    @permission_required("manage_users")
    def signUp(self, user_params : dict[str,Any]):
        from Classes.user import User, Librarian
        user = None
        self.validateSignUp(user_params)
        if user_params["role"] == "regular user":
            user = User.create_user(user_params["username"], user_params["password"])
        elif user_params["role"] == "librarian":
            user = Librarian.create_librarian(user_params["username"], user_params["password"])
            self.attach(user)
        if user is not None:
            user_id = user.id
            self.users[user_id] = user
            self.notifyObservers(f"new {user_params["role"]} with username: {user.username} signed up successfully.")
            return user
        else:
            raise SignUpError("Something went wrong during sign up. Please try again.")



    # ------------- Book Management -------------
    @permission_required("manage_books")
    def addBook(self, book: Book, caller: Optional['User'] = None):
        """
        If 'caller' is a librarian or has 'manage_books', add the book.
        Otherwise, raise PermissionDeniedException.
        """
        if caller is not None and not caller.has_permission("manage_books"):
            raise PermissionDeniedException("manage_books")
        book_id = book.id
        self.books[book_id] = book
        print(f"Book '{book.title}' added to the library.")
        self.notifyObservers(f"New book added: '{book.title}' by {book.author}.")

    @permission_required("manage_books")
    def removeBook(self, book: Book, caller: Optional['User'] = None):
        """
        Removes a book if caller is librarian or has 'manage_books'.
        Raises BookNotFoundException if not found.
        """
        if caller is not None and not caller.has_permission("manage_books"):
            raise PermissionDeniedException("manage_books")
        if book.id in self.books.keys():
            self.books.pop(book.id)
            print(f"Book '{book.title}' removed from the library.")
            self.notifyObservers(f"Book removed: '{book.title}' by {book.author}'.")
        else:
            raise BookNotFoundException(book.title)

    @permission_required("manage_books")
    def updateBook(self, book: Book, caller: Optional['User'] = None):
        """
        Placeholder to update book details if caller has manage_books.
        """
        if caller is not None and not caller.has_permission("manage_books"):
            raise PermissionDeniedException("manage_books")
        # Additional logic to actually update the Book object if needed
        print(f"Book '{book.title}' updated in the library.")
        self.notifyObservers(f"Book updated: '{book.title}'.")

    # ----------- Searching and Filters-------------
    def searchBooks(self, criteria: str, strategy: SearchStrategy) -> List[Book]:
        return strategy.search(self.books.values(), criteria)
    def getPopularBooks(self):
        sorted_books = sorted(self.books.values(), key=lambda book: book.borrow_count, reverse=True)
        print("books sorted by borrow_count:")
        for book in sorted_books:
            print(f"{book.title} - borrow_count: {book.borrow_count}")
        return sorted_books[:10]

    # ------------- Lending / Returning -------------
    @permission_required("borrow")
    def lendBook(self, user: 'User', book: Book) -> bool:
        """
        Let user borrow if copies > 0.
        """
        if book.copies > 0:
            user.borrowBook(book)
            book.updateCopies(-1)
            book.borrow_count += 1
            self.notifyObservers(f"{user.username} borrowed '{book.title}'.")
            return True
        else:
            print(f"No copies available for '{book.title}'.")
            book.attach(user)
            return False

    @permission_required("return")
    def returnBook(self, user: 'User', book: Book) -> bool:
        """
        Let user return if they do indeed have it.
        """
        if book in user.borrowedBooks:
            user.returnBook(book)
            self.notifyObservers(f"{user.username} returned '{book.title}'.")
            return True
        else:
            print(f"{user.username} does not have '{book.title}' borrowed.")
            return False

    # ------------- Subject Implementation -------------
    def attach(self, observer: Observer):
        if observer not in self.librarian_observers:
            self.librarian_observers.append(observer)
            print(f"{observer.name} is now observing the library.")

    def detach(self, observer: Observer):
        if observer in self.librarian_observers:
            self.librarian_observers.remove(observer)
            print(f"{observer.name} has stopped observing the library.")

    def notifyObservers(self, notification: str):
        for obs in self.librarian_observers:
            obs.update(notification)

    # ------------- Observer Implementation -------------
    def update(self, notification: str):
        """
        Library can respond to notifications from other subjects if needed.
        """
        print(f"Library received notification: {notification}")

    # ------------- CSV / JSON Persistence -------------

    def load_users_from_csv(self, csv_file_path: str):
        from Classes.user import User
        print("loading users from CSV...")
        json_root =os.path.join(Library.json_dirs, "users_from_csv")
        JS_mng.csv_to_individual_json_files(csv_file_path, JS_mng.user_headers_mapping, json_root)
        self.users = JS_mng.load_objs_from_json(json_root, "users")
        print(f"Loaded users from '{csv_file_path}'. \n"
              f"Users List:\n")

        if self.books is not None and len(self.books) > 0:
            JS_mng.reconnect_borrowed_books(self.users, self.books)
            JS_mng.reattached_observers(self.books, self.users)

        for user in self.users.values():
            if user.role == "librarian":
                self.attach(user)
            print(user)

    def load_books_from_csv(self, csv_file_path: str):
        print("loading books from CSV...")
        json_root = os.path.join(Library.json_dirs, "books_from_csv")
        JS_mng.csv_to_individual_json_files(csv_file_path, JS_mng.book_headers_mapping, json_root)
        self.books = JS_mng.load_objs_from_json(json_root, "books")
        print(f"Loaded books from '{csv_file_path}'. \n"
              f"Books List:\n")

        if self.users is not None and len(self.users) > 0:
            JS_mng.reconnect_borrowed_books(self.users, self.books)
            JS_mng.reattached_observers(self.books, self.users)

        for book in self.books.values():
            print(book)

    def export_users_to_csv(self, csv_path):
        root_dir = os.path.join(Library.json_dirs, "exported_users")
        JS_mng.write_json_obj(self.users.values(), root_dir, "users")
        JS_mng.jsons_to_csv_with_mapping(os.path.join(root_dir, "users_json"), csv_path , JS_mng.user_headers_mapping)
        print(f"Exported users to {csv_path}.")

    def export_books_to_csv(self,csv_path):
        root_dir = os.path.join(Library.json_dirs, "exported_books")
        JS_mng.write_json_obj(self.books.values(), root_dir, "books")
        JS_mng.jsons_to_csv_with_mapping(os.path.join(root_dir, "books_json"), csv_path, JS_mng.book_headers_mapping)
        print(f"Exported books to {csv_path}.")

    def to_json(self) -> dict:
        return {
            "books": [b.to_json() for b in self.books.values()],
            "users": [u.to_json() for u in self.users.values()]
            # ...other fields
        }


