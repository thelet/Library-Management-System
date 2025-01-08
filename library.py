# library.py
from typing import List
from observer import Subject, Observer
from book import Book
from strategy import SearchStrategy
import csv
import os

class Library(Subject, Observer):
    __instance = None

    def __init__(self):
        if Library.__instance is not None:
            raise Exception("This class is a singleton!")
        else:
            self.books: List[Book] = []
            self.users: List['User'] = []  # Use forward reference
            self.observers: List[Observer] = []
            Library.__instance = self

    @staticmethod
    def getInstance():
        if Library.__instance is None:
            Library()
        return Library.__instance

    @property
    def name(self) -> str:
        return "Library"

    def addBook(self, book: Book):
        self.books.append(book)
        self.notifyObservers(f"New book added: '{book.title}' by {book.author}.")

    def removeBook(self, book: Book):
        if book in self.books:
            self.books.remove(book)
            self.notifyObservers(f"Book removed: '{book.title}' by {book.author}'.")
        else:
            print(f"Book '{book.title}' not found in library.")

    def updateBook(self, book: Book):
        # Update book details logic (e.g., updating category, author)
        self.notifyObservers(f"Book updated: '{book.title}' by {book.author}'.")

    def searchBooks(self, criteria: str, strategy: SearchStrategy) -> List[Book]:
        return strategy.search(self.books, criteria)

    def lendBook(self, user: 'User', book: Book) -> bool:
        if book.copies > 0:
            #book.updateCopies(-1)
            user.borrowBook(book)
            self.notifyObservers(f"{user.username} borrowed '{book.title}'.")
            return True
        else:
            print(f"No copies available for '{book.title}'. {user.username} can subscribe for notifications.")
            # Automatically subscribe user for availability notifications
            book.attach(user)
            return False

    def returnBook(self, user: 'User', book: Book) -> bool:
        if book in user.borrowedBooks:
            #book.updateCopies(1)
            user.returnBook(book)
            self.notifyObservers(f"{user.username} returned '{book.title}'.")
            return True
        else:
            print(f"{user.username} does not have '{book.title}' borrowed.")
            return False

    # Subject interface methods
    def attach(self, observer: Observer):
        if observer not in self.observers:
            self.observers.append(observer)
            print(f"{observer.name} is now observing the library.")

    def detach(self, observer: Observer):
        if observer in self.observers:
            self.observers.remove(observer)
            print(f"{observer.name} has stopped observing the library.")

    def notifyObservers(self, notification: str):
        for observer in self.observers:
            observer.update(notification)

    # Observer interface method
    def update(self, notification: str):
        print(f"Library received notification: {notification}")
        # Further processing based on notification can be implemented here

    def load_books_from_csv(self, csv_file_path: str):
        if not os.path.exists(csv_file_path):
            print(f"CSV file '{csv_file_path}' does not exist.")
            return

        with open(csv_file_path, newline='', encoding='utf-8-sig') as csvfile:
            try:
                reader = csv.DictReader(csvfile, delimiter=',')

                # Debugging: Print the headers read
                print(f"CSV Headers: {reader.fieldnames}")

                required_fields = ['title', 'author', 'is_loaned', 'copies', 'genre', 'year']
                missing_fields = [field for field in required_fields if field not in reader.fieldnames]
                if missing_fields:
                    print(f"CSV is missing required fields: {missing_fields}")
                    return

                for row_number, row in enumerate(reader, start=2):  # Start at 2 to account for header
                    try:
                        # Debugging: Print each row being processed
                        print(f"Processing Row {row_number}: {row}")

                        title = row['title'].strip()
                        author = row['author'].strip()
                        is_loaned = row['is_loaned'].strip().lower()
                        copies_str = row['copies'].strip()
                        genre = row['genre'].strip()
                        year_str = row['year'].strip()

                        # Convert copies and year to integers, handle possible errors
                        copies = int(copies_str) if copies_str else 0
                        year = int(year_str) if year_str else 0

                        # Adjust available copies based on 'is_loaned' status
                        if is_loaned == 'yes':
                            available_copies = copies - 1 if copies > 0 else 0
                        else:
                            available_copies = copies

                        # Create and add the book to the library
                        book = Book.createBook(title, author, year, genre, available_copies)
                        self.addBook(book)
                    except ValueError as ve:
                        print(f"Error processing row {row_number}: {ve}")
                    except KeyError as ke:
                        print(f"Missing expected field {ke} in row {row_number}.")

            except csv.Error as e:
                print(f"Error reading CSV file: {e}")
                return

        print(f"Loaded books from '{csv_file_path}'. Total books: {len(self.books)}")
