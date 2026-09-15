"""Plot window for displaying variable data."""

from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QComboBox, QSpinBox, QDoubleSpinBox, QGroupBox,
    QPushButton, QScrollArea
)
from PyQt6.QtCore import Qt, QTimer, pyqtSignal
from gui.plot_widget import PlotWidget


class PlotWindow(QMainWindow):
    """Window for plotting a specific variable with controls."""

    def __init__(self, data, var_name, parent=None):
        super().__init__(parent)
        self.data = data
        self.var_name = var_name
        self.animation_timer = QTimer()
        self.animation_timer.timeout.connect(self.advance_time_step)
        self.animation_speed = 500  # milliseconds

        self.setWindowTitle(f"Plot: {var_name}")
        self.setGeometry(200, 200, 1400, 800)

        # Create central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QHBoxLayout(central_widget)

        # Left side: Control panel
        left_layout = QVBoxLayout()
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_widget = QWidget()
        scroll_layout = QVBoxLayout(scroll_widget)

        # Variable info
        info_group = QGroupBox("Variable Info")
        info_layout = QVBoxLayout()
        var = self.data[var_name]
        dims_text = f"Dimensions: {', '.join(var.dims)}"
        shape_text = f"Shape: {var.shape}"
        info_layout.addWidget(QLabel(dims_text))
        info_layout.addWidget(QLabel(shape_text))
        if hasattr(var, 'attrs') and 'long_name' in var.attrs:
            info_layout.addWidget(QLabel(f"Long name: {var.attrs['long_name']}"))
        if hasattr(var, 'attrs') and 'units' in var.attrs:
            info_layout.addWidget(QLabel(f"Units: {var.attrs['units']}"))
        info_group.setLayout(info_layout)
        scroll_layout.addWidget(info_group)

        # Time selection with animation
        time_group = QGroupBox("Time Step")
        time_layout = QVBoxLayout()

        time_control_layout = QHBoxLayout()
        self.time_spin = QSpinBox()
        self.time_spin.valueChanged.connect(self.on_time_changed)
        time_control_layout.addWidget(QLabel("Index:"))
        time_control_layout.addWidget(self.time_spin)
        time_layout.addLayout(time_control_layout)

        # Time value label
        self.time_value_label = QLabel("")
        time_layout.addWidget(self.time_value_label)

        # Animation controls
        anim_layout = QHBoxLayout()
        self.play_button = QPushButton("▶ Play")
        self.play_button.clicked.connect(self.toggle_animation)
        self.stop_button = QPushButton("⏹ Stop")
        self.stop_button.clicked.connect(self.stop_animation)
        self.stop_button.setEnabled(False)
        anim_layout.addWidget(self.play_button)
        anim_layout.addWidget(self.stop_button)
        time_layout.addLayout(anim_layout)

        # Animation speed slider
        speed_layout = QHBoxLayout()
        self.speed_spin = QSpinBox()
        self.speed_spin.setMinimum(100)
        self.speed_spin.setMaximum(2000)
        self.speed_spin.setValue(self.animation_speed)
        self.speed_spin.setSingleStep(100)
        self.speed_spin.valueChanged.connect(self.update_animation_speed)
        speed_layout.addWidget(QLabel("Speed (ms):"))
        speed_layout.addWidget(self.speed_spin)
        time_layout.addLayout(speed_layout)

        time_group.setLayout(time_layout)
        scroll_layout.addWidget(time_group)

        # Level selection
        level_group = QGroupBox("Vertical Level")
        level_layout = QVBoxLayout()
        self.level_spin = QSpinBox()
        self.level_spin.valueChanged.connect(self.on_level_changed)
        level_layout.addWidget(QLabel("Level Index:"))
        level_layout.addWidget(self.level_spin)
        self.level_value_label = QLabel("")
        level_layout.addWidget(self.level_value_label)
        level_group.setLayout(level_layout)
        scroll_layout.addWidget(level_group)

        # Colormap selection
        cmap_group = QGroupBox("Colormap")
        cmap_layout = QVBoxLayout()
        self.cmap_combo = QComboBox()
        self.cmap_combo.addItems(["viridis", "plasma", "inferno", "magma", "cividis",
                                   "RdYlBu", "RdYlGn", "jet", "cool", "hot", "bwr", "RdBu"])
        self.cmap_combo.currentTextChanged.connect(self.on_plot_update)
        cmap_layout.addWidget(self.cmap_combo)
        cmap_group.setLayout(cmap_layout)
        scroll_layout.addWidget(cmap_group)

        # Min/Max values
        range_group = QGroupBox("Value Range")
        range_layout = QVBoxLayout()
        self.vmin_spin = QDoubleSpinBox()
        self.vmin_spin.setMinimum(-1e10)
        self.vmin_spin.setMaximum(1e10)
        self.vmin_spin.valueChanged.connect(self.on_plot_update)
        self.vmax_spin = QDoubleSpinBox()
        self.vmax_spin.setMinimum(-1e10)
        self.vmax_spin.setMaximum(1e10)
        self.vmax_spin.valueChanged.connect(self.on_plot_update)
        range_layout.addWidget(QLabel("Min:"))
        range_layout.addWidget(self.vmin_spin)
        range_layout.addWidget(QLabel("Max:"))
        range_layout.addWidget(self.vmax_spin)
        range_group.setLayout(range_layout)
        scroll_layout.addWidget(range_group)

        scroll_layout.addStretch()
        scroll_area.setWidget(scroll_widget)
        left_layout.addWidget(scroll_area)

        # Right side: plot
        self.plot_widget = PlotWidget()

        main_layout.addLayout(left_layout, 1)
        main_layout.addWidget(self.plot_widget, 2)

        # Initialize
        self._initialize_controls()
        self.plot_data()

    def _initialize_controls(self):
        """Initialize control values based on data."""
        var = self.data[self.var_name]

        # Time steps
        if "time" in var.dims:
            n_times = var.sizes["time"]
            self.time_spin.setMaximum(n_times - 1)
            self.update_time_label()
        else:
            self.time_spin.setEnabled(False)

        # Levels
        n_levels = 1
        self.level_dim = None
        for dim in ["level", "height", "pressure", "sigma"]:
            if dim in var.dims:
                n_levels = var.sizes[dim]
                self.level_dim = dim
                break

        self.level_spin.setMaximum(max(0, n_levels - 1))
        self.update_level_label()

        # Auto-scale value range
        try:
            data_slice = self._get_data_slice()
            if data_slice is not None:
                vmin = float(data_slice.min())
                vmax = float(data_slice.max())
                self.vmin_spin.setValue(vmin)
                self.vmax_spin.setValue(vmax)
        except Exception:
            pass

    def _get_data_slice(self):
        """Get current 2D data slice."""
        var = self.data[self.var_name]
        data_array = var

        # Extract 2D slice
        if "time" in data_array.dims:
            time_idx = self.time_spin.value()
            data_array = data_array.isel(time=time_idx)

        if self.level_dim and self.level_dim in data_array.dims:
            level_idx = self.level_spin.value()
            data_array = data_array.isel({self.level_dim: level_idx})

        return data_array

    def plot_data(self):
        """Plot the current data slice."""
        try:
            data_array = self._get_data_slice()
            if data_array is None:
                return

            cmap = self.cmap_combo.currentText()
            vmin = self.vmin_spin.value() if self.vmin_spin.value() != 0 else None
            vmax = self.vmax_spin.value() if self.vmax_spin.value() != 0 else None

            title = f"{self.var_name}"
            if "time" in self.data[self.var_name].dims:
                title += f" (time index: {self.time_spin.value()})"
            if self.level_dim:
                title += f" ({self.level_dim} index: {self.level_spin.value()})"

            self.plot_widget.plot_data(
                data_array,
                title=title,
                cmap=cmap,
                vmin=vmin,
                vmax=vmax
            )
        except Exception as e:
            print(f"Error plotting: {str(e)}")

    def on_time_changed(self):
        """Handle time step change."""
        self.update_time_label()
        self.plot_data()

    def on_level_changed(self):
        """Handle level change."""
        self.update_level_label()
        self.plot_data()

    def on_plot_update(self):
        """Handle plot parameter changes."""
        self.plot_data()

    def update_time_label(self):
        """Update time value label."""
        var = self.data[self.var_name]
        if "time" in var.dims and "time" in self.data.coords:
            try:
                time_values = self.data.coords["time"].values
                time_idx = self.time_spin.value()
                time_val = time_values[time_idx]
                self.time_value_label.setText(f"Time: {time_val}")
            except (IndexError, TypeError):
                pass

    def update_level_label(self):
        """Update level value label."""
        if self.level_dim and self.level_dim in self.data.coords:
            try:
                level_values = self.data.coords[self.level_dim].values
                level_idx = self.level_spin.value()
                level_val = level_values[level_idx]
                self.level_value_label.setText(f"{self.level_dim}: {level_val:.1f}")
            except (IndexError, TypeError):
                pass

    def toggle_animation(self):
        """Toggle time step animation."""
        if self.animation_timer.isActive():
            self.stop_animation()
        else:
            self.play_button.setEnabled(False)
            self.stop_button.setEnabled(True)
            self.animation_timer.start(self.animation_speed)

    def stop_animation(self):
        """Stop time step animation."""
        self.animation_timer.stop()
        self.play_button.setEnabled(True)
        self.stop_button.setEnabled(False)

    def advance_time_step(self):
        """Advance to next time step, loop at end."""
        max_time = self.time_spin.maximum()
        current_time = self.time_spin.value()

        if current_time >= max_time:
            self.time_spin.setValue(0)
        else:
            self.time_spin.setValue(current_time + 1)

    def update_animation_speed(self, speed):
        """Update animation speed."""
        self.animation_speed = speed
        if self.animation_timer.isActive():
            self.animation_timer.setInterval(speed)
