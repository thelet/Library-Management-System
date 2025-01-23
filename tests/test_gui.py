import os
import unittest
import tkinter as tk
from unittest.mock import patch, MagicMock
from io import StringIO

# Import your classes
from GUI.entry_gui import EntryGUI
from GUI.gui import LibraryGUI
from Classes.library import Library
from Classes.user import User, Librarian
from Classes.book import Book
from design_patterns.logger import Logger


class LoggerCaptureMixin:
    """
    Mixin that redirects Logger output to an in-memory buffer so you can
    inspect the logger messages after test steps.
    """

    def setUp(self):
        super().setUp()
        self.log_stream = StringIO()

        # Patch Logger so it writes to our StringIO instead of 'log.txt'
        # We'll keep a real Logger instance, but redirect its writes
        self.logger_patch = patch.object(Logger, 'log', side_effect=self._capture_log)
        self.mock_logger = self.logger_patch.start()

    def tearDown(self):
        self.logger_patch.stop()
        self.log_stream.close()
        super().tearDown()

    def _capture_log(self, message: str, print_to_console: bool = True):
        """
        Our custom side_effect to collect log messages in an in-memory buffer.
        """
        # Optionally bypass printing to console or do partial prints
        self.log_stream.write(f"[LOG]: {message}\n")


class TestEntryGUI(LoggerCaptureMixin, unittest.TestCase):
    """
    Tests for EntryGUI which loads CSV data and starts the system.
    """

    def setUp(self):
        super().setUp()
        # Create a hidden root window for Tkinter
        self.root = tk.Tk()
        self.root.withdraw()

        # Clear / re-initialize the Library singleton for each test
        #   (If needed, you can forcibly reset the singleton instance)
        Library._Library__instance = None
        self.library = Library.getInstance()

        self.entry_gui = EntryGUI(self.root)

    def tearDown(self):
        # Destroy the Tk root after each test
        self.root.destroy()
        super().tearDown()



