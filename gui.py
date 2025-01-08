# gui.py
import tkinter as tk
from tkinter import ttk, messagebox
from library import Library
from book import Book
from user import User
from logger import Logger
from strategy import SearchByTitle, SearchByAuthor, SearchByCategory
import csv
import os

class LibraryGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Library Management System")
        self.logger = Logger()
        self.library = Library.getInstance()
        self.current_user = None  # Track the logged-in user

        # Load books from CSV
        csv_file_path = r"C:\Users\thele\Documents\PythonProject\oop_ex_3\books2.csv"
        self.library.load_books_from_csv(csv_file_path)

        # Create frames
        self.create_widgets()

    def create_widgets(self):
        # Top frame for buttons
        top_frame = tk.Frame(self.root)
        top_frame.pack(side=tk.TOP, fill=tk.X, padx=5, pady=5)

        # Buttons
        self.add_book_button = tk.Button(top_frame, text="Add Book", command=self.handleAddBook)
        self.add_book_button.pack(side=tk.LEFT, padx=5)

        self.remove_book_button = tk.Button(top_frame, text="Remove Book", command=self.handleRemoveBook)
        self.remove_book_button.pack(side=tk.LEFT, padx=5)

        self.search_book_button = tk.Button(top_frame, text="Search Book", command=self.handleSearchBook)
        self.search_book_button.pack(side=tk.LEFT, padx=5)

        self.view_books_button = tk.Button(top_frame, text="View Books", command=self.handleViewBooks)
        self.view_books_button.pack(side=tk.LEFT, padx=5)

        self.lend_book_button = tk.Button(top_frame, text="Lend Book", command=self.handleLendBook)
        self.lend_book_button.pack(side=tk.LEFT, padx=5)

        self.return_book_button = tk.Button(top_frame, text="Return Book", command=self.handleReturnBook)
        self.return_book_button.pack(side=tk.LEFT, padx=5)

        self.popular_books_button = tk.Button(top_frame, text="Popular Books", command=self.handlePopularBooks)
        self.popular_books_button.pack(side=tk.LEFT, padx=5)

        self.login_button = tk.Button(top_frame, text="Login", command=self.handleLogin)
        self.login_button.pack(side=tk.LEFT, padx=5)

        self.register_button = tk.Button(top_frame, text="Register", command=self.handleRegister)
        self.register_button.pack(side=tk.LEFT, padx=5)

        self.logout_button = tk.Button(top_frame, text="Logout", command=self.handleLogout, state=tk.DISABLED)
        self.logout_button.pack(side=tk.LEFT, padx=5)

        # Main frame
        main_frame = tk.Frame(self.root)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        # Left frame for book list
        left_frame = tk.Frame(main_frame)
        left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        # Scrollbar for book list
        scrollbar = tk.Scrollbar(left_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        # Listbox for books
        self.book_listbox = tk.Listbox(left_frame, yscrollcommand=scrollbar.set)
        self.book_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.config(command=self.book_listbox.yview)

        self.book_listbox.bind('<<ListboxSelect>>', self.on_book_select)

        # Right frame for book details
        right_frame = tk.Frame(main_frame)
        right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

        self.details_label = tk.Label(right_frame, text="Select a book to see details.", justify=tk.LEFT, anchor='nw')
        self.details_label.pack(fill=tk.BOTH, expand=True)

        # Populate the book list
        self.populate_book_list()

    def populate_book_list(self):
        self.book_listbox.delete(0, tk.END)
        for book in self.library.books:
            self.book_listbox.insert(tk.END, book.title)

    def on_book_select(self, event):
        selection = event.widget.curselection()
        if selection:
            index = selection[0]
            book_title = event.widget.get(index)
            book = next((b for b in self.library.books if b.title == book_title), None)
            if book:
                details = f"Title: {book.title}\nAuthor: {book.author}\nYear: {book.year}\nGenre: {book.category}\nAvailable Copies: {book.copies}"
                self.details_label.config(text=details)

    def handleAddBook(self):
        if not self.current_user:
            messagebox.showwarning("Warning", "You need to be logged in to add books.")
            return

        if "add" not in self.current_user.permissions:
            messagebox.showwarning("Warning", "You do not have permission to add books.")
            return

        add_window = tk.Toplevel(self.root)
        add_window.title("Add Book")

        tk.Label(add_window, text="Title:").grid(row=0, column=0, padx=5, pady=5)
        title_entry = tk.Entry(add_window)
        title_entry.grid(row=0, column=1, padx=5, pady=5)

        tk.Label(add_window, text="Author:").grid(row=1, column=0, padx=5, pady=5)
        author_entry = tk.Entry(add_window)
        author_entry.grid(row=1, column=1, padx=5, pady=5)

        tk.Label(add_window, text="Year:").grid(row=2, column=0, padx=5, pady=5)
        year_entry = tk.Entry(add_window)
        year_entry.grid(row=2, column=1, padx=5, pady=5)

        tk.Label(add_window, text="Genre:").grid(row=3, column=0, padx=5, pady=5)
        genre_entry = tk.Entry(add_window)
        genre_entry.grid(row=3, column=1, padx=5, pady=5)

        tk.Label(add_window, text="Copies:").grid(row=4, column=0, padx=5, pady=5)
        copies_entry = tk.Entry(add_window)
        copies_entry.grid(row=4, column=1, padx=5, pady=5)

        def add_book():
            title = title_entry.get().strip()
            author = author_entry.get().strip()
            try:
                year = int(year_entry.get().strip())
                genre = genre_entry.get().strip()
                copies = int(copies_entry.get().strip())
                if copies < 0:
                    raise ValueError
                book = Book.createBook(title, author, year, genre, copies)
                self.library.addBook(book)
                self.populate_book_list()
                self.logger.log(f"Book '{title}' added by {self.current_user.username}.")
                messagebox.showinfo("Success", f"Book '{title}' added successfully.")
                add_window.destroy()
            except ValueError:
                messagebox.showerror("Error", "Please enter valid data.")

        add_button = tk.Button(add_window, text="Add", command=add_book)
        add_button.grid(row=5, column=0, columnspan=2, pady=10)

    def handleRemoveBook(self):
        if not self.current_user:
            messagebox.showwarning("Warning", "You need to be logged in to remove books.")
            return

        if "remove" not in self.current_user.permissions:
            messagebox.showwarning("Warning", "You do not have permission to remove books.")
            return

        remove_window = tk.Toplevel(self.root)
        remove_window.title("Remove Book")

        tk.Label(remove_window, text="Select Book to Remove:").pack(padx=5, pady=5)

        book_titles = [book.title for book in self.library.books]
        selected_book = tk.StringVar()
        selected_book.set(book_titles[0] if book_titles else "")

        book_dropdown = ttk.Combobox(remove_window, textvariable=selected_book, values=book_titles, state='readonly')
        book_dropdown.pack(padx=5, pady=5)

        def remove_book():
            title = selected_book.get()
            book = next((b for b in self.library.books if b.title == title), None)
            if book:
                self.library.removeBook(book)
                self.populate_book_list()
                self.logger.log(f"Book '{title}' removed by {self.current_user.username}.")
                messagebox.showinfo("Success", f"Book '{title}' removed successfully.")
                remove_window.destroy()
            else:
                messagebox.showerror("Error", "Selected book not found.")

        remove_button = tk.Button(remove_window, text="Remove", command=remove_book)
        remove_button.pack(pady=10)

    def handleSearchBook(self):
        search_window = tk.Toplevel(self.root)
        search_window.title("Search Book")

        tk.Label(search_window, text="Search by:").grid(row=0, column=0, padx=5, pady=5)
        search_by = tk.StringVar()
        search_by.set("Title")
        search_options = ["Title", "Author", "Category"]
        search_dropdown = ttk.Combobox(search_window, textvariable=search_by, values=search_options, state='readonly')
        search_dropdown.grid(row=0, column=1, padx=5, pady=5)

        tk.Label(search_window, text="Search criteria:").grid(row=1, column=0, padx=5, pady=5)
        criteria_entry = tk.Entry(search_window)
        criteria_entry.grid(row=1, column=1, padx=5, pady=5)

        results_listbox = tk.Listbox(search_window, width=50)
        results_listbox.grid(row=2, column=0, columnspan=2, padx=5, pady=5)

        def perform_search():
            criteria = criteria_entry.get().strip()
            if not criteria:
                messagebox.showwarning("Warning", "Please enter search criteria.")
                return
            option = search_by.get()
            if option == "Title":
                strategy = SearchByTitle()
            elif option == "Author":
                strategy = SearchByAuthor()
            elif option == "Category":
                strategy = SearchByCategory()
            else:
                messagebox.showerror("Error", "Invalid search option.")
                return
            results = self.library.searchBooks(criteria, strategy)
            results_listbox.delete(0, tk.END)
            for book in results:
                results_listbox.insert(tk.END, book.title)

        search_button = tk.Button(search_window, text="Search", command=perform_search)
        search_button.grid(row=3, column=0, columnspan=2, pady=5)

        results_listbox.bind('<<ListboxSelect>>', self.on_search_result_select)

    def on_search_result_select(self, event):
        selection = event.widget.curselection()
        if selection:
            index = selection[0]
            book_title = event.widget.get(index)
            book = next((b for b in self.library.books if b.title == book_title), None)
            if book:
                messagebox.showinfo("Book Details", f"Title: {book.title}\nAuthor: {book.author}\nYear: {book.year}\nGenre: {book.category}\nAvailable Copies: {book.copies}")

    def handleViewBooks(self):
        # Since the book list is already displayed, perhaps focus on it
        if self.library.books:
            self.book_listbox.select_set(0)
            self.book_listbox.event_generate("<<ListboxSelect>>")
        else:
            messagebox.showinfo("Info", "No books available in the library.")

    def handleLendBook(self):
        if not self.current_user:
            messagebox.showwarning("Warning", "You need to be logged in to lend books.")
            return

        lend_window = tk.Toplevel(self.root)
        lend_window.title("Lend Book")

        tk.Label(lend_window, text="Select Book to Lend:").pack(padx=5, pady=5)

        book_titles = [book.title for book in self.library.books if book.copies > 0]
        if not book_titles:
            messagebox.showinfo("Info", "No books available for lending.")
            lend_window.destroy()
            return

        selected_book = tk.StringVar()
        selected_book.set(book_titles[0])

        book_dropdown = ttk.Combobox(lend_window, textvariable=selected_book, values=book_titles, state='readonly')
        book_dropdown.pack(padx=5, pady=5)

        def lend_book():
            title = selected_book.get()
            book = next((b for b in self.library.books if b.title == title), None)
            if book:
                success = self.library.lendBook(self.current_user, book)
                if success:
                    self.populate_book_list()
                    self.logger.log(f"{self.current_user.username} borrowed '{title}'.")
                    messagebox.showinfo("Success", f"You have borrowed '{title}'.")
                else:
                    self.logger.log(f"{self.current_user.username} attempted to borrow '{title}', but no copies were available.")
                    messagebox.showwarning("Warning", f"No copies available for '{title}'. You have been subscribed for notifications.")
                lend_window.destroy()
            else:
                messagebox.showerror("Error", "Selected book not found.")

        lend_button = tk.Button(lend_window, text="Lend", command=lend_book)
        lend_button.pack(pady=10)

    def handleReturnBook(self):
        if not self.current_user:
            messagebox.showwarning("Warning", "You need to be logged in to return books.")
            return

        if not self.current_user.borrowedBooks:
            messagebox.showinfo("Info", "You have no borrowed books.")
            return

        return_window = tk.Toplevel(self.root)
        return_window.title("Return Book")

        tk.Label(return_window, text="Select Book to Return:").pack(padx=5, pady=5)

        book_titles = [book.title for book in self.current_user.borrowedBooks]
        selected_book = tk.StringVar()
        selected_book.set(book_titles[0])

        book_dropdown = ttk.Combobox(return_window, textvariable=selected_book, values=book_titles, state='readonly')
        book_dropdown.pack(padx=5, pady=5)

        def return_book():
            title = selected_book.get()
            book = next((b for b in self.current_user.borrowedBooks if b.title == title), None)
            if book:
                success = self.library.returnBook(self.current_user, book)
                if success:
                    self.populate_book_list()
                    self.logger.log(f"{self.current_user.username} returned '{title}'.")
                    messagebox.showinfo("Success", f"You have returned '{title}'.")
                else:
                    self.logger.log(f"{self.current_user.username} attempted to return '{title}', but did not have it borrowed.")
                    messagebox.showerror("Error", f"You do not have '{title}' borrowed.")
                return_window.destroy()
            else:
                messagebox.showerror("Error", "Selected book not found.")

        return_button = tk.Button(return_window, text="Return", command=return_book)
        return_button.pack(pady=10)

    def handleLogout(self):
        if self.current_user:
            self.logger.log(f"{self.current_user.username} logged out.")
            messagebox.showinfo("Logout", f"Goodbye, {self.current_user.username}!")
            self.current_user = None
            self.logout_button.config(state=tk.DISABLED)
            self.login_button.config(state=tk.NORMAL)
            self.register_button.config(state=tk.NORMAL)
        else:
            messagebox.showwarning("Warning", "No user is currently logged in.")

    def handleLogin(self):
        login_window = tk.Toplevel(self.root)
        login_window.title("Login")

        tk.Label(login_window, text="Username:").grid(row=0, column=0, padx=5, pady=5)
        username_entry = tk.Entry(login_window)
        username_entry.grid(row=0, column=1, padx=5, pady=5)

        tk.Label(login_window, text="Password:").grid(row=1, column=0, padx=5, pady=5)
        password_entry = tk.Entry(login_window, show="*")
        password_entry.grid(row=1, column=1, padx=5, pady=5)

        def login():
            username = username_entry.get().strip()
            password = password_entry.get().strip()
            user = next((u for u in self.library.users if u.username == username and u.passwordHash == password), None)
            if user:
                self.current_user = user
                self.logout_button.config(state=tk.NORMAL)
                self.login_button.config(state=tk.DISABLED)
                self.register_button.config(state=tk.DISABLED)
                self.logger.log(f"{username} logged in.")
                messagebox.showinfo("Login", f"Welcome, {username}!")
                login_window.destroy()
            else:
                messagebox.showerror("Error", "Invalid credentials.")

        login_button = tk.Button(login_window, text="Login", command=login)
        login_button.grid(row=2, column=0, columnspan=2, pady=10)

    def handleRegister(self):
        register_window = tk.Toplevel(self.root)
        register_window.title("Register")

        tk.Label(register_window, text="Username:").grid(row=0, column=0, padx=5, pady=5)
        username_entry = tk.Entry(register_window)
        username_entry.grid(row=0, column=1, padx=5, pady=5)

        tk.Label(register_window, text="Password:").grid(row=1, column=0, padx=5, pady=5)
        password_entry = tk.Entry(register_window, show="*")
        password_entry.grid(row=1, column=1, padx=5, pady=5)

        tk.Label(register_window, text="Permissions:").grid(row=2, column=0, padx=5, pady=5)
        permissions_var = tk.StringVar(value="borrow")
        permissions_entry = tk.Entry(register_window, textvariable=permissions_var)
        permissions_entry.grid(row=2, column=1, padx=5, pady=5)
        tk.Label(register_window, text="(e.g., borrow, add, remove)").grid(row=2, column=2, padx=5, pady=5)

        def register():
            username = username_entry.get().strip()
            password = password_entry.get().strip()
            permissions = [perm.strip() for perm in permissions_var.get().split(',')]
            if not username or not password:
                messagebox.showerror("Error", "Username and password cannot be empty.")
                return
            if any(u.username == username for u in self.library.users):
                messagebox.showerror("Error", "Username already exists.")
                return
            user = User(username, password, permissions)
            self.library.users.append(user)
            user.register(password)
            self.logger.log(f"User '{username}' registered.")
            messagebox.showinfo("Register", f"User '{username}' registered successfully.")
            register_window.destroy()

        register_button = tk.Button(register_window, text="Register", command=register)
        register_button.grid(row=3, column=0, columnspan=3, pady=10)

    def handlePopularBooks(self):
        # Placeholder for popular books feature
        messagebox.showinfo("Popular Books", "Popular books feature not implemented yet.")
