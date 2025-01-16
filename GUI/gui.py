import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from typing import Optional

from Classes.library import Library
from Classes.user import User, Librarian
from Classes.book import Book
from decorator import DescriptionDecorator, CoverDecorator
from logger import Logger
from strategy import SearchByTitle, SearchByAuthor, SearchByCategory
from exceptions import PermissionDeniedException


class LibraryGUI:
    """
    GUI for the Library system, with the following improvements:
      1) A Filter combobox next to the search bar, offering:
         - All Books
         - By Genre (displays a second genre combobox)
         - Popular Books  (placeholder: self.library.getPopularBooks())
         - My Books       (books the user borrowed)
         - Available Books (copies > 0)
         - Not Available Books (copies == 0)
         - Previously Loand (placeholder: current_user.prev_books)
         - Notifications (books where current_user is in user_observers)
      2) A 'Remove from Notifications' button next to 'Apply for Notifications'.
      3) is_librarian = self.current_user.role == "librarian" is unchanged.
      4) Smaller window size: 800x400.
      5) Notifications screen below the book screen, each with scrollbars.
    """

    def __init__(self, root: tk.Toplevel, current_user: Optional[User] = None):
        self.root = root
        self.root.title("Library Management System")
        self.root.geometry("800x400")  # Smaller default GUI size

        self.logger = Logger()
        self.library = Library.getInstance()
        self.current_user = current_user  # None => guest

        # Fields related to filter and search
        self.search_entry = None
        self.filter_combobox = None
        self.genre_label = None
        self.genre_combobox = None

        # Book list, details
        self.book_listbox = None
        self.details_label = None

        # Buttons
        self.lend_button = None
        self.return_button = None
        self.apply_notifications_button = None
        self.remove_notifications_button = None

        # Notifications Text
        self.notifications_text = None

        self.create_widgets()

    def create_widgets(self):
        # DO NOT CHANGE: is_librarian = self.current_user.role == "librarian"
        # (if current_user is None, this will be False)
        is_librarian = (self.current_user is not None and self.current_user.role == "librarian")
        is_guest = (self.current_user is None)

        # --- TOP FRAME (User-based buttons, CSV exports) ---
        top_frame = tk.Frame(self.root)
        top_frame.pack(side=tk.TOP, fill=tk.X, padx=5, pady=5)

        if is_librarian:
            tk.Button(top_frame, text="Add Book", command=self.handleAddBook).pack(side=tk.LEFT, padx=5)
            tk.Button(top_frame, text="Remove Book", command=self.handleRemoveBook).pack(side=tk.LEFT, padx=5)

        if is_guest:
            tk.Button(top_frame, text="Log In", command=self.handleLogin).pack(side=tk.LEFT, padx=5)
            tk.Button(top_frame, text="Sign Up", command=self.handleRegister).pack(side=tk.LEFT, padx=5)

        if not is_guest:
            tk.Button(top_frame, text="Logout", command=self.handleLogout).pack(side=tk.LEFT, padx=5)

        tk.Button(top_frame, text="Export Users CSV", command=self.handleExportUsersCSV).pack(side=tk.LEFT, padx=5)
        tk.Button(top_frame, text="Export Books CSV", command=self.handleExportBooksCSV).pack(side=tk.LEFT, padx=5)

        # --- Main frame: top (book screen), bottom (notifications) ---
        main_frame = tk.Frame(self.root)
        main_frame.pack(fill=tk.BOTH, expand=True)

        # Book screen on top
        books_frame = tk.Frame(main_frame)
        books_frame.pack(side=tk.TOP, fill=tk.BOTH, expand=True)

        self.create_book_screen(books_frame)

        # Notifications screen on bottom
        notif_frame = tk.Frame(main_frame, height=120)
        notif_frame.pack(side=tk.BOTTOM, fill=tk.X, padx=5, pady=5)
        self.create_notifications_screen(notif_frame)

        # Initial data populate
        self.populate_book_list()
        self.refresh_notifications()

    def create_book_screen(self, parent):
        """Build the top portion: search bar, filter combo, genre combo, book list, details, Lend/Return, Apply/Remove Notifs."""
        # Search + filter row
        search_frame = tk.Frame(parent)
        search_frame.pack(side=tk.TOP, fill=tk.X, pady=5)

        tk.Label(search_frame, text="Search:").pack(side=tk.LEFT, padx=5)
        self.search_entry = tk.Entry(search_frame, width=20)
        self.search_entry.pack(side=tk.LEFT, padx=5)

        # Filter combobox
        filter_options = [
            "All Books",
            "By Genre",
            "Popular Books",
            "My Books",
            "Available Books",
            "Not Available Books",
            "Previously Loand",
            "Notifications"
        ]
        self.filter_combobox = ttk.Combobox(search_frame, values=filter_options, state="readonly", width=15)
        self.filter_combobox.pack(side=tk.LEFT, padx=5)
        self.filter_combobox.set("All Books")
        self.filter_combobox.bind("<<ComboboxSelected>>", self.on_filter_selected)

        # Genre label + combobox (hidden unless "By Genre" is selected)
        self.genre_label = tk.Label(search_frame, text="Genre:")
        self.genre_label.pack_forget()

        self.genre_combobox = ttk.Combobox(search_frame, state="disabled", width=15)
        self.genre_combobox.pack_forget()
        self.genre_combobox.bind("<<ComboboxSelected>>", self.on_genre_selected)

        # "Apply" button to trigger search + filter
        tk.Button(search_frame, text="Apply", command=self.perform_search).pack(side=tk.LEFT, padx=5)

        # Book list + details
        content_frame = tk.Frame(parent)
        content_frame.pack(side=tk.TOP, fill=tk.BOTH, expand=True)

        # Book list
        list_frame = tk.Frame(content_frame)
        list_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        scroll_books = tk.Scrollbar(list_frame)
        scroll_books.pack(side=tk.RIGHT, fill=tk.Y)

        self.book_listbox = tk.Listbox(list_frame, yscrollcommand=scroll_books.set)
        self.book_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scroll_books.config(command=self.book_listbox.yview)
        self.book_listbox.bind("<<ListboxSelect>>", self.on_book_select)

        # Details + buttons
        details_frame = tk.Frame(content_frame)
        details_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

        self.details_label = tk.Label(details_frame, text="Select a book to see details.", anchor="nw", justify=tk.LEFT)
        self.details_label.pack(side=tk.TOP, fill=tk.BOTH, expand=True, padx=5, pady=5)

        button_row = tk.Frame(details_frame)
        button_row.pack(side=tk.BOTTOM, anchor="s", pady=10)

        # Remove from notifications
        if self.current_user:
            self.remove_notifications_button = tk.Button(
                button_row, text="Remove from Notifications",
                command=self.handleRemoveFromNotifications
            )
            self.remove_notifications_button.pack(side=tk.TOP, pady=5)

        # Apply for notifications
        if self.current_user:
            self.apply_notifications_button = tk.Button(
                button_row, text="Apply for Notifications",
                command=self.handleApplyForNotifications
            )
            self.apply_notifications_button.pack(side=tk.TOP, pady=5)

        # Lend/Return
        if self.current_user and self.current_user.has_permission("borrow"):
            self.lend_button = tk.Button(button_row, text="Lend Book", command=self.handleLendBook)
            self.lend_button.pack(side=tk.TOP, pady=5)

        if self.current_user and self.current_user.has_permission("return"):
            self.return_button = tk.Button(button_row, text="Return Book", command=self.handleReturnBook)
            self.return_button.pack(side=tk.TOP, pady=5)

    def create_notifications_screen(self, parent):
        """Smaller notifications screen with a Text widget + scrollbar + refresh button (centered)."""
        parent.pack_propagate(False)
        parent.update()

        notif_scroll = tk.Scrollbar(parent)
        notif_scroll.pack(side=tk.RIGHT, fill=tk.Y)

        self.notifications_text = tk.Text(parent, wrap="word", yscrollcommand=notif_scroll.set)
        self.notifications_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        notif_scroll.config(command=self.notifications_text.yview)

        refresh_button = tk.Button(parent, text="Refresh Notifications", command=self.refresh_notifications)
        refresh_button.place(relx=0.5, rely=0.5, anchor="center")

    # ----------------- Filter / Genre ----------------- #
    def on_filter_selected(self, event):
        chosen_filter = self.filter_combobox.get()
        if chosen_filter == "By Genre":
            self.update_genre_combobox()
            self.genre_label.pack(side=tk.LEFT, padx=5)
            self.genre_combobox.pack(side=tk.LEFT, padx=5)
        else:
            self.genre_label.pack_forget()
            self.genre_combobox.pack_forget()

    def update_genre_combobox(self):
        categories = sorted({b.category for b in self.library.books.values()})
        self.genre_combobox.config(values=categories, state="readonly")
        if categories:
            self.genre_combobox.set(categories[0])
        else:
            self.genre_combobox.set("")

    def on_genre_selected(self, event):
        self.perform_filter()

    # ----------------- Book List / Notifications Refresh ----------------- #
    def populate_book_list(self):
        """Populate the book list with all library books initially."""
        self.book_listbox.delete(0, tk.END)
        for i, book in enumerate(self.library.books.values()):
            self.book_listbox.insert(tk.END, book.title)
            if self.current_user and book in getattr(self.current_user, "borrowedBooks", []):
                self.book_listbox.itemconfig(i, bg="green")

    def refresh_notifications(self):
        self.notifications_text.delete("1.0", tk.END)
        if self.current_user:
            for note in self.current_user.notifications:
                self.notifications_text.insert(tk.END, note + "\n")

    # ----------------- Searching / Filtering ----------------- #
    def perform_search(self):
        """Combine textual search with the currently chosen filter."""
        criteria = self.search_entry.get().strip()

        if criteria:
            t_res = self.library.searchBooks(criteria, SearchByTitle())
            a_res = self.library.searchBooks(criteria, SearchByAuthor())
            c_res = self.library.searchBooks(criteria, SearchByCategory())
            initial_set = set(t_res + a_res + c_res)
        else:
            initial_set = set(self.library.books.values())

        filtered = self.apply_filter_to_books(initial_set)
        self.update_book_list(filtered)

    def perform_filter(self):
        """Apply only the chosen filter, ignoring textual search."""
        initial_set = set(self.library.books.values())
        filtered = self.apply_filter_to_books(initial_set)
        self.update_book_list(filtered)

    def apply_filter_to_books(self, books_set):
        chosen_filter = self.filter_combobox.get()
        if chosen_filter == "All Books":
            return books_set
        elif chosen_filter == "By Genre":
            if self.genre_combobox:
                selected_genre = self.genre_combobox.get().strip()
                if selected_genre:
                    return {b for b in books_set if b.category == selected_genre}
            return books_set
        elif chosen_filter == "Popular Books":
            return set(self.library.getPopularBooks())
        elif chosen_filter == "My Books":
            if self.current_user:
                return {b for b in books_set if b in getattr(self.current_user, "borrowedBooks", [])}
            return set()
        elif chosen_filter == "Available Books":
            return {b for b in books_set if b.copies > 0}
        elif chosen_filter == "Not Available Books":
            return {b for b in books_set if b.copies == 0}
        elif chosen_filter == "Previously Loand":
            if self.current_user and hasattr(self.current_user, "previously_borrowed_books"):
                prev_ids = self.current_user.previously_borrowed_books  # e.g. [1, 10, 12]
                return {b for b in books_set if b.id in prev_ids}
            return set()
        elif chosen_filter == "Notifications":
            if self.current_user:
                return {b for b in books_set if self.current_user in b.user_observers}
            return set()
        return books_set

    def update_book_list(self, books_collection):
        self.book_listbox.delete(0, tk.END)
        # Sort by title
        for i, book in enumerate(sorted(books_collection, key=lambda bk: bk.title)):
            self.book_listbox.insert(tk.END, book.title)
            if self.current_user and book in getattr(self.current_user, "borrowedBooks", []):
                self.book_listbox.itemconfig(i, bg="green")

    # ----------------- Book Selection ----------------- #
    def on_book_select(self, event):
        from JSON_manager import format_json_dict
        """Show details for the selected book, highlight Return button if user has borrowed it."""
        selection = event.widget.curselection()
        if not selection:
            return
        idx = selection[0]
        btitle = event.widget.get(idx)
        book = next((b for b in self.library.books.values() if b.title == btitle), None)
        if not book:
            return
        if book.id in self.library.decorated_books:
            book = self.library.decorated_books.get(book.id)

        book_details = book.getDetails()
        if "cover_image" in book_details and book_details["cover_image"]:
            self.display_cover_image(book_details["cover_image"])
            book_details.pop("cover_image")

        details = format_json_dict(book_details)

        if self.current_user and book in getattr(self.current_user, "borrowedBooks", []):
            details += "\nYou have borrowed this book."
            if self.return_button:
                self.return_button.config(bg="green")
        else:
            if self.return_button:
                self.return_button.config(bg="SystemButtonFace")

        self.details_label.config(text=details)

    # ----------------- handles image decorator----------------- #
    def display_cover_image(self, image_path):
        """
        Display a cover image in the details_label frame.
        :param image_path: Path to the image file
        """
        try:
            from PIL import Image, ImageTk

            # Load and resize the image for display
            pil_img = Image.open(image_path)
            pil_img = pil_img.resize((150, 200))  # Resize to fit nicely
            img = ImageTk.PhotoImage(pil_img)

            # Check if a previous image exists, remove it
            if hasattr(self, "cover_image_label"):
                self.cover_image_label.destroy()

            # Create a new label to display the image
            self.cover_image_label = tk.Label(self.details_label, image=img)
            self.cover_image_label.image = img  # Keep a reference
            self.cover_image_label.pack(side=tk.RIGHT, padx=5, pady=5)

        except Exception as e:
            print(f"Failed to load cover image: {e}")

    # ----------------- Button Handlers (Add/Remove, Lend/Return, Notifs) ----------------- #
    def handleAddBook(self):
        if not self.current_user:
            messagebox.showwarning("Warning", "You must be logged in to add books.")
            return
        if not self.current_user.has_permission("manage_books"):
            messagebox.showwarning("Warning", "No permission to add books.")
            return

        add_win = tk.Toplevel(self.root)
        add_win.title("Add Book")

        # Initialize image_path variable
        image_path = tk.StringVar(value="")

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

        tk.Label(add_win, text="Description (Optional):").grid(row=5, column=0, padx=5, pady=5)
        description_ent = tk.Entry(add_win)
        description_ent.grid(row=5, column=1, padx=5, pady=5)

        # Add Book Image (Optional) Button
        def choose_image():
            file_path = filedialog.askopenfilename(
                title="Select Book Cover Image",
                filetypes=[("Image Files", "*.png;*.jpg;*.jpeg;*.gif;*.bmp"), ("All Files", "*.*")]
            )
            if file_path:
                image_path.set(file_path)

        tk.Button(add_win, text="Add Book Image (Optional)", command=choose_image).grid(row=6, column=0, columnspan=2,
                                                                                        pady=10)


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
                if description_ent.get().strip():
                    description_decorated = DescriptionDecorator(book, description_ent.get().strip())
                    self.library.decorated_books[book.id] = description_decorated
                # Add cover decorator if image_path is set
                if image_path.get():
                    cover_decorated = CoverDecorator(book, image_path.get())
                    self.library.decorated_books[book.id] =cover_decorated

                self.logger.log(f"{self.current_user.username} added '{title}'.")
                messagebox.showinfo("Success", f"Book '{title}' added.")
                # Refresh filter or default list
                self.perform_search()
                add_win.destroy()
            except ValueError:
                messagebox.showerror("Error", "Numeric values required for year/copies.")
            except PermissionDeniedException:
                messagebox.showerror("Error", "No permission to add books.")

        tk.Button(add_win, text="Add", command=confirm_add).grid(row=7, column=0, columnspan=2, pady=10)

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
        combo = ttk.Combobox(remove_win, textvariable=sel_var, values=book_titles, state="readonly")
        combo.pack(padx=5, pady=5)

        def confirm_remove():
            title = sel_var.get()
            book = next((b for b in self.library.books.values() if b.title == title), None)
            if not book:
                messagebox.showerror("Error", "Book not found.")
                return
            try:
                self.library.removeBook(book, self.current_user)
                self.logger.log(f"{self.current_user.username} removed '{title}'.")
                messagebox.showinfo("Success", f"Book '{title}' removed.")
                # Refresh filter or default list
                self.perform_search()
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
                self.logger.log(f"{self.current_user.username} borrowed '{btitle}'.")
                messagebox.showinfo("Success", f"You borrowed '{btitle}'.")
                self.perform_search()
            else:
                messagebox.showwarning("Warning", f"No copies available for '{btitle}'. Subscribed for notifications.")

    def handleReturnBook(self):
        if not self.current_user:
            messagebox.showwarning("Warning", "Must be logged in to return books.")
            return
        if not self.current_user.has_permission("return"):
            messagebox.showwarning("Warning", "No permission to return books.")
            return

        sel = self.book_listbox.curselection()
        if not sel:
            messagebox.showinfo("Info", "Select a book first.")
            return

        idx = sel[0]
        btitle = self.book_listbox.get(idx)
        book = next((b for b in self.library.books.values() if b.title == btitle), None)
        if book:
            success = self.library.returnBook(self.current_user, book)
            if success:
                self.logger.log(f"{self.current_user.username} returned '{btitle}'.")
                messagebox.showinfo("Success", f"You returned '{btitle}'.")
                self.perform_search()
            else:
                messagebox.showerror("Error", f"You do not have '{btitle}' borrowed.")

    def handleApplyForNotifications(self):
        if not self.current_user:
            messagebox.showwarning("Warning", "Must be logged in to apply for notifications.")
            return
        sel = self.book_listbox.curselection()
        if not sel:
            messagebox.showinfo("Info", "Select a book first.")
            return
        idx = sel[0]
        btitle = self.book_listbox.get(idx)
        book = next((b for b in self.library.books.values() if b.title == btitle), None)
        if book:
            if self.current_user in book.user_observers:
                messagebox.showinfo("Info", f"You are already subscribed to '{btitle}'.")
            else:
                book.attach(self.current_user)
                messagebox.showinfo("Info", f"You subscribed to notifications for '{btitle}'.")

    def handleRemoveFromNotifications(self):
        if not self.current_user:
            messagebox.showwarning("Warning", "Must be logged in to remove notifications.")
            return
        sel = self.book_listbox.curselection()
        if not sel:
            messagebox.showinfo("Info", "Select a book first.")
            return
        idx = sel[0]
        btitle = self.book_listbox.get(idx)
        book = next((b for b in self.library.books.values() if b.title == btitle), None)
        if book:
            if self.current_user in book.user_observers:
                book.detach(self.current_user)
                messagebox.showinfo("Info", f"You were removed from notifications for '{btitle}'.")
            else:
                messagebox.showinfo("Info", f"You were not subscribed to '{btitle}' notifications.")

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

    # ------------- Export CSV -------------
    def handleExportUsersCSV(self):
        csv_path = filedialog.asksaveasfilename(
            title="Export Users CSV",
            defaultextension=".csv",
            filetypes=[("CSV files", "*.csv"), ("All files", "*.*")],
        )
        if not csv_path:
            return
        try:
            self.library.export_users_to_csv(csv_path)
            messagebox.showinfo("Export", f"Users exported successfully to {csv_path}.")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to export users CSV: {e}")

    def handleExportBooksCSV(self):
        csv_path = filedialog.asksaveasfilename(
            title="Export Books CSV",
            defaultextension=".csv",
            filetypes=[("CSV files", "*.csv"), ("All files", "*.*")],
        )
        if not csv_path:
            return
        try:
            self.library.export_books_to_csv(csv_path)
            messagebox.showinfo("Export", f"Books exported successfully to {csv_path}.")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to export books CSV: {e}")