class TestLibraryGUI(LoggerCaptureMixin, unittest.TestCase):
    """
    Tests for the main LibraryGUI.
    """

    def setUp(self):
        super().setUp()
        self.root = tk.Tk()
        self.root.withdraw()

        # Reset library singleton
        Library._Library__instance = None
        self.library = Library.getInstance()

        # Create a test user or librarian
        self.test_user = User.create_user("testuser", "testpassword")
        self.library.users[self.test_user.id] = self.test_user

        self.gui = LibraryGUI(self.root, self.test_user)

    def tearDown(self):
        self.root.destroy()
        super().tearDown()

    def test_handleAddBook_no_permission(self):
        """
        If a user does NOT have 'manage_books' permission, handleAddBook should
        display a warning. We'll patch messagebox to intercept the warning.
        """
        # Ensure test_user has only 'borrow'/'return' but not 'manage_books'
        self.test_user.permissions = ["borrow", "return"]
        with patch('tkinter.messagebox.showwarning') as mock_warn:
            self.gui.handleAddBook()
            mock_warn.assert_called_once()
            args, _ = mock_warn.call_args
            self.assertIn("No permission to add books.", args[1])  # second param is message

    def test_handleAddBook_librarian(self):
        """
        For a librarian user, check that the 'Add Book' process tries to open
        a Toplevel for adding details. We'll patch Toplevel to confirm it is created.
        """
        # Convert our test_user into a librarian
        self.test_user.permissions = ["borrow", "return", "manage_books"]
        self.test_user.role = "librarian"

        with patch('tkinter.Toplevel') as mock_toplevel:
            self.gui.handleAddBook()
            mock_toplevel.assert_called_once()


    def test_handleRemoveBook_success(self):
        """
        If user has permission and there's at least one book in the library,
        handleRemoveBook should remove it successfully.
        """
        # Give the user manage_books permission
        self.test_user.permissions.append("manage_books")

        # Add a sample book
        book = Book.createBook("Test Title", "Test Author", 2023, "Test Genre", 5)
        self.library.addBook(book)

        # We patch Toplevel so the user can pick which book to remove
        # We'll mock the combobox selection
        with patch('tkinter.ttk.Combobox') as mock_combo:
            instance = mock_combo.return_value
            instance.get.return_value = "Test Title"  # user "selected" our book

            with patch('tkinter.messagebox.showinfo') as mock_info:
                self.gui.handleRemoveBook()
                # Verify the library no longer has that book
                self.assertNotIn(book.id, self.library.books.keys())

                # Check success message
                mock_info.assert_called_once()
                self.assertIn("Book 'Test Title' removed.", mock_info.call_args[0][1])

        logs = self.log_stream.getvalue()
        self.assertIn("removed 'Test Title'", logs)  # from logger

    def test_handleLendBook_no_user(self):
        """
        If current_user is None, handleLendBook warns about logging in.
        We'll simulate a LibraryGUI with no user.
        """
        gui_no_user = LibraryGUI(self.root, current_user=None)
        with patch('tkinter.messagebox.showwarning') as mock_warn:
            gui_no_user.handleLendBook()
            mock_warn.assert_called_once()
            self.assertIn("Must be logged in to lend books", mock_warn.call_args[0][1])

    def test_handleLendBook_success(self):
        """
        Lend a book to the current user if it has available copies.
        """
        # Make sure user has "borrow" permission
        self.test_user.permissions = ["borrow"]

        # Add a sample book to library
        book = Book.createBook("Title Lendable", "Author", 2023, "Genre", 2)
        self.library.addBook(book, caller=None)

        # Insert it in the listbox so user can "select" it
        self.gui.update_book_list(self.library.books.values())

        # Programmatically select the first listbox item
        self.gui.book_listbox.select_set(0)
        with patch('tkinter.messagebox.showinfo') as mock_info:
            self.gui.handleLendBook()
            mock_info.assert_called_once()
            self.assertIn("You borrowed 'Title Lendable'", mock_info.call_args[0][1])

        # Check that user has the book in borrowedBooks
        self.assertIn(book, self.test_user.borrowedBooks)

        # Check logger
        logs = self.log_stream.getvalue()
        self.assertIn("testuser borrowed 'Title Lendable'", logs)

    def test_handleReturnBook_success(self):
        """
        Return a book that the current user has borrowed.
        """
        self.test_user.permissions = ["borrow", "return"]
        book = Book.createBook("Returnable Book", "SomeAuthor", 2020, "Category", 3)
        self.library.addBook(book, caller=None)

        # Lend it first so user has it
        self.library.lendBook(self.test_user, book)
        self.assertIn(book, self.test_user.borrowedBooks)

        self.gui.update_book_list(self.library.books.values())
        # Fake select in the listbox
        self.gui.book_listbox.select_set(0)

        with patch('tkinter.messagebox.showinfo') as mock_info:
            self.gui.handleReturnBook()
            mock_info.assert_called_once()
            self.assertIn("You returned 'Returnable Book'", mock_info.call_args[0][1])

        # Confirm user no longer has that book
        self.assertNotIn(book, self.test_user.borrowedBooks)

        logs = self.log_stream.getvalue()
        self.assertIn("testuser returned 'Returnable Book'", logs)

    def test_handleApplyForNotifications_already_subscribed(self):
        """
        If user is already subscribed to a book, show appropriate info.
        """
        self.test_user.permissions = ["borrow"]  # Sufficient to operate
        book = Book.createBook("Notify Book", "Author", 2021, "Category", 3)
        self.library.addBook(book, caller=None)

        # Subscribe user
        book.attach(self.test_user)

        # put it in the listbox
        self.gui.update_book_list(self.library.books.values())
        # select the book
        self.gui.book_listbox.select_set(0)

        with patch('tkinter.messagebox.showinfo') as mock_info:
            self.gui.handleApplyForNotifications()
            mock_info.assert_called_once()
            self.assertIn("You are already subscribed", mock_info.call_args[0][1])

    def test_handleApplyForNotifications_success(self):
        """
        If user is not subscribed to a book, they get attached successfully.
        """
        self.test_user.permissions = ["borrow"]
        book = Book.createBook("New Notify Book", "Author", 2020, "Category", 2)
        self.library.addBook(book, caller=None)

        self.gui.update_book_list(self.library.books.values())
        self.gui.book_listbox.select_set(0)

        with patch('tkinter.messagebox.showinfo') as mock_info:
            self.gui.handleApplyForNotifications()
            mock_info.assert_called_once()
            self.assertIn("You subscribed to notifications for 'New Notify Book'",
                          mock_info.call_args[0][1])

        self.assertIn(self.test_user, book.user_observers)

    def test_handleRemoveFromNotifications(self):
        """
        If user is subscribed to a book, removing them from notifications detaches them.
        """
        self.test_user.permissions = ["borrow"]
        book = Book.createBook("Removable Notify Book", "Author", 2020, "Category", 1)
        self.library.addBook(book, caller=None)

        book.attach(self.test_user)
        self.assertIn(self.test_user, book.user_observers)

        self.gui.update_book_list(self.library.books.values())
        self.gui.book_listbox.select_set(0)

        with patch('tkinter.messagebox.showinfo') as mock_info:
            self.gui.handleRemoveFromNotifications()
            mock_info.assert_called_once()
            self.assertIn("You were removed from notifications for 'Removable Notify Book'",
                          mock_info.call_args[0][1])

        self.assertNotIn(self.test_user, book.user_observers)


if __name__ == '__main__':
    unittest.main()
