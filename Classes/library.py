# library.py
from Classes import user
from function_decorator import permission_required, upsert_after
from observer import Subject, Observer
from strategy import SearchStrategy
from exceptions import PermissionDeniedException, BookNotFoundException, SignUpError
import GUI.JSON_manager as JS_mng
from GUI.JSON_manager import *
from logger import Logger
from Classes.book import Book
from Classes.user import User, Librarian
from manage_files import csv_manager
# Forward references to avoid circular imports
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    #from user import User, Librarian
    from decorator import BookDecorator, CoverDecorator



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
    def signUp(self, user_params : dict[str,Any]):
        from Classes.user import User, Librarian
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
            self.notifyObservers(f"new {user_params["role"]} with username: {user.username} signed up successfully.")
            csv_manager.upsert_obj_to_csv(user.to_json(),self.users_csv_file_path, csv_manager.user_headers_mapping)
            print(f"added user to {self.users_csv_file_path}")

            return user
        else:
            raise SignUpError("Something went wrong during sign up. Please try again.")



    # ------------- Book Management -------------
    @permission_required("manage_books")
    @upsert_after(obj_arg_name='book', csv_file_path_attr='books_csv_file_path', headers_mapping_attr='book_headers_mapping')
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
            print(f"Book '{book.title}' removed from the library.")
            self.logger.log(f"Book '{book.title}' removed from the library.")
            self.notifyObservers(f"Book removed: '{book.title}' by {book.author}'.")
        else:
            raise BookNotFoundException(book.title)



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
    @upsert_after(obj_arg_name='book', csv_file_path_attr='books_csv_file_path',headers_mapping_attr='book_headers_mapping')
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
            csv_manager.upsert_obj_to_csv(user.to_json(), self.users_csv_file_path, csv_manager.user_headers_mapping)
            return True
        else:
            print(f"No copies available for '{book.title}'.")
            self.logger.log(f"User {user.username} tried to borrow book: '{book.title}' but no copies are available."
                            f"adding user '{user.username}' to book '{book.title}' notifications.")
            book.attach(user)
            return False

    @permission_required("return")
    @upsert_after(obj_arg_name='book', csv_file_path_attr='books_csv_file_path',headers_mapping_attr='book_headers_mapping')
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
            csv_manager.upsert_obj_to_csv(user.to_json(), self.users_csv_file_path, csv_manager.user_headers_mapping)
            return True
        else:
            print(f"{user.username} does not have '{book.title}' borrowed.")
            self.logger.log(f"User {user.username} tried to return '{book.title}' that he didn't borrowed.")
            return False

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
            self.load_decorators_from_json(csv_file_path)
        except FileNotFoundError:
            print(f"No decorators for books available for '{csv_file_path}'.")


    def after_login(self):
        from manage_files import csv_manager
        csv_manager.connect_books_and_users(self.users, self.books)
        if self.users_csv_file_path is None:
            self.users_csv_file_path = csv_manager.create_empty_files(self.books_csv_file_path,
                                                                      self.user_headers_mapping.values(), "_users")
        if self.books_csv_file_path is None:
            self.books_csv_file_path = csv_manager.create_empty_files(self.users_csv_file_path,
                                                                      self.book_headers_mapping.values(), "_books")
        self.book_decorators_file_path = csv_manager.create_empty_files(self.books_csv_file_path, self.book_deco_headers_mapping.values(), "_book_decorators")


    def load_decorators_from_json(self, csv_path):
        from decorator import CoverDecorator, DescriptionDecorator
        json_path = os.path.join(os.path.splitext(csv_path)[0], "decorators")
        # Ensure the directory exists
        if not os.path.isdir(json_path):
            raise FileNotFoundError(f"The directory '{json_path}' does not exist.")

        decorator_obj = []
        # Iterate over all files in the directory
        for filename in os.listdir(json_path):
            file_path = os.path.join(json_path, filename)
            if filename.endswith(".json") and os.path.isfile(file_path):
                try:
                    with open(file_path, "r", encoding="utf-8") as json_file:
                        json_data = json.load(json_file)
                        if "cover_image" in json_data:
                            d_book = CoverDecorator(self.books.get(int(filename[:-5])), json_data["cover_image"])
                            self.decorated_books[int(filename[:-5])] = d_book
                        if "description" in json_data:
                            d_book = DescriptionDecorator(self.books.get(int(filename[:-5])), json_data["description"])
                            self.decorated_books[int(filename[:-5])] = d_book
                except json.JSONDecodeError as e:
                    print(f"Failed to parse JSON file '{filename}': {e}")
                except Exception as e:
                    print(f"An error occurred while reading '{filename}': {e}")



    def export_users_to_csv(self, csv_path):
        root_dir = os.path.join(Library.json_dirs, "exported_users")
        JS_mng.write_json_obj(self.users.values(), root_dir, "users")
        JS_mng.jsons_to_csv_with_mapping(os.path.join(root_dir, "users_json"), csv_path , JS_mng.user_headers_mapping)
        print(f"Exported users to {csv_path}.")
        self.logger.log(f"Exported users to {csv_path}.")

    def export_books_to_csv(self,csv_path):
        root_dir = os.path.join(Library.json_dirs, "exported_books")
        JS_mng.write_json_obj(self.books.values(), root_dir, "books")
        JS_mng.jsons_to_csv_with_mapping(os.path.join(root_dir, "books_json"), csv_path, JS_mng.book_headers_mapping)
        print(f"Exported books to {csv_path}.")
        if self.decorated_books is not None and len(self.decorated_books) > 0:
            self.export_decorators_to_json(csv_path[:-4])
        self.logger.log(f"Exported books to {csv_path}.")

    def export_decorators_to_json(self, csv_path):
        root_dir = os.path.join(csv_path, "decorators")
        os.makedirs(root_dir, exist_ok=True)
        for b_id in self.decorated_books.keys():
            d_book = self.decorated_books[b_id]
            file_name = f"{b_id}.json"
            file_path = os.path.join(root_dir, file_name)
            with open(file_path, 'w', encoding='utf-8') as json_file:
                print(d_book.getDetails())
                json.dump(d_book.getDetails(), json_file, indent=4)
        print(f"Exported decorators to {root_dir}.")


    def to_json(self) -> dict:
        return {
            "books": [b.to_json() for b in self.books.values()],
            "users": [u.to_json() for u in self.users.values()]
            # ...other fields
        }


