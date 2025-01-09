

class LibraryException(Exception):
    """Base class for all library-related exceptions."""
    pass

class PermissionDeniedException(LibraryException):
    """Exception raised for permission-related errors."""
    def __init__(self, action):
        self.action = action
        super().__init__(f"Permission denied for action: {self.action}")

class BookNotFoundException(LibraryException):
    """Exception raised when a book is not found."""
    def __init__(self, book_title):
        self.book_title = book_title
        super().__init__(f"Book '{self.book_title}' not found.")