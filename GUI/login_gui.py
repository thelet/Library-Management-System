import tkinter as tk
from tkinter import messagebox
from Classes.library import Library
from Classes.user import User, Librarian


class LoginGUI:
    def __init__(self, master):
        self.master = master
        self.master.title("Login Screen")
        self.library = Library.getInstance()

        # Username and Password fields
        tk.Label(self.master, text="Username:").grid(row=0, column=0, padx=5, pady=5)
        self.username_entry = tk.Entry(self.master)
        self.username_entry.grid(row=0, column=1, padx=5, pady=5)

        tk.Label(self.master, text="Password:").grid(row=1, column=0, padx=5, pady=5)
        self.password_entry = tk.Entry(self.master, show="*")
        self.password_entry.grid(row=1, column=1, padx=5, pady=5)

        # Buttons
        tk.Button(self.master, text="Log in as Librarian", command=self.login_librarian).grid(row=2, column=0, padx=5,
                                                                                              pady=5)
        tk.Button(self.master, text="Log in as User", command=self.login_user).grid(row=2, column=1, padx=5, pady=5)
        tk.Button(self.master, text="Sign up as Librarian", command=self.signup_librarian).grid(row=3, column=0, padx=5,
                                                                                                pady=5)
        tk.Button(self.master, text="Sign up as User", command=self.signup_user).grid(row=3, column=1, padx=5, pady=5)

        tk.Button(self.master, text="Continue as Guest", command=self.guest_mode).grid(row=4, column=0, columnspan=2,
                                                                                       pady=5)

    def login_librarian(self):
        username = self.username_entry.get().strip()
        password = self.password_entry.get().strip()

        # Find a librarian with these credentials
        librarian = next((l for l in self.library.librarian_users
                          if l.username == username and l._User__passwordHash == password), None)
        if librarian:
            self.open_main_screen(librarian)
        else:
            messagebox.showerror("Error", "Invalid librarian credentials.")

    def login_user(self):
        username = self.username_entry.get().strip()
        password = self.password_entry.get().strip()

        # Find a user with these credentials
        user = next((u for u in self.library.users
                     if u.username == username and u._User__passwordHash == password), None)
        if user:
            self.open_main_screen(user)
        else:
            messagebox.showerror("Error", "Invalid user credentials.")

    def signup_librarian(self):
        username = self.username_entry.get().strip()
        password = self.password_entry.get().strip()
        if not username or not password:
            messagebox.showerror("Error", "Username and password cannot be empty.")
            return
        # Check if already exists
        if any(l.username == username for l in self.library.librarian_users):
            messagebox.showerror("Error", "Librarian username already exists.")
            return
        librarian = Librarian(username, password)
        self.library.librarian_users.append(librarian)
        messagebox.showinfo("Success", f"Librarian '{username}' created.")
        self.open_main_screen(librarian)

    def signup_user(self):
        username = self.username_entry.get().strip()
        password = self.password_entry.get().strip()
        if not username or not password:
            messagebox.showerror("Error", "Username and password cannot be empty.")
            return
        if any(u.username == username for u in self.library.users):
            messagebox.showerror("Error", "User username already exists.")
            return
        user = User(username, password)  # Default permissions: ["borrow", "return"]
        self.library.users.append(user)
        messagebox.showinfo("Success", f"User '{username}' created.")
        self.open_main_screen(user)

    def guest_mode(self):
        # Guest has no user instance
        self.open_main_screen(None)

    def open_main_screen(self, user):
        from gui import LibraryGUI
        new_window = tk.Toplevel(self.master)
        LibraryGUI(new_window, user)  # Pass in the user or None for guests
        # optional: keep or destroy the login window
        # self.master.destroy()
