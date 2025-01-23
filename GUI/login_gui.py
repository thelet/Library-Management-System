import tkinter as tk
from tkinter import messagebox
from Classes.library import Library
from design_patterns.exceptions import SignUpError


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
        tk.Button(
            self.master,
            text="Log in as Librarian or a user",
            command=lambda: self.login("librarian"),
        ).grid(row=2, column=0, columnspan=2, padx=5, pady=5)
        # tk.Button(self.master, text="Log in as User", command=lambda:self.login("regular user")).grid(row=2, column=1, padx=5, pady=5)
        tk.Button(
            self.master,
            text="Sign up as Librarian",
            command=lambda: self.signup("librarian"),
        ).grid(row=3, column=0, padx=5, pady=5)
        tk.Button(
            self.master,
            text="Sign up as User",
            command=lambda: self.signup("regular user"),
        ).grid(row=3, column=1, padx=5, pady=5)

        tk.Button(self.master, text="Continue as Guest", command=self.guest_mode).grid(
            row=4, column=0, columnspan=2, pady=5
        )

    def signup(self, role):
        username = self.username_entry.get().strip()
        password = self.password_entry.get().strip()
        if not username or not password:
            messagebox.showerror("Error", "Username and password cannot be empty.")
            self.library.log_notify_print(to_log="Registration failed - username or password empty",
                                          to_print="Registration failed - username or password empty", to_notify=None)
            return
        try:
            user = self.library.signUp(
                {"username": username, "password": password, "role": role}
            )
        except SignUpError as e:
            messagebox.showerror("Error", str(e))
        else:
            messagebox.showinfo("Success", f"{role} '{username}' created.")
            self.open_main_screen(user)

        # gui_login.py

    def login(self, role: str):
        username = self.username_entry.get().strip()
        password = self.password_entry.get().strip()

        # Find a user with the given username
        user = next(
            (u for u in self.library.users.values() if u.username == username), None
        )

        if user and user.verify_password(password):
            self.open_main_screen(user)
        else:
            messagebox.showerror("Error", f"Invalid {role} credentials.")
            self.library.log_notify_print(to_log=f"Login failed - invalid {role} credentials",
                                          to_print=f"Login failed - invalid {role} credentials", to_notify=None)

    def guest_mode(self):
        # Guest has no user instance
        self.open_main_screen(None)

    def open_main_screen(self, user):
        from gui import LibraryGUI

        new_window = tk.Toplevel(self.master)
        LibraryGUI(new_window, user)  # Pass in the user or None for guests
        # optional: keep or destroy the login window
        # self.master.destroy()
