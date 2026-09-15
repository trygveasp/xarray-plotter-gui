"""Main application window."""

import sys
from pathlib import Path
from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QFileDialog, QLabel, QStatusBar
)
from PyQt6.QtCore import Qt
from gui.plot_widget import PlotWidget
from gui.controls import ControlPanel
from data.loader import DataLoader


class MainWindow(QMainWindow):
    """Main application window."""

    def __init__(self):
        super().__init__()
        self.setWindowTitle("Xarray Plotter GUI")
        self.setGeometry(100, 100, 1200, 800)

        self.data_loader = DataLoader()
        self.current_data = None
        self.current_file = None

        # Create central widget and layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QHBoxLayout(central_widget)

        # Left side: controls
        left_layout = QVBoxLayout()
        self.open_button = QPushButton("Open File")
        self.open_button.clicked.connect(self.open_file)
        left_layout.addWidget(self.open_button)

        self.file_label = QLabel("No file opened")
        left_layout.addWidget(QLabel("Current File:"))
        left_layout.addWidget(self.file_label)

        self.control_panel = ControlPanel()
        self.control_panel.variable_changed.connect(self.on_variable_changed)
        self.control_panel.time_changed.connect(self.on_time_changed)
        self.control_panel.level_changed.connect(self.on_level_changed)
        left_layout.addWidget(self.control_panel)
        left_layout.addStretch()

        # Right side: plot
        self.plot_widget = PlotWidget()
        layout.addLayout(left_layout, 1)
        layout.addWidget(self.plot_widget, 2)

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
                self.statusBar().showMessage(f"Loaded: {Path(file_path).name}")
            except Exception as e:
                self.statusBar().showMessage(f"Error loading file: {str(e)}")

    def on_variable_changed(self, var_name):
        """Handle variable change."""
        if self.current_data and var_name:
            try:
                self.control_panel.populate_time_steps(self.current_data, var_name)
                self.control_panel.populate_levels(self.current_data, var_name)
                self.plot_data(var_name)
            except Exception as e:
                self.statusBar().showMessage(f"Error: {str(e)}")

    def on_time_changed(self):
        """Handle time step change."""
        var_name = self.control_panel.get_selected_variable()
        if var_name:
            self.plot_data(var_name)

    def on_level_changed(self):
        """Handle level change."""
        var_name = self.control_panel.get_selected_variable()
        if var_name:
            self.plot_data(var_name)

    def plot_data(self, var_name):
        """Plot the selected variable."""
        if not self.current_data:
            return

        try:
            time_idx = self.control_panel.get_selected_time_index()
            level_idx = self.control_panel.get_selected_level_index()
            cmap = self.control_panel.get_colormap()
            vmin = self.control_panel.get_vmin()
            vmax = self.control_panel.get_vmax()

            data_array = self.current_data[var_name]

            # Extract 2D slice
            if time_idx is not None and "time" in data_array.dims:
                data_array = data_array.isel(time=time_idx)
            if level_idx is not None and "level" in data_array.dims:
                data_array = data_array.isel(level=level_idx)
            elif level_idx is not None and "height" in data_array.dims:
                data_array = data_array.isel(height=level_idx)

            self.plot_widget.plot_data(
                data_array,
                title=f"{var_name}",
                cmap=cmap,
                vmin=vmin,
                vmax=vmax
            )
            self.statusBar().showMessage(f"Plotted: {var_name}")
        except Exception as e:
            self.statusBar().showMessage(f"Error plotting: {str(e)}")


def main():
    """Run the application."""
    app = sys.modules.get('PyQt6.QtWidgets', __import__('PyQt6.QtWidgets'))
    from PyQt6.QtWidgets import QApplication
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
