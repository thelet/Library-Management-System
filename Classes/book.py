# book.py
import ast
from typing import List, Any, TYPE_CHECKING
from design_patterns.observer import Subject, Observer
if TYPE_CHECKING:
    from Classes.user import User

class Book(Subject):
    book_id = 0
    book_ids = [0]
    def __init__(self, title: str, author: str, year: int, category: str, available_copies: int):
        self.id = Book.book_id
        self.title = title
        self.author = author
        self.year = year
        self.category = category
        self.available_copies = available_copies
        self.copies = available_copies
        self.isLoaned = False
        self.user_observers: List['User'] = []
        self.borrow_count = 0  # To track popularity
        self.temp_followers = None
        self.borrowed_users : List[int] = []


    def __str__(self):
        return (f'book id: {self.id} | title: {self.title} | author: {self.author} | year: {self.year} | category: {self.category}'
                f' | copies: {self.copies} | available_copies: {self.available_copies} | isLoaned: {self.isLoaned}'
                f' | followers users ids: {[user.id for user in self.user_observers]} | borrowed this book : {self.borrowed_users}\n')


 #------------------- loading\creating a book --------------
    @staticmethod
    def createBook(title: str, author: str, year: int, category: str, copies: int) -> 'Book':
        if copies < 0:
            raise ValueError("Number of copies cannot be negative.")
        while Book.book_id in Book.book_ids:
            Book.book_id += 1
        Book.book_ids.append(Book.book_id)
        return Book(title, author, year, category, copies)

    @staticmethod
    def loaded_book(title: str, author: str, year: int, category: str, copies: int, prev_id,
                    followers_ids : List[int], borrow_count : int, borrowed_users : List[int], is_loaned :bool) -> 'Book':
        new_book =  Book(title, author, year, str(category), int(copies))
        new_book.set_id(prev_id)
        Book.book_ids.append(new_book.id)
        new_book.temp_followers = followers_ids
        new_book.borrow_count = borrow_count
        new_book.borrowed_users = borrowed_users
        new_book.available_copies -= len(borrowed_users)
        new_book.isLoaned = is_loaned

        return new_book

#------------borrow and return--------------
    def borrow_book(self, user: 'User', print_update_for_copy = True) -> bool:
        try:
            if self.isLoaned or self.available_copies <1:
                return False
            self.updateCopies(-1, to_print=print_update_for_copy)
            self.borrow_count += 1
            self.borrowed_users.append(user.id)
        except Exception as e:
            print(f"Error: book class, borrow book method: {e}")
            return False
        return True

    def return_book(self, user: 'User', print_update_for_copy = True) -> bool:
        try:
            self.borrowed_users.remove(user.id)
            self.updateCopies(1, to_print=print_update_for_copy)
        except Exception as e:
            print(f"Error: book class, return book method: {e}")
            return False
        return True

    #-------------------- observer methods -------------------------
    def attach(self, observer: Observer):
        from Classes.library import Library
        if observer not in self.user_observers:
            self.user_observers.append(observer)
            Library.getInstance().log_notify_print(to_log=f"User '{observer.name}' applied for book '{self.title}' notifications - successfully.",
                                  to_print=f"User '{observer.name}' applied for '{self.title}' notifications",
                                  to_notify=None)

    def detach(self, observer: Observer):
        from Classes.library import Library
        if observer in self.user_observers:
            self.user_observers.remove(observer)
            Library.getInstance().log_notify_print(to_log=f"Removed '{observer.name}' from notifications for '{self.title}' - successfully..",
                                                   to_print=f"User '{observer.name}' unsubscribed from notifications for '{self.title}' .", to_notify=None)

    def notifyObservers(self, notification: str):
        from Classes.library import Library
        for observer in self.user_observers:
            observer.update(notification)
        Library.getInstance().log_notify_print(to_log=f"Sent notification- from book '{self.title}' | msg : {notification} | - successfully.",
                                               to_print=f"Sent notification from book '{self.title}' | msg : {notification}.", to_notify=None)



#---------------- JSON\dict methods ------------------------

    def to_json(self):
        from Classes.user import User

        observers_ids = [user.id for user in self.user_observers]
        is_loaned = "Yes" if self.isLoaned else "No"

        return {
            "id": self.id,
            "title": self.title,
            "author": self.author,
            "year": self.year,
            "category": self.category,
            "copies": self.copies,
            "isLoaned": is_loaned,
            "borrow_count": self.borrow_count,
            "user_observers": observers_ids,
            "borrowed_users" : self.borrowed_users
        }


    def getDetails(self) -> dict[str, Any]:
        details = {
            "Title": self.title,
            "Author": self.author,
            "Year": self.year,
            "Genre": self.category,
            "Available Copies": self.available_copies
        }
        return details


    @staticmethod
    def from_json(json: dict[str, Any]):
        is_loaned = json["isLoaned"].strip().lower() == "yes"
        return Book.loaded_book(title= str(json["title"]), author= str(json["author"]), category=str(json["category"]),
                                copies=int(json["copies"]), prev_id = int(json["id"]), year=int(json["year"]),
                                followers_ids=ast.literal_eval(json["user_observers"]),borrow_count=int(json["borrow_count"]),
                                borrowed_users = ast.literal_eval(json["borrowed_users"]), is_loaned = is_loaned)



#----------------- setters ----------------------

    def set_id(self, id: int):
        self.id = id

    def set_borrow_count(self, count: int):
        self.borrow_count = count

    def updateCopies(self, count: int, to_print = True):
        from Classes.library import Library
        previous_copies = self.available_copies
        self.available_copies += count
        if to_print:
            Library.getInstance().log_notify_print(to_log=f"Updated copies for '{self.title}': {previous_copies} -> {self.available_copies}",
                                                   to_print=f"Updated copies for '{self.title}': {previous_copies} -> {self.available_copies}", to_notify=None)
        if previous_copies <= 0 < self.available_copies:
            # Notify observers that the book is now available
            self.isLoaned = False
            if to_print:
                Library.getInstance().log_notify_print(to_log=f"Book '{self.title}' is now available for borrowing.",
                                                   to_print=f"Book '{self.title}' is now available for borrowing.",
                                                   to_notify=[self, f"Book '{self.title}' from your waiting list is now available for borrowing."])
        if self.available_copies <=0 :
            self.isLoaned = True



