# Project Name: Library Management System

## Overview
This is a Library Management System built using Python with a Tkinter-based graphical user interface (GUI). It allows users to manage books, search for books, borrow/return books, and more. The project supports both regular users and librarians, with specific permissions for each role.

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

3. **Tkinter**
   - Tkinter is included by default in most Python installations. Verify its availability by running:
     ```bash
     python -m tkinter
     ```

---

## Installation

### Clone the Repository
1. Open your terminal or command prompt.
2. Clone the project repository from GitHub:
   ```bash
   git clone <repository_url>
   ```
   Replace `<repository_url>` with the actual URL of this project's GitHub repository.

3. Navigate to the project directory:
   ```bash
   cd <project_directory>
   ```

---

## Running the Project

### Option 1: Run via Python Interpreter
1. Open your terminal or command prompt.
2. Navigate to the main directory containing the `main.py` file.
3. Run the program:
   ```bash
   python main.py
   ```

### Option 2: Run as Executable (Optional)
If you have already created an `.exe` file using PyInstaller, navigate to the folder containing the `.exe` and double-click the file to run the application.

---

## Features

- **User Roles**:
  - Regular Users: Can borrow and return books, view borrowed books, and subscribe to notifications.
  - Librarians: Can add/remove books, manage users, and perform all actions available to regular users.

- **Book Management**:
  - Add, remove, and update book details.
  - Attach descriptions and cover images to books using decorators.

- **Search and Filters**:
  - Search books by title, author, or category.
  - Apply filters such as "Available Books", "Popular Books", and "By Genre".

- **Notifications**:
  - Receive notifications for specific books.
  - Manage subscriptions to book availability notifications.

---

## File Structure

```
project_directory/
|-- Classes/
|   |-- book.py               # Book class implementation
|   |-- user.py               # User and Librarian classes
|   |-- library.py            # Library class (main system logic)
|
|-- design_patterns/
|   |-- decorator.py          # Decorators for book descriptions and cover images
|   |-- strategy.py           # Search strategies for books
|   |-- observer.py           # Observer design pattern implementation
|
|-- manage_files/
|   |-- csv_manager.py        # CSV file handling for users and books
|
|-- GUI/
|   |-- gui.py                # Main GUI implementation
|   |-- login_gui.py          # Login and signup GUI
|
|-- data_files/               # Contains sample CSV files for books and users
|
|-- requirements.txt          # Python dependencies
|-- main.py                   # Entry point for the program
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

## License
This project is licensed under the MIT License. See the `LICENSE` file for details.

---

## Contact
For any questions or issues, please contact the project maintainer at:
- Email: maintainer@example.com
- GitHub: [Your GitHub Profile](https://github.com/your-profile)

