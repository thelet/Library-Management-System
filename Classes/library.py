# library.py
import os

from Classes import user
from design_patterns.function_decorator import permission_required, upsert_after, update_csv_after
from design_patterns.observer import Subject, Observer
from design_patterns.strategy import SearchStrategy
from design_patterns.exceptions import PermissionDeniedException, BookNotFoundException, SignUpError
from design_patterns.logger import Logger
from Classes.book import Book
from Classes.user import User, Librarian
from manage_files import csv_manager
# Forward references to avoid circular imports
from typing import TYPE_CHECKING, Any, Optional,List

if TYPE_CHECKING:
    #from user import User, Librarian
    from design_patterns.decorator import BookDecorator, CoverDecorator

user_args_for_csv_update_wrapper =  {
            "obj_arg_name": "user",
            "csv_file_path_attr": "users_csv_file_path",
            "headers_mapping_attr": "user_headers_mapping"
        }
book_args_for_csv_update_wrapper ={
            "obj_arg_name": "book",
            "csv_file_path_attr": "books_csv_file_path",
            "headers_mapping_attr": "book_headers_mapping"
        }
dec_book_args_for_csv_update_wrapper = {
    "obj_arg_name": "deco_book",
    "csv_file_path_attr": "book_decorators_file_path",
    "headers_mapping_attr": "book_deco_headers_mapping"
}

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
        self.logger: Logger = Logger()
        self.lost_books_user = User("holds_lost_books", "00000")
        self.users[0] = self.lost_books_user
        self.users_csv_file_path = None
        self.books_csv_file_path = None
        self.book_decorators_file_path = None
        self.book_headers_mapping = csv_manager.book_headers_mapping
        self.user_headers_mapping = csv_manager.user_headers_mapping
        self.book_deco_headers_mapping = csv_manager.book_deco_headers_mapping

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
    def signUp(self, user_params: dict[str, Any]):
        """
        Signs up a new user or librarian.

        :param user_params: dict - Contains 'username', 'password', and 'role'.
        :return: User or Librarian instance.
        """
        user = None
        self.validateSignUp(user_params)
        if user_params["role"] == "regular user":
            user = User.create_user(user_params["username"], user_params["password"])
            self.logger.log(f"\nUser {user.username} created successfully.\nUser Details:\n{user.__str__()}")
        elif user_params["role"] == "librarian":
            user = Librarian.create_librarian(user_params["username"], user_params["password"])
            self.logger.log(f"\nLibrarian {user.username} created successfully.\nLibrarian Details:\n{user.__str__()}")
            self.attach(user)
        if user is not None:
            user_id = user.id
            self.users[user_id] = user
            self.notifyObservers(f"new {user_params['role']} with username: {user.username} signed up successfully.")
            try:
                csv_manager.update_csv([user.to_json(), self.users_csv_file_path, csv_manager.user_headers_mapping])
            except ValueError as e:
                print(f"error when writing to file: {e}")

            print(f"added user to {self.users_csv_file_path}")
            return user
        else:
            raise SignUpError("Something went wrong during sign up. Please try again.")



    # ------------- Book Management -------------
    @permission_required("manage_books")
    @update_csv_after([book_args_for_csv_update_wrapper])
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
        self.logger.log(f"\nBook '{book.title}' added to the library.\nBook Details:\n{book.__str__()}")
        self.notifyObservers(f"New book added: '{book.title}' by {book.author}.")
        #csv_manager.upsert_obj_to_csv(book.to_json(), self.books_csv_file_path, csv_manager.book_headers_mapping)
        print(f"added book to {self.users_csv_file_path}")

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
            Book.book_ids.remove(book.id)
            csv_manager.remove_book_from_csv(book.id, self.books_csv_file_path)
            print(f"Book '{book.title}' removed from the library.")
            self.logger.log(f"Book '{book.title}' removed from the library.")
            self.notifyObservers(f"Book removed: '{book.title}' by {book.author}'.")
        else:
            raise BookNotFoundException(book.title)

    @update_csv_after([dec_book_args_for_csv_update_wrapper])
    def add_decorated_book(self, deco_book: 'BookDecorator'):
        if deco_book.id in self.books.keys():
            self.decorated_books.update({deco_book.id : deco_book})
            print(f"added decorator: {deco_book.id}")
            #csv_manager.upsert_obj_to_csv(deco_book.toJson(),self.book_decorators_file_path, self.book_deco_headers_mapping)


    # ----------- Searching and Filters-------------
    def searchBooks(self, criteria: str, strategy: SearchStrategy) -> List[Book]:
        book_list, str_to_log = strategy.search([book for book in self.books.values()], criteria)
        self.logger.log(f"\nBooks searched: {str_to_log}")
        return book_list
    def getPopularBooks(self):
        sorted_books = sorted([book for book in self.books.values()], key=lambda book: book.borrow_count, reverse=True)
        print("books sorted by borrow_count:")
        self.logger.log(f"\nPopular books result:\n")
        for book in sorted_books:
            print(f"{book.title} - borrow_count: {book.borrow_count}")
            self.logger.log(f"Book: '{book.title}' borrow_count: {book.borrow_count}")
        return sorted_books[:10]

    # ------------- Lending / Returning -------------
    @permission_required("borrow")
    @update_csv_after([user_args_for_csv_update_wrapper, book_args_for_csv_update_wrapper])
    def lendBook(self, user: 'User', book: Book) -> bool:
        """
        Let user borrow if copies > 0.
        """
        if book.available_copies > 0:
            user.borrowBook(book)
            book.updateCopies(-1)
            book.borrow_count += 1
            book.borrowed_users.append(user.id)
            self.notifyObservers(f"{user.username} borrowed '{book.title}'.")
            self.logger.log(f"User {user.username} borrowed book: '{book.title}' .")
            #csv_manager.upsert_obj_to_csv(user.to_json(), self.users_csv_file_path, csv_manager.user_headers_mapping)
            return True
        else:
            print(f"No copies available for '{book.title}'.")
            self.logger.log(f"User {user.username} tried to borrow book: '{book.title}' but no copies are available."
                            f"adding user '{user.username}' to book '{book.title}' notifications.")
            book.attach(user)
            return False

    @permission_required("return")
    @update_csv_after([user_args_for_csv_update_wrapper, book_args_for_csv_update_wrapper])
    def returnBook(self, user: 'User', book: Book) -> bool:
        """
        Let user return if they do indeed have it.
        """
        if book in user.borrowedBooks:
            user.returnBook(book)
            book.borrowed_users.remove(user.id)
            print(f"returned book: {book}")
            self.notifyObservers(f"{user.username} returned '{book.title}'.")
            self.logger.log(f"User {user.username} returned '{book.title}'.")
            #csv_manager.upsert_obj_to_csv(user.to_json(), self.users_csv_file_path, csv_manager.user_headers_mapping)
            return True
        else:
            print(f"{user.username} does not have '{book.title}' borrowed.")
            self.logger.log(f"User {user.username} tried to return '{book.title}' that he didn't borrowed.")
            raise BookNotFoundException(f"User {user.username} tried to return '{book.title}' that he didn't borrowed.")


    # ------------- Subject Implementation -------------
    def attach(self, observer: Observer):
        if observer not in self.librarian_observers:
            self.librarian_observers.append(observer)
            self.logger.log(f"{observer.name} is now observing the library.")
            print(f"{observer.name} is now observing the library.")

    def detach(self, observer: Observer):
        if observer in self.librarian_observers:
            self.librarian_observers.remove(observer)
            print(f"{observer.name} has stopped observing the library.")
            self.logger.log(f"{observer.name} has stopped observing the library.")

    def notifyObservers(self, notification: str):
        for obs in self.librarian_observers:
            obs.update(notification)
        self.logger.log(f"Library notified observers: {notification}")

    # ------------- Observer Implementation -------------
    def update(self, notification: str):
        """
        Library can respond to notifications from other subjects if needed.
        """
        print(f"Library received notification: {notification}")
        self.logger.log(f"Library received notification: {notification}")

    # ------------- CSV / JSON Persistence -------------

    def load_users_from_csv(self, csv_file_path: str):
        from Classes.user import User
        print("loading users from CSV...")
        self.users = csv_manager.load_objs_dict_from_csv(csv_file_path, csv_manager.user_headers_mapping, "User")

        print(f"Loaded users from '{csv_file_path}'. \n"
              f"Users List:\n")
        for u in self.users.values():
            if u.role == "librarian":
                self.attach(u)
            print(u)

        self.logger.log(f"Loaded users from '{csv_file_path}' :\nLoaded users:\n")
        self.users_csv_file_path = csv_file_path


    def load_books_from_csv(self, csv_file_path: str):
        from manage_files import csv_manager
        print("loading books from CSV...")
        self.books = csv_manager.load_objs_dict_from_csv(csv_file_path, csv_manager.book_headers_mapping, "Book")
        print(f"Loaded books from '{csv_file_path}'. \n"
              f"Books List:\n")
        self.logger.log(f"Loaded books from '{csv_file_path}' :\nLoaded books:\n")
        for book in self.books.values():
            print(book)
            self.logger.log(f"{book.__str__()}")

        self.books_csv_file_path = csv_file_path
        #search if decorators exist and if they do, loading them
        try:
            self.load_decorators_from_csv(csv_file_path)
        except FileNotFoundError:
            print(f"No decorators for books available for '{csv_file_path}'.")


    def after_start(self):
        from manage_files import csv_manager
        if self.users_csv_file_path is None:
            self.users_csv_file_path = csv_manager.create_empty_files(self.books_csv_file_path,
                                                                      self.user_headers_mapping.values(), "_users")
        if self.books_csv_file_path is None:
            self.books_csv_file_path = csv_manager.create_empty_files(self.users_csv_file_path,
                                                                      self.book_headers_mapping.values(), "_books")
        if self.book_decorators_file_path is None:
            self.book_decorators_file_path = csv_manager.create_empty_files(self.books_csv_file_path,
                                                                            self.book_deco_headers_mapping.values(), "_book_decorators")
        csv_manager.connect_books_and_users(self.users, self.books)

    def load_decorators_from_csv(self, books_csv_file_path: str):
        # Split the path into directory and filename
        directory, filename = os.path.split(books_csv_file_path)
        name, ext = os.path.splitext(filename)
        new_file_name = f"{name}_book_decorators{ext}"
        csv_file_path = os.path.join(directory, new_file_name)

        # Check if the new CSV file exists
        if os.path.exists(csv_file_path):
            print(f"found decorators file '{csv_file_path}'.")
            self.decorated_books = csv_manager.load_objs_dict_from_csv(csv_file_path,
                                                                       self.book_deco_headers_mapping, "book_decorator")
            self.book_decorators_file_path = csv_file_path
            print(f"loaded decorators file '{self.book_decorators_file_path}'.")
        else:
            print(f"decorators file '{csv_file_path}' does not exist.")




    def export_users_to_csv(self, csv_path):
        pass

    def export_books_to_csv(self,csv_path):
        pass




    def to_json(self) -> dict:
        return {
            "books": [b.to_json() for b in self.books.values()],
            "users": [u.to_json() for u in self.users.values()]
            # ...other fields
        }


