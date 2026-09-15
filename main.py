#!/usr/bin/env python
"""Entry point for xarray plotter GUI application."""

import sys
from gui.main_window import MainWindow
from PyQt6.QtWidgets import QApplication


def main(fname=None):
    """Run the application."""
    app = QApplication(sys.argv)
    window = MainWindow(fname=fname)
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    fname = None
    if len(sys.argv) > 1:
        fname = sys.argv[1]
    main(fname=fname)
