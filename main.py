# main.py
import tkinter as tk
from gui import LibraryGUI

def main():
    root = tk.Tk()
    gui = LibraryGUI(root)
    root.mainloop()

if __name__ == "__main__":
    main()
