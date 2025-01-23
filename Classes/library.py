# library.py
import os
from os import write

from design_patterns.function_decorator import permission_required, upsert_after, update_csv_after
from design_patterns.observer import Subject, Observer
from design_patterns.strategy import SearchStrategy
from design_patterns.exceptions import PermissionDeniedException, BookNotFoundException, SignUpError
from design_patterns.logger import Logger
from Classes.book import Book
from Classes.user import User, Librarian
from manage_files import csv_manager

from typing import TYPE_CHECKING, Any, Optional,List

# Forward references to avoid circular imports
if TYPE_CHECKING:
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
PRINT_LOG = False
REGULAR_PRINTS = True

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

        with open(self.logger.log_file, "w") as log_file:
            log_file.write("")
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
        elif user_params["role"] == "librarian":
            user = Librarian.create_librarian(user_params["username"], user_params["password"])
            self.attach(user)

        if user is not None:
            user_id = user.id
            self.users[user_id] = user
            self.log_notify_print(
                to_log=f"\nRegistered - new {user.role} with Username :{user.username} and id: {user.id} - successfully.",
                to_notify=[self, f"New {user_params['role']} with username: {user.username} joined the library."],
                to_print = f"Completed sign up for {user_params['role']} with username: {user.username} and id: {user.id}.")

            self.write_new_user_to_csv(user)
            return user

        else:
            self.log_notify_print(
                to_log=f"Registration - with params {user_params} - failed",
                to_print=f"Error: Failed to register user", to_notify=None)
            raise SignUpError("Something went wrong during sign up. Please try again.")

    @update_csv_after([user_args_for_csv_update_wrapper])
    def write_new_user_to_csv(self, user: 'User'):
        pass

    # ------------- Book Management -------------

    @permission_required("manage_books")
    @update_csv_after([book_args_for_csv_update_wrapper])
    def addBook(self, book: Book, caller: Optional[User] = None):
        """
        If 'caller' is a librarian or has 'manage_books', add the book.
        Otherwise, raise PermissionDeniedException.
        """
        if caller is not None and not caller.has_permission("manage_books"):
            self.log_notify_print(to_log= f"Warning : unauthorised object tried to add a book.",
                                  to_print=f"Warning : unauthorised object tried to add a book.", to_notify=None)
            raise PermissionDeniedException("manage_books")

        self.books[book.id] = book
        self.log_notify_print(to_log= f"\nAdded book - '{book.title}' with id: {book.id} to the library - successfully.",
                              to_notify=[self, f"New book '{book.title}' by '{book.author}' added to library collection."],
                              to_print=f"New book '{book.title}' with id:{book.id} added to the library.")


    @permission_required("manage_books")
    def removeBook(self, book: Book, caller: Optional[User] = None):
        """
        Removes a book if caller is librarian or has 'manage_books'.
        Raises BookNotFoundException if not found.
        """
        if caller is not None and not caller.has_permission("manage_books"):
            self.log_notify_print(to_log=f"Warning : unauthorised object tried to remove a book.",
                                  to_print=f"Warning : unauthorised object tried to remove a book.", to_notify=None)
            raise PermissionDeniedException("manage_books")

        if book.id in self.books.keys():
            self.books.pop(book.id)
            Book.book_ids.remove(book.id)
            removed = csv_manager.remove_book_from_csv(book.id, self.books_csv_file_path)
            if removed:
                self.log_notify_print(to_log=f"Removed book - '{book.title}' from the library - successfully.",
                                      to_notify=[self,f"Removed book '{book.title}' by '{book.author}' from library collection."],
                                      to_print=f"Removed book '{book.title}' with id: '{book.id}' from the library.")
            else:
                self.log_notify_print(to_log=f"Remove book - for '{book.title}' - failed",to_print=f"Error: Failed to remove book '{book.title}'",to_notify=None)
        else:
            self.log_notify_print(to_log= f"Remove book - for '{book.title}' - failed, book not found",to_print= f"Error: Failed to remove book '{book.title}', book not found.", to_notify=None)
            raise BookNotFoundException(book.title)

    @update_csv_after([dec_book_args_for_csv_update_wrapper])
    def add_decorated_book(self, deco_book: 'BookDecorator'):
        if deco_book.id in self.books.keys():
            self.decorated_books.update({deco_book.id : deco_book})
            self.log_notify_print(to_log=f"Added decorator - for book {deco_book.id} - successfully.",
                                  to_print=f"Added decorator for book {deco_book.id}.",to_notify=None)


    # ----------- Searching and Filters-------------
    def searchBooks(self, criteria: str, strategy: SearchStrategy) -> List[Book]:
        book_list, str_to_log = strategy.search([book for book in self.books.values()], criteria)
        self.log_notify_print(to_log= f"{str_to_log} - {'successfully' if len(book_list) > 0 else 'failed'}" ,
                              to_print=str_to_log, to_notify=None)
        return book_list

    def getPopularBooks(self):
        sorted_books = sorted([book for book in self.books.values()], key=lambda book: book.borrow_count, reverse=True)
        if sorted_books and len(sorted_books) > 0:
            self.log_notify_print(to_log="Popular books - preformed - successfully.\nPopular books result:",
                                  to_print="Popular books search results: ", to_notify=None)
            for book in sorted_books:
                self.log_notify_print(to_log=f"Book: '{book.title}' Loans Counter: {book.borrow_count}",
                                      to_print=f"{book.title} - Borrow_count: {book.borrow_count}", to_notify=None)
            return sorted_books[:10]
        else:
            self.log_notify_print(to_log="Popular books - didn't found any books - failed.",
                                  to_print="Error : No popular books to display", to_notify=None)
            raise BookNotFoundException("No popular books to display")


    # ------------- Lending / Returning -------------
    @permission_required("borrow")
    @update_csv_after([user_args_for_csv_update_wrapper, book_args_for_csv_update_wrapper])
    def lendBook(self, user: 'User', book: Book, print_book = True) -> bool:
        """
        Let user borrow if copies > 0.
        """
        if book.available_copies > 0:
            user_borrowed = user.borrowBook(book)
            book_borrowed = book.borrow_book(user, print_update_for_copy= print_book)
            if not (user_borrowed or not book_borrowed) and print_book:
                self.log_notify_print(to_log=f"Book borrowing - for '{book.title}' - failed",
                                      to_print= f"Error: when user {user.id} tried to borrow '{book.title}'", to_notify=None)
            elif print_book:
                self.log_notify_print(to_log=f"Book borrowed - '{book.title}' by user '{user.id}' - successfully",
                                      to_print= f"User {user.username} with id: {user.id} borrowed '{book.title}'.",to_notify=None)
            return True
        else:
            self.log_notify_print(to_log=f"Book borrowing - for '{book.title}'  - failed, book had no available copies",
                                  to_print=f"User {user.id} tried to borrow book '{book.title}' but there's no available copies",
                                  to_notify=None)
            book.attach(user)
            return False

    @permission_required("return")
    @update_csv_after([user_args_for_csv_update_wrapper, book_args_for_csv_update_wrapper])
    def returnBook(self, user: 'User', book: Book, to_print = True) -> bool:
        """
        Let user return if they do indeed have it.
        """
        try:
            user_returned = user.returnBook(book)
            book_returned = book.return_book(user, print_update_for_copy=to_print)
            if not user_returned or not book_returned:
                self.log_notify_print(to_log=f"Book return - for '{book.title}' and user {user.username} - failed.",
                                      to_print=f"failed to return book '{book.title}' from user {user.username}.", to_notify=None)
            else:
                self.log_notify_print(to_log=f"Returned Book - '{book.title}' by user '{user.username}' - successfully",
                                      to_print=f"User {user.username} returned '{book.title}'.", to_notify=None)
        except BookNotFoundException:
            self.log_notify_print(
                to_log=f"Return Book - '{book.title}' by user '{user.username}' - failed, user doesn't have this book.",
                to_print=f"{user.username} does not have '{book.title}' borrowed.", to_notify=None)
            raise BookNotFoundException(f"User {user.username} tried to return '{book.title}' that he didn't borrowed.")
        return True



    # ------------- Subject Implementation -------------
    def attach(self, observer: Observer):
        if observer not in self.librarian_observers:
            self.librarian_observers.append(observer)
            self.log_notify_print(to_log= f"Attached observer - '{observer.name}' to library",
                                  to_print=f"User {observer.name} is now observing the library.",to_notify=None)

    def detach(self, observer: Observer):
        if observer in self.librarian_observers:
            self.librarian_observers.remove(observer)
            self.log_notify_print(to_log= f"Detached observer - '{observer.name}' from library",
                                  to_print=f"User {observer.name} stopped observing library.", to_notify=None)

    def notifyObservers(self, notification: str):
        for obs in self.librarian_observers:
            obs.update(notification)
        self.log_notify_print(to_log=f"Sent notification - from library to librarian users | msg : {notification} - successfully",
                                  to_print=f"Library notified observers: {notification}", to_notify=None)


    # ------------- Observer Implementation -------------
    def update(self, notification: str):
        """
        Library can receive notifications from other subjects if needed.
        """
        self.log_notify_print(to_log=f"Library received notification: {notification}",
                              to_print=f"Library received notification: {notification}", to_notify=None)

    # ------------- CSV / JSON Persistence -------------

    def load_users_from_csv(self, csv_file_path: str):

        self.users = csv_manager.load_objs_dict_from_csv(csv_file_path, self.user_headers_mapping, "User")
        self.users_csv_file_path = csv_file_path

        for u in self.users.values():
            if u.role == "librarian":
                self.attach(u)

        if len(self.users.values()) > 1:
            self.log_notify_print(to_log=f"Loaded ({len(self.users.values())-1}) users - from csv file: {csv_file_path} - successfully",
                                  to_print=f"Loaded ({len(self.users.values())-1}) users from csv file: {csv_file_path}", to_notify=None)
        else:
            self.log_notify_print(to_log=f"Warning : no users found in csv file: {csv_file_path}",
                                  to_print=f"No users found in csv file: {csv_file_path}", to_notify=None)



    def load_books_from_csv(self, csv_file_path: str):
        self.books = csv_manager.load_objs_dict_from_csv(csv_file_path, csv_manager.book_headers_mapping, "Book")
        self.books_csv_file_path = csv_file_path
        if len(self.books.values()) > 0:
            self.log_notify_print(to_log=f"Loaded ({len(self.books.values())}) books - from csv file: {csv_file_path} - successfully",
                                  to_print=f"Loaded ({len(self.books.values())}) books from csv file: {csv_file_path}", to_notify=None)
        else:
            self.log_notify_print(to_log=f"Warning : no books found in csv file: {csv_file_path}",
                                  to_print=f"No books found in csv file: {csv_file_path}", to_notify=None)

        #search if decorators exist and if they do, loading them
        try:
            self.load_decorators_from_csv(csv_file_path)
        except FileNotFoundError:
            self.log_notify_print(to_log=f"No decorators for books available for '{csv_file_path}'.",
                                  to_print=f"No decorators for books available for '{csv_file_path}'.", to_notify=None)


    def load_decorators_from_csv(self, books_csv_file_path: str):
        directory, filename = os.path.split(books_csv_file_path)
        name, ext = os.path.splitext(filename)
        new_file_name = f"{name}_book_decorators{ext}"
        csv_file_path = os.path.join(directory, new_file_name)

        # Check if the new CSV file exists
        if os.path.exists(csv_file_path):
            self.log_notify_print(to_log=f"Found decorators csv file: {csv_file_path}",
                                  to_print=f"Found decorators csv file: {csv_file_path}",to_notify=None)
            self.decorated_books = csv_manager.load_objs_dict_from_csv(csv_file_path,
                                                                       self.book_deco_headers_mapping, "book_decorator")
            self.book_decorators_file_path = csv_file_path
            if len(self.decorated_books.values()) > 0:
                self.log_notify_print(to_log=f"Loaded ({len(self.decorated_books.values())}) books decorator - from csv file: {csv_file_path} - successfully",
                                      to_print=f"Loaded ({len(self.decorated_books.values())}) books decorator from csv file: {csv_file_path}",to_notify=None)
            else:
                self.log_notify_print(to_log=f"Warning : no books decorator found in csv file: {csv_file_path}",
                                      to_print=f"No books decorator found in csv file: {csv_file_path}", to_notify=None)
        else:
            self.log_notify_print(to_log=f"No decorators for books available for '{csv_file_path}'.",
                                  to_print=f"No books decorator available for '{csv_file_path}'.", to_notify=None)



    def after_start(self):
        if self.users_csv_file_path is None:
            self.users_csv_file_path = csv_manager.create_empty_files(self.books_csv_file_path,
                                                                      self.user_headers_mapping.values(), "_users")
            self.log_notify_print(to_log=f"Created new users csv file: {self.users_csv_file_path}",
                                  to_print=f"Created new users csv file: {self.users_csv_file_path}",to_notify=None)

        if self.books_csv_file_path is None:
            self.books_csv_file_path = csv_manager.create_empty_files(self.users_csv_file_path,
                                                                      self.book_headers_mapping.values(), "_books")
            self.log_notify_print(to_log=f"Created new books csv file: {self.users_csv_file_path}",
                                  to_print=f"Created new books csv file: {self.users_csv_file_path}", to_notify=None)

        if self.book_decorators_file_path is None:
            self.book_decorators_file_path = csv_manager.create_empty_files(self.books_csv_file_path,
                                                                            self.book_deco_headers_mapping.values(), "_book_decorators")
            self.log_notify_print(to_log=f"Created new books decorators csv file: {self.users_csv_file_path}",
                                  to_print=f"Created new books decorators csv file: {self.users_csv_file_path}", to_notify=None)

        csv_manager.connect_books_and_users(self.users, self.books)


#----------------other methods----------------------
    def log_notify_print(self, to_log : str or None, to_notify: tuple[Subject, str] or None, to_print: str or None):
        if to_log:
            self.logger.log(to_log, PRINT_LOG)
        if to_notify:
            to_notify[0].notifyObservers(to_notify[1])
        if to_print and REGULAR_PRINTS:
            print(to_print)
            if to_log: print()

    def to_json(self) -> dict:
        return {
            "books": [b.to_json() for b in self.books.values()],
            "users": [u.to_json() for u in self.users.values()]
            # ...other fields
        }


