#!/usr/bin/env python
"""Entry point for xarray plotter GUI application."""

import sys
from gui.main_window import MainWindow
from PyQt6.QtWidgets import QApplication


def main():
    """Run the application."""
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
