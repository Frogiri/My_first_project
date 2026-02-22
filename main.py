import sys
import os

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

import tkinter as tk
from controllers.app_controller import AppController
from views.main_window import MainWindow

def main():
    root = tk.Tk()
    controller = AppController()
    view = MainWindow(root, controller)
    root.mainloop()

if __name__ == "__main__":
    main()