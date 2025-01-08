# main_for_prints_UI.py
from prints_user_interface import LibraryGUI

def main():
    gui = LibraryGUI()
    while True:
        gui.displayMainMenu()
        choice = input("Enter your choice: ")
        if choice == '1':
            gui.handleAddBook()
        elif choice == '2':
            gui.handleRemoveBook()
        elif choice == '3':
            gui.handleSearchBook()
        elif choice == '4':
            gui.handleViewBooks()
        elif choice == '5':
            gui.handleLendBook()
        elif choice == '6':
            gui.handleReturnBook()
        elif choice == '7':
            gui.handleLogin()
        elif choice == '8':
            gui.handleRegister()
        elif choice == '9':
            gui.handlePopularBooks()
        elif choice == '0':
            print("Exiting the Library Management System. Goodbye!")
            break
        else:
            print("Invalid choice. Please try again.")

if __name__ == "__main__":
    main()
