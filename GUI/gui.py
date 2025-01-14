import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from typing import Optional

from Classes.library import Library
from Classes.user import User, Librarian
from Classes.book import Book
from logger import Logger
from strategy import SearchByTitle, SearchByAuthor, SearchByCategory
from exceptions import PermissionDeniedException


class LibraryGUI:
    """
    Main GUI for the Library system with:
      - Role-based display (librarian vs. user vs. guest)
      - Borrowed books in green
      - Return button in green for user's borrowed book
      - Lend/Return at bottom-right
      - Search text box above book list
      - Export to CSV button
    """

    def __init__(self, root: tk.Toplevel, current_user: Optional[User] = None):
        self.root = root
        self.root.title("Library Management System")

        self.logger = Logger()
        self.library = Library.getInstance()
        self.current_user = current_user  # None => guest

        self.book_listbox = None
        self.details_label = None
        self.search_entry = None
        self.lend_button = None
        self.return_button = None

        self.create_widgets()

    def create_widgets(self):
        """Build the main library GUI layout."""
        is_librarian = self.current_user.role = "librarian"
        is_guest = self.current_user is None

        # ------ Top Frame (user-based buttons) ------
        top_frame = tk.Frame(self.root)
        top_frame.pack(side=tk.TOP, fill=tk.X, padx=5, pady=5)

        # 1) Add/Remove Book -> Only if librarian
        if is_librarian:
            tk.Button(top_frame, text="Add Book", command=self.handleAddBook).pack(
                side=tk.LEFT, padx=5
            )
            tk.Button(
                top_frame, text="Remove Book", command=self.handleRemoveBook
            ).pack(side=tk.LEFT, padx=5)

        # 2) Log In / Sign Up -> Only if guest
        if is_guest:
            tk.Button(top_frame, text="Log In", command=self.handleLogin).pack(
                side=tk.LEFT, padx=5
            )
            tk.Button(top_frame, text="Sign Up", command=self.handleRegister).pack(
                side=tk.LEFT, padx=5
            )

        # 3) Logout -> only if not guest
        if not is_guest:
            tk.Button(top_frame, text="Logout", command=self.handleLogout).pack(
                side=tk.LEFT, padx=5
            )

        # 4) Export to CSV button -> always shown (or only if user is librarian, your choice).
        # We'll show it always for demonstration.
        export_button = tk.Button(
            top_frame, text="Export to CSV", command=self.handleExportToCSV
        )
        export_button.pack(side=tk.LEFT, padx=5)

        # ------ Main Frame (Search + Book List + Details + Lend/Return) ------
        main_frame = tk.Frame(self.root)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        # Search section above the list
        search_frame = tk.Frame(main_frame)
        search_frame.pack(side=tk.TOP, fill=tk.X, pady=5)

        tk.Label(search_frame, text="Search:").pack(side=tk.LEFT, padx=5)
        self.search_entry = tk.Entry(search_frame, width=30)
        self.search_entry.pack(side=tk.LEFT, padx=5)

        tk.Button(search_frame, text="Apply", command=self.perform_search).pack(
            side=tk.LEFT, padx=5
        )

        # Content -> Book list + details
        content_frame = tk.Frame(main_frame)
        content_frame.pack(side=tk.TOP, fill=tk.BOTH, expand=True)

        # Left: Book list
        left_frame = tk.Frame(content_frame)
        left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        scrollbar = tk.Scrollbar(left_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        self.book_listbox = tk.Listbox(left_frame, yscrollcommand=scrollbar.set)
        self.book_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.config(command=self.book_listbox.yview)
        self.book_listbox.bind("<<ListboxSelect>>", self.on_book_select)

        # Right: Details
        right_frame = tk.Frame(content_frame)
        right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

        self.details_label = tk.Label(
            right_frame,
            text="Select a book to see details.",
            anchor="nw",
            justify=tk.LEFT,
        )
        self.details_label.pack(side=tk.TOP, fill=tk.BOTH, expand=True)

        # Bottom-right: Lend/Return
        bottom_right_frame = tk.Frame(right_frame)
        bottom_right_frame.pack(side=tk.BOTTOM, anchor="se", pady=10)

        if not is_guest and self.current_user.has_permission("borrow"):
            self.lend_button = tk.Button(
                bottom_right_frame, text="Lend Book", command=self.handleLendBook
            )
            self.lend_button.pack(side=tk.LEFT, padx=5)

        if not is_guest and self.current_user.has_permission("return"):
            self.return_button = tk.Button(
                bottom_right_frame, text="Return Book", command=self.handleReturnBook
            )
            self.return_button.pack(side=tk.LEFT, padx=5)

        # Populate list
        self.populate_book_list()

    # ------------------ Populate & Refresh ------------------ #
    def populate_book_list(self):
        """
        Clears and repopulates the book list with all books in the library.
        If current_user has borrowed a book, highlight that entry in green.
        """
        self.book_listbox.delete(0, tk.END)
        for i, book in enumerate(self.library.books.values()):
            self.book_listbox.insert(tk.END, book.title)
            if self.current_user and book in getattr(
                self.current_user, "borrowedBooks", []
            ):
                self.book_listbox.itemconfig(i, bg="green")

    def on_book_select(self, event):
        """Display details for the selected book. If user has it borrowed, add a line and make Return button green."""
        selection = event.widget.curselection()
        if not selection:
            return
        index = selection[0]
        btitle = event.widget.get(index)
        book = next((b for b in self.library.books.values() if b.title == btitle), None)
        if not book:
            return

        # Basic details
        details = (
            f"Title: {book.title}\n"
            f"Author: {book.author}\n"
            f"Year: {book.year}\n"
            f"Genre: {book.category}\n"
            f"Available Copies: {book.copies}"
        )

        # If user borrowed => add a line + color Return button
        if self.current_user and book in getattr(
            self.current_user, "borrowedBooks", []
        ):
            details += "\nYou have borrowed this book."
            if self.return_button:
                self.return_button.config(bg="green")
        else:
            # revert return button color
            if self.return_button:
                self.return_button.config(bg="SystemButtonFace")

        self.details_label.config(text=details)

    # ------------------ SEARCH ------------------ #
    def perform_search(self):
        criteria = self.search_entry.get().strip()
        if not criteria:
            # Revert to showing all books if no search criteria are provided
            self.populate_book_list()
            return

        # Combine results from all search criteria
        title_results = self.library.searchBooks(criteria, SearchByTitle())
        author_results = self.library.searchBooks(criteria, SearchByAuthor())
        category_results = self.library.searchBooks(criteria, SearchByCategory())

        # Use a set to avoid duplicate entries and merge results
        all_results = {
            book for book in title_results + author_results + category_results
        }

        # Update the listbox with the combined search results
        self.book_listbox.delete(0, tk.END)
        for i, book in enumerate(all_results):
            self.book_listbox.insert(tk.END, book.title)
            if self.current_user and book in getattr(
                self.current_user, "borrowedBooks", []
            ):
                self.book_listbox.itemconfig(i, bg="green")

    # ------------------ Button Handlers ------------------ #
    def handleAddBook(self):
        if not self.current_user:
            messagebox.showwarning("Warning", "You must be logged in to add books.")
            return
        if not self.current_user.has_permission("manage_books"):
            messagebox.showwarning("Warning", "No permission to add books.")
            return

        add_win = tk.Toplevel(self.root)
        add_win.title("Add Book")

        tk.Label(add_win, text="Title:").grid(row=0, column=0, padx=5, pady=5)
        title_ent = tk.Entry(add_win)
        title_ent.grid(row=0, column=1, padx=5, pady=5)

        tk.Label(add_win, text="Author:").grid(row=1, column=0, padx=5, pady=5)
        author_ent = tk.Entry(add_win)
        author_ent.grid(row=1, column=1, padx=5, pady=5)

        tk.Label(add_win, text="Year:").grid(row=2, column=0, padx=5, pady=5)
        year_ent = tk.Entry(add_win)
        year_ent.grid(row=2, column=1, padx=5, pady=5)

        tk.Label(add_win, text="Genre:").grid(row=3, column=0, padx=5, pady=5)
        genre_ent = tk.Entry(add_win)
        genre_ent.grid(row=3, column=1, padx=5, pady=5)

        tk.Label(add_win, text="Copies:").grid(row=4, column=0, padx=5, pady=5)
        copies_ent = tk.Entry(add_win)
        copies_ent.grid(row=4, column=1, padx=5, pady=5)

        def confirm_add():
            from Classes.book import Book

            title = title_ent.get().strip()
            author = author_ent.get().strip()
            try:
                year = int(year_ent.get().strip())
                genre = genre_ent.get().strip()
                copies = int(copies_ent.get().strip())
                book = Book.createBook(title, author, year, genre, copies)
                self.library.addBook(book, self.current_user)
                self.populate_book_list()
                self.logger.log(f"{self.current_user.username} added '{title}'.")
                messagebox.showinfo("Success", f"Book '{title}' added.")
                add_win.destroy()
            except ValueError:
                messagebox.showerror(
                    "Error", "Numeric values required for year/copies."
                )
            except PermissionDeniedException:
                messagebox.showerror("Error", "No permission to add books.")

        tk.Button(add_win, text="Add", command=confirm_add).grid(
            row=5, column=0, columnspan=2, pady=10
        )

    def handleRemoveBook(self):
        if not self.current_user:
            messagebox.showwarning("Warning", "Must be logged in to remove books.")
            return
        if not self.current_user.has_permission("manage_books"):
            messagebox.showwarning("Warning", "No permission to remove books.")
            return

        remove_win = tk.Toplevel(self.root)
        remove_win.title("Remove Book")

        tk.Label(remove_win, text="Select Book to Remove:").pack(padx=5, pady=5)
        book_titles = [b.title for b in self.library.books.values()]
        if not book_titles:
            messagebox.showinfo("Info", "No books in the library.")
            remove_win.destroy()
            return

        sel_var = tk.StringVar(value=book_titles[0])
        combo = ttk.Combobox(
            remove_win, textvariable=sel_var, values=book_titles, state="readonly"
        )
        combo.pack(padx=5, pady=5)

        def confirm_remove():
            title = sel_var.get()
            book = next((b for b in self.library.books.values() if b.title == title), None)
            if not book:
                messagebox.showerror("Error", "Book not found.")
                return
            try:
                self.library.removeBook(book, self.current_user)
                self.populate_book_list()
                self.logger.log(f"{self.current_user.username} removed '{title}'.")
                messagebox.showinfo("Success", f"Book '{title}' removed.")
                remove_win.destroy()
            except PermissionDeniedException:
                messagebox.showerror("Error", "No permission to remove books.")

        tk.Button(remove_win, text="Remove", command=confirm_remove).pack(pady=10)

    def handleLendBook(self):
        if not self.current_user:
            messagebox.showwarning("Warning", "Must be logged in to lend books.")
            return
        if not self.current_user.has_permission("borrow"):
            messagebox.showwarning("Warning", "No permission to borrow.")
            return

        sel = self.book_listbox.curselection()
        if not sel:
            messagebox.showinfo("Info", "Select a book from the list first.")
            return
        idx = sel[0]
        btitle = self.book_listbox.get(idx)
        book = next((b for b in self.library.books.values() if b.title == btitle), None)
        if book:
            success = self.library.lendBook(self.current_user, book)
            if success:
                self.populate_book_list()
                messagebox.showinfo("Success", f"You borrowed '{btitle}'.")
            else:
                messagebox.showwarning(
                    "Warning",
                    f"No copies available for '{btitle}'. Subscribed for notifications.",
                )

    def handleReturnBook(self):
        if not self.current_user:
            messagebox.showwarning("Warning", "Must be logged in to return books.")
            return
        if not self.current_user.has_permission("return"):
            messagebox.showwarning("Warning", "No permission to return books.")
            return

        sel = self.book_listbox.curselection()
        if not sel:
            messagebox.showinfo("Info", "Select a book from the list first.")
            return
        idx = sel[0]
        btitle = self.book_listbox.get(idx)
        book = next((b for b in self.library.books.values() if b.title == btitle), None)
        if book:
            success = self.library.returnBook(self.current_user, book)
            if success:
                self.populate_book_list()
                messagebox.showinfo("Success", f"You returned '{btitle}'.")
            else:
                messagebox.showerror("Error", f"You do not have '{btitle}' borrowed.")

    def handleLogin(self):
        from login_gui import LoginGUI

        new_win = tk.Toplevel(self.root)
        LoginGUI(new_win)

    def handleRegister(self):
        from login_gui import LoginGUI

        new_win = tk.Toplevel(self.root)
        LoginGUI(new_win, signup_mode=True)

    def handleLogout(self):
        if self.current_user:
            messagebox.showinfo("Logout", f"Goodbye, {self.current_user.username}!")
        else:
            messagebox.showinfo("Logout", "Guest session ended.")
        self.root.destroy()

    # ------------------ Export to CSV Handler ------------------ #
    def handleExportToCSV(self):
        """
        Asks for two CSV file paths: one for books, one for users.
        Then calls a library method to export the updated data.
        """
        from tkinter import filedialog

        # Choose path for Books CSV
        books_path = filedialog.asksaveasfilename(
            title="Export Books CSV",
            defaultextension=".csv",
            filetypes=[("CSV files", "*.csv"), ("All files", "*.*")],
        )
        if not books_path:
            return  # user canceled

        # Choose path for Users CSV
        users_path = filedialog.asksaveasfilename(
            title="Export Users CSV",
            defaultextension=".csv",
            filetypes=[("CSV files", "*.csv"), ("All files", "*.*")],
        )
        if not users_path:
            return  # user canceled

        try:
            self.library.export_data_to_csv(books_path, users_path)
            messagebox.showinfo("Export", "Data exported successfully!")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to export data: {e}")
