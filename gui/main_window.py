"""Main application window."""

import sys
from pathlib import Path
from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QFileDialog, QLabel, QListWidget, QListWidgetItem, QSplitter
)
from PyQt6.QtCore import Qt
from gui.plot_window import PlotWindow
from gui.controls import ControlPanel
from data.loader import DataLoader


class MainWindow(QMainWindow):
    """Main application window."""

    def __init__(self):
        super().__init__()
        self.setWindowTitle("Xarray Plotter GUI")
        self.setGeometry(100, 100, 1000, 700)

        self.data_loader = DataLoader()
        self.current_data = None
        self.current_file = None
        self.plot_window = None

        # Create central widget and layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)

        # Top: File controls
        file_layout = QHBoxLayout()
        self.open_button = QPushButton("Open File")
        self.open_button.clicked.connect(self.open_file)
        file_layout.addWidget(self.open_button)

        self.file_label = QLabel("No file opened")
        file_layout.addWidget(QLabel("File:"))
        file_layout.addWidget(self.file_label)
        file_layout.addStretch()
        layout.addLayout(file_layout)

        # Main content: Controls and Variable List
        content_layout = QHBoxLayout()

        # Left side: controls
        self.control_panel = ControlPanel()
        self.control_panel.variable_changed.connect(self.on_variable_changed)
        self.control_panel.vertical_dim_changed.connect(self.on_vertical_dim_changed)
        content_layout.addWidget(self.control_panel, 1)

        # Right side: Variable list sorted by dimensions
        var_group_layout = QVBoxLayout()
        var_group_layout.addWidget(QLabel("Variables (sorted by dimensions):"))
        self.variable_list = QListWidget()
        self.variable_list.itemClicked.connect(self.on_variable_list_clicked)
        var_group_layout.addWidget(self.variable_list)
        content_layout.addLayout(var_group_layout, 1)

        layout.addLayout(content_layout)

        # Bottom: Info
        info_layout = QHBoxLayout()
        self.info_label = QLabel("Ready")
        info_layout.addWidget(self.info_label)
        layout.addLayout(info_layout)

        # Status bar
        self.statusBar().showMessage("Ready")

    def open_file(self):
        """Open a file dialog and load a GRIB or NetCDF file."""
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Open GRIB, NetCDF File",
            "",
            "grbfp Files (*.grbfp);;GRIB Files (*.grib *.grib2 *.grb *.grb2);;NetCDF Files (*.nc *.netcdf);;All Files (*)"
        )

        if file_path:
            try:
                self.current_file = file_path
                self.current_data = self.data_loader.load_file(file_path)
                self.file_label.setText(Path(file_path).name)
                self.control_panel.populate_variables(self.current_data)
                self.populate_variable_list()
                self.statusBar().showMessage(f"Loaded: {Path(file_path).name}")
            except Exception as e:
                self.statusBar().showMessage(f"Error loading file: {str(e)}")

    def populate_variable_list(self):
        """Populate variable list sorted by number of dimensions."""
        if not self.current_data:
            return

        vert_dim = self.control_panel.get_selected_vertical_dim()
        
        # Get variables
        variables = list(self.current_data.data_vars)
        
        # Filter by vertical dimension if selected
        if vert_dim and vert_dim != "None":
            variables = [var for var in variables 
                        if vert_dim in self.current_data[var].dims or
                           vert_dim.lower() in [d.lower() for d in self.current_data[var].dims]]
        
        # Sort by number of dimensions (descending)
        variables.sort(
            key=lambda v: len(self.current_data[v].dims),
            reverse=True
        )

        # Populate list with dimension info
        self.variable_list.clear()
        for var_name in variables:
            var = self.current_data[var_name]
            n_dims = len(var.dims)
            dims_str = ", ".join(var.dims)
            item_text = f"{var_name} ({n_dims}D: {dims_str})"
            item = QListWidgetItem(item_text)
            item.setData(Qt.ItemDataRole.UserRole, var_name)
            self.variable_list.addItem(item)

    def on_variable_list_clicked(self, item):
        """Handle variable list click to open plot window."""
        var_name = item.data(Qt.ItemDataRole.UserRole)
        if var_name:
            self.open_plot_window(var_name)

    def on_variable_changed(self, var_name):
        """Handle variable change from control panel."""
        if self.current_data and var_name:
            try:
                self.control_panel.populate_time_steps(self.current_data, var_name)
                self.control_panel.populate_levels(self.current_data, var_name)
                self.statusBar().showMessage(f"Selected: {var_name}")
            except Exception as e:
                self.statusBar().showMessage(f"Error: {str(e)}")

    def on_vertical_dim_changed(self, vert_dim):
        """Handle vertical dimension change."""
        self.populate_variable_list()

    def open_plot_window(self, var_name):
        """Open a new plot window for the selected variable."""
        if not self.current_data:
            return

        if var_name not in self.current_data.data_vars:
            self.statusBar().showMessage(f"Variable not found: {var_name}")
            return

        try:
            # Create and show plot window
            self.plot_window = PlotWindow(
                self.current_data,
                var_name,
                parent=self
            )
            self.plot_window.show()
            self.statusBar().showMessage(f"Opened plot window for: {var_name}")
        except Exception as e:
            self.statusBar().showMessage(f"Error opening plot window: {str(e)}")


def main():
    """Run the application."""
    from PyQt6.QtWidgets import QApplication
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
