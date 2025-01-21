# # test_library.py
# import unittest
# from Classes.library import Library
# from Classes.book import Book
# from Classes.user import User, Librarian
# from design_patterns.exceptions import PermissionDeniedException, BookNotFoundException, SignUpError
#
#
# class TestLibrary(unittest.TestCase):
#
#     def setUp(self):
#         # Reset the singleton instance for testing
#         Library._instance = None
#         self.library = Library.getInstance()
#         self.user = User("test_user", "12345")
#         self.librarian = Librarian("test_librarian", "admin123")
#         self.book = Book(1, "Test Book", "Author", 10, 0)
#
#     def test_sign_up_user(self):
#         user_params = {"username": "new_user", "password": "password", "role": "regular user"}
#         user = self.library.signUp(user_params)
#         self.assertIn(user.id, self.library.users)
#         self.assertEqual(user.username, "new_user")
#
#     def test_sign_up_librarian(self):
#         librarian_params = {"username": "new_librarian", "password": "adminpass", "role": "librarian"}
#         librarian = self.library.signUp(librarian_params)
#         self.assertIn(librarian.id, self.library.users)
#         self.assertEqual(librarian.username, "new_librarian")
#
#     def test_sign_up_existing_user(self):
#         user_params = {"username": "test_user", "password": "password", "role": "regular user"}
#         self.library.signUp(user_params)
#         with self.assertRaises(SignUpError):
#             self.library.signUp(user_params)
#
#     def test_add_book_permission_denied(self):
#         with self.assertRaises(PermissionDeniedException):
#             self.library.addBook(self.book, caller=self.user)
#
#     def test_add_book(self):
#         self.library.addBook(self.book, caller=self.librarian)
#         self.assertIn(self.book.id, self.library.books)
#
#     def test_remove_book(self):
#         self.library.addBook(self.book, caller=self.librarian)
#         self.library.removeBook(self.book, caller=self.librarian)
#         self.assertNotIn(self.book.id, self.library.books)
#
#     def test_remove_nonexistent_book(self):
#         with self.assertRaises(BookNotFoundException):
#             self.library.removeBook(self.book, caller=self.librarian)
#
#     def test_lend_book(self):
#         self.library.addBook(self.book, caller=self.librarian)
#         self.library.lendBook(self.user, self.book)
#         self.assertIn(self.book, self.user.borrowedBooks)
#
#     def test_lend_book_no_copies(self):
#         book = Book(2, "Out of Stock Book", "Author", 0, 0)
#         self.library.addBook(book, caller=self.librarian)
#         result = self.library.lendBook(self.user, book)
#         self.assertFalse(result)
#
#     def test_return_book(self):
#         self.library.addBook(self.book, caller=self.librarian)
#         self.library.lendBook(self.user, self.book)
#         self.library.returnBook(self.user, self.book)
#         self.assertNotIn(self.book, self.user.borrowedBooks)
#
#     def test_return_book_not_borrowed(self):
#         with self.assertRaises(PermissionDeniedException):
#             self.library.returnBook(self.user, self.book)
#
#
# if __name__ == "__main__":
#     unittest.main()
