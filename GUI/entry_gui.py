import tkinter as tk
from tkinter import filedialog, messagebox
from Classes.library import Library


class EntryGUI:
    def __init__(self, master):
        self.master = master
        self.master.title("Library Entry Screen")

        self.library = Library.getInstance()
        self.books_csv_path = None
        self.users_csv_path = None

        # Label
        tk.Label(
            self.master,
            text="Choose file path for previous library data.\nIf you want to start with an empty collection, do not load any files.",
        ).pack(pady=10)

        # Buttons
        tk.Button(
            self.master,
            text="Load Book Collection from CSV",
            command=self.load_books_csv,
        ).pack(pady=5)
        tk.Button(
            self.master,
            text="Load User Collection from CSV",
            command=self.load_users_csv,
        ).pack(pady=5)

        # Start button
        self.start_button = tk.Button(
            self.master, text="Start", bg="green", fg="white", command=self.start_system
        )
        self.start_button.pack(pady=5)

    def load_books_csv(self):
        path = filedialog.askopenfilename(
            title="Select Books CSV",
            filetypes=[("CSV files", "*.csv"), ("All files", "*.*")],
        )
        if path:
            self.books_csv_path = path
            try:
                self.library.load_books_from_csv(path)
                messagebox.showinfo("Success", f"Loaded books from {path}")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to load books: {e}")

    def load_users_csv(self):
        path = filedialog.askopenfilename(
            title="Select Users CSV",
            filetypes=[("CSV files", "*.csv"), ("All files", "*.*")],
        )
        if path:
            self.users_csv_path = path
            try:
                # You need to implement this method in the Library class if not present
                self.library.load_users_from_csv(path)
                messagebox.showinfo("Success", f"Loaded users from {path}")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to load users: {e}")

    def start_system(self):
        # Reset the logs file
        with open("log.txt", "w") as log_file:
            log_file.write("")
        self.library.after_login()
        # If data has been loaded or not, we proceed
        messagebox.showinfo("Info", "Starting Library System.")

        # Move to the login screen
        from login_gui import LoginGUI

        login_window = tk.Toplevel(self.master)
        LoginGUI(login_window)
        # Optionally, you can close this window:
        # self.master.destroy()
