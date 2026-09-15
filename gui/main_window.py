"""Main application window."""

import sys
from pathlib import Path
from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QFileDialog, QLabel, QListWidget, QListWidgetItem, QGroupBox
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

        # Main content: Controls and Variable Lists
        content_layout = QHBoxLayout()

        # Left side: Vertical dimension controls
        left_layout = QVBoxLayout()
        self.control_panel = ControlPanel()
        self.control_panel.variable_changed.connect(self.on_variable_changed)
        self.control_panel.vertical_dim_changed.connect(self.on_vertical_dim_changed)
        left_layout.addWidget(self.control_panel)
        left_layout.addStretch()
        content_layout.addLayout(left_layout, 1)

        # Right side: Variable lists grouped by number of dimensions
        right_layout = QVBoxLayout()
        right_layout.addWidget(QLabel("Variables (sorted by dimensions):"))
        
        # Container for dimension groups
        self.dimension_groups = {}
        self.variable_lists = {}
        
        content_layout.addLayout(right_layout, 2)
        layout.addLayout(content_layout)

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
                self.populate_variable_lists()
                self.statusBar().showMessage(f"Loaded: {Path(file_path).name}")
            except Exception as e:
                self.statusBar().showMessage(f"Error loading file: {str(e)}")

    def populate_variable_lists(self):
        """Populate variable lists grouped by number of dimensions."""
        if not self.current_data:
            return

        vert_dim = self.control_panel.get_selected_vertical_dim()
        
        # Get variables and filter by vertical dimension
        variables = list(self.current_data.data_vars)
        
        if vert_dim and vert_dim != "None":
            variables = [var for var in variables 
                        if vert_dim in self.current_data[var].dims or
                           vert_dim.lower() in [d.lower() for d in self.current_data[var].dims]]
        
        # Group variables by non-spatial, non-time dimensions
        dimension_groups = {}
        
        for var_name in variables:
            var = self.current_data[var_name]
            
            # Get dimensions excluding time, x, y, lat, lon
            spatial_time_dims = {'time', 'x', 'y', 'lat', 'lon', 'latitude', 'longitude'}
            other_dims = tuple(sorted([d for d in var.dims if d.lower() not in spatial_time_dims]))
            
            # Create key for grouping
            if not other_dims:
                group_key = "2D (time/space only)"
            else:
                group_key = f"{len(other_dims)}D other: {', '.join(other_dims)}"
            
            if group_key not in dimension_groups:
                dimension_groups[group_key] = []
            dimension_groups[group_key].append(var_name)
        
        # Clear existing groups
        content_widget = self.centralWidget().layout().itemAt(1).itemAt(1).widget()
        if content_widget and hasattr(content_widget, 'layout'):
            layout = content_widget.layout()
            while layout.count() > 1:  # Keep the label
                layout.takeAt(1).widget().deleteLater()
        
        self.dimension_groups = {}
        self.variable_lists = {}
        
        # Get the right layout
        right_layout = self.centralWidget().layout().itemAt(1).itemAt(1)
        
        # Add groups sorted by number of dimensions
        sorted_groups = sorted(dimension_groups.keys(), 
                              key=lambda x: (0 if x == "2D (time/space only)" else int(x.split('D')[0])))
        
        for group_key in sorted_groups:
            group_box = QGroupBox(group_key)
            group_layout = QVBoxLayout()
            
            var_list = QListWidget()
            var_list.itemClicked.connect(lambda item: self.on_variable_list_clicked(item))
            
            # Add variables to this group
            for var_name in sorted(dimension_groups[group_key]):
                var = self.current_data[var_name]
                dims_str = ", ".join(var.dims)
                item_text = f"{var_name} ({dims_str})"
                item = QListWidgetItem(item_text)
                item.setData(Qt.ItemDataRole.UserRole, var_name)
                var_list.addItem(item)
            
            group_layout.addWidget(var_list)
            group_box.setLayout(group_layout)
            right_layout.addWidget(group_box)
            
            self.dimension_groups[group_key] = group_box
            self.variable_lists[group_key] = var_list

    def on_variable_list_clicked(self, item):
        """Handle variable list click to open plot window."""
        var_name = item.data(Qt.ItemDataRole.UserRole)
        if var_name:
            self.open_plot_window(var_name)

    def on_variable_changed(self, var_name):
        """Handle variable change from control panel."""
        if self.current_data and var_name:
            self.statusBar().showMessage(f"Selected: {var_name}")

    def on_vertical_dim_changed(self, vert_dim):
        """Handle vertical dimension change."""
        self.populate_variable_lists()

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
