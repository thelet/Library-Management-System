# prints_user_interface.py
from library import Library
from book import Book
from user import User
from logger import Logger
from strategy import SearchByTitle, SearchByAuthor, SearchByCategory

class LibraryGUI:
    def __init__(self):
        self.library = Library.getInstance()
        self.logger = Logger()

    def displayMainMenu(self):
        print("\n=== Library Management System ===")
        print("1. Add Book")
        print("2. Remove Book")
        print("3. Search Book")
        print("4. View Books")
        print("5. Lend Book")
        print("6. Return Book")
        print("7. Login")
        print("8. Register")
        print("9. View Notifications")
        print("0. Exit")

    def handleAddBook(self):
        title = input("Enter book title: ")
        author = input("Enter author name: ")
        try:
            year = int(input("Enter publication year: "))
            category = input("Enter category: ")
            copies = int(input("Enter number of copies: "))
            book = Book.createBook(title, author, year, category, copies)
            self.library.addBook(book)
            self.logger.log(f"Book '{title}' added to the library.")
        except ValueError as ve:
            print(f"Error: {ve}")

    def handleRemoveBook(self):
        title = input("Enter book title to remove: ")
        book = next((b for b in self.library.books if b.title == title), None)
        if book:
            self.library.removeBook(book)
            self.logger.log(f"Book '{title}' removed from the library.")
        else:
            print(f"Book '{title}' not found in the library.")

    def handleSearchBook(self):
        print("\nSearch by:")
        print("1. Title")
        print("2. Author")
        print("3. Category")
        choice = input("Choose an option: ")
        criteria = input("Enter search criteria: ")
        if choice == '1':
            strategy = SearchByTitle()
        elif choice == '2':
            strategy = SearchByAuthor()
        elif choice == '3':
            strategy = SearchByCategory()
        else:
            print("Invalid choice.")
            return
        results = self.library.searchBooks(criteria, strategy)
        print(f"\nFound {len(results)} book(s):")
        for book in results:
            print(book.getDetails())

    def handleViewBooks(self):
        print("\n=== All Books in the Library ===")
        for book in self.library.books:
            print(book.getDetails())

    def handleLendBook(self):
        username = input("Enter your username: ")
        user = next((u for u in self.library.users if u.username == username), None)
        if not user:
            print("User not found. Please register first.")
            return
        title = input("Enter book title to borrow: ")
        book = next((b for b in self.library.books if b.title == title), None)
        if not book:
            print(f"Book '{title}' not found in the library.")
            return
        success = self.library.lendBook(user, book)
        if success:
            self.logger.log(f"{user.username} borrowed '{book.title}'.")
        else:
            self.logger.log(f"{user.username} attempted to borrow '{book.title}', but no copies were available.")

    def handleReturnBook(self):
        username = input("Enter your username: ")
        user = next((u for u in self.library.users if u.username == username), None)
        if not user:
            print("User not found.")
            return
        title = input("Enter book title to return: ")
        book = next((b for b in self.library.books if b.title == title), None)
        if not book:
            print(f"Book '{title}' not found in the library.")
            return
        success = self.library.returnBook(user, book)
        if success:
            self.logger.log(f"{user.username} returned '{book.title}'.")
        else:
            self.logger.log(f"{user.username} attempted to return '{book.title}', but did not have it borrowed.")

    def handleLogin(self):
        username = input("Enter username: ")
        password = input("Enter password: ")
        user = next((u for u in self.library.users if u.username == username and u.passwordHash == password), None)
        if user:
            print(f"Welcome, {username}!")
            self.logger.log(f"{username} logged in.")
        else:
            print("Invalid credentials.")

    def handleRegister(self):
        username = input("Choose a username: ")
        password = input("Choose a password: ")
        permissions = ["borrow"]  # Default permissions
        if any(u.username == username for u in self.library.users):
            print("Username already exists. Please choose a different username.")
            return
        user = User(username, password, permissions)
        self.library.users.append(user)
        user.register(password)
        self.logger.log(f"User '{username}' registered.")

    def handlePopularBooks(self):
        # Placeholder for popular books feature
        print("Popular books feature not implemented yet.")

    def handleLogout(self):
        # Placeholder for logout functionality
        print("Logout functionality not implemented yet.")
