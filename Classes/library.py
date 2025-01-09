# library.py

import json
import csv
import os
from typing import List, Optional

from observer import Subject, Observer
from Classes.book import Book
from strategy import SearchStrategy
from exceptions import LibraryException, PermissionDeniedException, BookNotFoundException
from functions.csv_json_functions import json_to_csv

# Forward references to avoid circular imports
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from user import User, Librarian


class Library(Subject, Observer):
    """
    The Library is a singleton that manages books, regular users, and librarian users.
    Implements Subject (can attach/detach/notify observers)
    and also Observer (can get notifications from other subjects).
    """

    __instance = None

    def __init__(self):
        if Library.__instance is not None:
            raise RuntimeError("Library is a singleton! Use Library.getInstance() instead.")

        # Collections
        self.books: List[Book] = []
        self.users: List['User'] = []
        self.librarian_users: List['Librarian'] = []
        self.books_observers: List[Observer] = []

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
        return permission in ["borrow", "return", "manage_books"]

    # ------------- Book Management -------------
    def addBook(self, book: Book, caller: Optional['User'] = None):
        """
        If 'caller' is a librarian or has 'manage_books', add the book.
        Otherwise, raise PermissionDeniedException.
        """
        if caller is not None and not caller.has_permission("manage_books"):
            raise PermissionDeniedException("manage_books")
        self.books.append(book)
        print(f"Book '{book.title}' added to the library.")
        self.notifyObservers(f"New book added: '{book.title}' by {book.author}.")

    def removeBook(self, book: Book, caller: Optional['User'] = None):
        """
        Removes a book if caller is librarian or has 'manage_books'.
        Raises BookNotFoundException if not found.
        """
        if caller is not None and not caller.has_permission("manage_books"):
            raise PermissionDeniedException("manage_books")
        if book in self.books:
            self.books.remove(book)
            print(f"Book '{book.title}' removed from the library.")
            self.notifyObservers(f"Book removed: '{book.title}' by {book.author}'.")
        else:
            raise BookNotFoundException(book.title)

    def updateBook(self, book: Book, caller: Optional['User'] = None):
        """
        Placeholder to update book details if caller has manage_books.
        """
        if caller is not None and not caller.has_permission("manage_books"):
            raise PermissionDeniedException("manage_books")
        # Additional logic to actually update the Book object if needed
        print(f"Book '{book.title}' updated in the library.")
        self.notifyObservers(f"Book updated: '{book.title}'.")

    # ------------- Searching -------------
    def searchBooks(self, criteria: str, strategy: SearchStrategy) -> List[Book]:
        return strategy.search(self.books, criteria)

    # ------------- Lending / Returning -------------
    def lendBook(self, user: 'User', book: Book) -> bool:
        """
        Let user borrow if copies > 0.
        """
        if book.copies > 0:
            user.borrowBook(book)
            book.updateCopies(-1)
            self.notifyObservers(f"{user.username} borrowed '{book.title}'.")
            return True
        else:
            print(f"No copies available for '{book.title}'.")
            book.attach(user)
            return False

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
        if observer not in self.books_observers:
            self.books_observers.append(observer)
            print(f"{observer.name} is now observing the library.")

    def detach(self, observer: Observer):
        if observer in self.books_observers:
            self.books_observers.remove(observer)
            print(f"{observer.name} has stopped observing the library.")

    def notifyObservers(self, notification: str):
        for obs in self.books_observers:
            obs.update(notification)

    # ------------- Observer Implementation -------------
    def update(self, notification: str):
        """
        Library can respond to notifications from other subjects if needed.
        """
        print(f"Library received notification: {notification}")

    # ------------- CSV / JSON Persistence -------------
    def books_collection_to_json(self):
        """
        Write current library books to JSON, then convert to CSV.
        """
        json_books = [b.to_json() for b in self.books]
        json_file_path = r"C:\path\to\books_collection.json"
        try:
            with open(json_file_path, "w", encoding="utf-8") as file:
                json.dump(json_books, file, indent=4)
            print(f"Data successfully written to {json_file_path}.")
        except Exception as e:
            print(f"Failed to write data to JSON file: {e}")
            return

        # Convert JSON to CSV
        try:
            from functions.csv_json_functions import json_to_csv
            csv_dest = r"C:\path\to\books_collection.csv"
            json_to_csv(json_file_path, csv_dest)
        except Exception as e:
            print(f"Failed to convert JSON to CSV: {e}")

    def load_books_from_csv(self, csv_file_path: str):
        """
        Reads books from a CSV and adds them to the library.
        """
        if not os.path.exists(csv_file_path):
            print(f"CSV file '{csv_file_path}' does not exist.")
            return

        required_fields = ['title', 'author', 'is_loaned', 'copies', 'genre', 'year']

        with open(csv_file_path, newline='', encoding='utf-8-sig') as csvfile:
            try:
                reader = csv.DictReader(csvfile, delimiter=',')
                print(f"CSV Headers: {reader.fieldnames}")

                missing_fields = [f for f in required_fields if f not in reader.fieldnames]
                if missing_fields:
                    print(f"CSV is missing required fields: {missing_fields}")
                    return

                from Classes.book import Book
                from exceptions import PermissionDeniedException, BookNotFoundException

                # 'self' acts as a caller if needed
                for row_number, row in enumerate(reader, start=2):
                    try:
                        print(f"Processing Row {row_number}: {row}")

                        title = row['title'].strip()
                        author = row['author'].strip()
                        is_loaned = row['is_loaned'].strip().lower()
                        copies_str = row['copies'].strip()
                        genre = row['genre'].strip()
                        year_str = row['year'].strip()

                        copies = int(copies_str) if copies_str else 0
                        year = int(year_str) if year_str else 0
                        if is_loaned == 'yes':
                            available_copies = copies - 1 if copies > 0 else 0
                        else:
                            available_copies = copies

                        book = Book.createBook(title, author, year, genre, available_copies)
                        self.addBook(book, self)  # 'self' is the caller
                    except ValueError as ve:
                        print(f"Error processing row {row_number}: {ve}")
                    except KeyError as ke:
                        print(f"Missing expected field {ke} in row {row_number}.")

            except csv.Error as e:
                print(f"Error reading CSV file: {e}")
                return

        self.books_collection_to_json()
        print(f"Loaded books from '{csv_file_path}'. Total books: {len(self.books)}")

    def load_users_from_csv(self, csv_file_path: str):
        """
        Example function for loading user data from CSV, if you want to implement it.
        """
        if not os.path.exists(csv_file_path):
            print(f"CSV file '{csv_file_path}' does not exist.")
            return

        # e.g. fields: username, passwordHash, role (user/librarian)
        required_fields = ["username", "passwordHash", "role"]

        with open(csv_file_path, newline='', encoding='utf-8-sig') as csvfile:
            try:
                reader = csv.DictReader(csvfile, delimiter=',')
                print(f"CSV Headers: {reader.fieldnames}")

                missing_fields = [f for f in required_fields if f not in reader.fieldnames]
                if missing_fields:
                    print(f"CSV is missing required fields: {missing_fields}")
                    return

                from Classes.user import User, Librarian

                for row_number, row in enumerate(reader, start=2):
                    username = row["username"].strip()
                    password_hash = row["passwordHash"].strip()
                    role = row["role"].strip().lower()

                    if role == "librarian":
                        librarian = Librarian(username, password_hash)
                        self.librarian_users.append(librarian)
                        print(f"Librarian '{username}' loaded from CSV.")
                    else:
                        user = User(username, password_hash)
                        self.users.append(user)
                        print(f"User '{username}' loaded from CSV.")

            except csv.Error as e:
                print(f"Error reading CSV file: {e}")
                return

        print(
            f"Loaded users from '{csv_file_path}'. Total users: {len(self.users)}, librarians: {len(self.librarian_users)}")

    def to_json(self) -> dict:
        return {
            "books": [b.to_json() for b in self.books],
            "users": [u.to_json() for u in self.users],
            "librarian_users": [l.to_json() for l in self.librarian_users]
            # ...other fields
        }

    def export_data_to_csv(self, books_csv_path: str, users_csv_path: str):
        """
        Exports the current library books and users to two CSV files.
        :param books_csv_path: Destination CSV path for books
        :param users_csv_path: Destination CSV path for users
        """
        # 1) Export Books
        try:
            import csv
            with open(books_csv_path, mode="w", newline="", encoding="utf-8") as books_file:
                writer = csv.writer(books_file)
                writer.writerow(["title", "author","is_loaned", "copies", "genre", "year", ])
                for book in self.books:
                    is_loaned = "Yes" if book.isLoaned else "No"
                    writer.writerow([
                        book.title,
                        book.author,
                        is_loaned,
                        book.copies,
                        book.category,
                        book.year
                    ])
            print(f"Books exported to {books_csv_path}.")
        except Exception as e:
            print(f"Failed to export books: {e}")
            raise

        # 2) Export Users (regular + librarians)
        try:
            import csv
            with open(users_csv_path, mode="w", newline="", encoding="utf-8") as users_file:
                writer = csv.writer(users_file)
                writer.writerow(["username", "passwordHash", "role", "permissions"])
                # Export regular users
                for user in self.users:
                    role = "user"
                    writer.writerow([
                        user.username,
                        user.passwordHash,
                        role,
                        ",".join(user.permissions)
                    ])
                # Export librarians
                for librarian in self.librarian_users:
                    role = "librarian"
                    writer.writerow([
                        librarian.username,
                        librarian.passwordHash,
                        role,
                        ",".join(librarian.permissions)
                    ])
            print(f"Users exported to {users_csv_path}.")
        except Exception as e:
            print(f"Failed to export users: {e}")
            raise


