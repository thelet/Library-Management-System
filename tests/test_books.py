import unittest
from Classes.book import Book


class MockUser:
    """A mock user to simulate the Observer behavior."""
    def __init__(self, user_id, name="Mock User"):
        self.id = user_id
        self.name = name
        self.notifications = []

    def update(self, notification):
        """Simulate receiving a notification."""
        self.notifications.append(notification)


class TestBook(unittest.TestCase):

    def setUp(self):
        """Set up sample books before each test."""
        self.book = Book.createBook("Sample Title", "Sample Author", 2020, "Fiction", 5)

    def test_create_book(self):
        """Test creation of a new book."""
        self.assertEqual(self.book.title, "Sample Title")
        self.assertEqual(self.book.author, "Sample Author")
        self.assertEqual(self.book.year, 2020)
        self.assertEqual(self.book.category, "Fiction")
        self.assertEqual(self.book.copies, 5)
        self.assertEqual(self.book.available_copies, 5)
        self.assertFalse(self.book.isLoaned)

    def test_loaded_book(self):
        """Test loading a book with specific attributes."""
        loaded_book = Book.loaded_book(
            "Loaded Title",
            "Loaded Author",
            2015,
            "Non-Fiction",
            10,
            prev_id=2,
            followers_ids=[101, 102],
            borrow_count=3,
            borrowed_users=[201],
            is_loaned=True,
        )
        self.assertEqual(loaded_book.id, 2)
        self.assertEqual(loaded_book.title, "Loaded Title")
        self.assertEqual(loaded_book.author, "Loaded Author")
        self.assertEqual(loaded_book.year, 2015)
        self.assertEqual(loaded_book.category, "Non-Fiction")
        self.assertEqual(loaded_book.copies, 10)
        self.assertEqual(loaded_book.available_copies, 9)  # One user borrowed it
        self.assertTrue(loaded_book.isLoaned)
        self.assertEqual(loaded_book.borrow_count, 3)
        self.assertEqual(loaded_book.borrowed_users, [201])
        self.assertEqual(loaded_book.temp_followers, [101, 102])

    def test_update_copies(self):
        """Test updating available copies."""
        self.book.updateCopies(-2)
        self.assertEqual(self.book.available_copies, 3)
        self.assertFalse(self.book.isLoaned)

        self.book.updateCopies(-3)
        self.assertEqual(self.book.available_copies, 0)
        self.assertTrue(self.book.isLoaned)

        self.book.updateCopies(1)
        self.assertEqual(self.book.available_copies, 1)
        self.assertFalse(self.book.isLoaned)

    def test_set_id(self):
        """Test setting the ID of a book."""
        self.book.set_id(10)
        self.assertEqual(self.book.id, 10)

    def test_observer_methods(self):
        """Test attaching, detaching, and notifying observers."""
        observer1 = MockUser(1, "Observer 1")
        observer2 = MockUser(2, "Observer 2")

        self.book.attach(observer1)
        self.book.attach(observer2)
        self.assertIn(observer1, self.book.user_observers)
        self.assertIn(observer2, self.book.user_observers)

        self.book.notifyObservers("Test Notification")
        self.assertEqual(observer1.notifications, ["Test Notification"])
        self.assertEqual(observer2.notifications, ["Test Notification"])

        self.book.detach(observer1)
        self.assertNotIn(observer1, self.book.user_observers)

    def test_to_json(self):
        """Test converting book to JSON."""
        self.book.attach(MockUser(1))
        json_data = self.book.to_json()
        self.assertEqual(json_data["title"], "Sample Title")
        self.assertEqual(json_data["author"], "Sample Author")
        self.assertEqual(json_data["copies"], 5)
        self.assertEqual(json_data["isLoaned"], "No")

    def test_from_json(self):
        """Test creating a book from JSON."""
        json_data = {
            "id": 1,
            "title": "JSON Title",
            "author": "JSON Author",
            "year": 2021,
            "category": "Drama",
            "copies": 4,
            "isLoaned": "Yes",
            "borrow_count": 2,
            "user_observers": "[1, 2]",
            "borrowed_users": "[3]",
        }
        book_from_json = Book.from_json(json_data)
        self.assertEqual(book_from_json.title, "JSON Title")
        self.assertEqual(book_from_json.author, "JSON Author")
        self.assertEqual(book_from_json.copies, 4)
        self.assertTrue(book_from_json.isLoaned)
        self.assertEqual(book_from_json.borrowed_users, [3])

    def test_get_details(self):
        """Test retrieving book details."""
        details = self.book.getDetails()
        self.assertEqual(details["Title"], "Sample Title")
        self.assertEqual(details["Author"], "Sample Author")
        self.assertEqual(details["Year"], 2020)
        self.assertEqual(details["Genre"], "Fiction")
        self.assertEqual(details["Available Copies"], 5)


if __name__ == "__main__":
    unittest.main()
