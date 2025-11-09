#  Library Management System
Object-Oriented Programming Course Project — Grade: 100/100
A Python-based desktop application for managing books, users, and library operations with a Tkinter GUI and solid OOP design patterns.

## Overview
The Library Management System is a complete desktop solution built in Python with a Tkinter graphical interface.
It allows librarians and regular users to manage books, borrow and return items, and receive notifications — all while demonstrating modular, maintainable, and testable object-oriented architecture.

---



## Features

- **User Roles**:
  - Regular Users: Borrow/return books, view borrowed history, manage notifications.
  - Librarians: Add/remove/update books, manage users, and access all regular-user actions.

- **Book Management**:
  - Add, remove, and edit book details (title, author, genre, etc.)
  - Attach cover images and extended descriptions using the Decorator pattern.
  - Real-time book status updates (available/borrowed).

- **Search and Filters**:
  - Search books by title, author, or category.
  - Apply filters such as "Available Books", "Popular Books", and "By Genre".
  - Search logic implemented using the Strategy pattern.

- **Notifications**:
  - Subscribe to book availability alerts.
  - Manage notifications through the Observer pattern.

---

## File Structure

```
project_directory/
|-- Classes/
|   |-- book.py               # Book class implementation
|   |-- user.py               # User and Librarian classes
|   |-- library.py            # Main library system logic
|
|-- design_patterns/
|   |-- decorator.py          # Add-on for book descriptions/covers
|   |-- strategy.py           # Search strategy patter
|   |-- observer.py           # Observer pattern implementation
|
|-- manage_files/
|   |-- csv_manager.py        # CSV file handling for users and books
|
|-- GUI/
|   |-- gui.py                # Main GUI interface
|   |-- login_gui.py          # Login and signup GUI
|
|-- data_files/               # Sample CSVs for demo data
|
|-- requirements.txt          # Python dependencies
|-- main.py                   # Entry point 
```


---

## Testing

To run tests for this project:
1. Ensure all dependencies are installed.
2. Run the test suite using `unittest`:
   ```bash
   python -m unittest discover
   ```

---
## Prerequisites
Before running this project, ensure you have the following installed on your system:

1. **Python 3.8+**
   - Download and install Python from [python.org](https://www.python.org/downloads/).

2. **Dependencies**
   - Install the required Python packages by running the following command in your terminal:
     ```bash
     pip install -r requirements.txt
     ```
---

## Creating an Executable (Optional)
To create an `.exe` file for this project:
1. Install PyInstaller:
   ```bash
   pip install pyinstaller
   ```
2. Navigate to the project directory.
3. Run the following command:
   ```bash
   pyinstaller --onefile main.py
   ```
4. The executable file will be located in the `dist/` folder.

---

## Contributions
If you wish to contribute to this project:
1. Fork the repository.
2. Create a new branch for your feature/bugfix.
3. Commit your changes and push the branch to your fork.
4. Submit a pull request to the main repository.


---

## Contact
For any questions or issues, please contact the project maintainer

