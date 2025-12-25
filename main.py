"""
Main entry point for ClipYTwo application
"""
import sys
import os

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

import customtkinter as ctk
from src.view.main_window import MainWindow
from src.controller.main_controller import MainController


def main():
    """Main function to start the application"""
    # Create and configure root window
    root = MainWindow()
    
    # Create controller
    controller = MainController(root)
    
    # Start GUI event loop
    root.mainloop()


if __name__ == "__main__":
    main()

