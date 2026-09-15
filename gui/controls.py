"""Control panel for variable, time, and level selection."""

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QComboBox,
    QSpinBox, QDoubleSpinBox, QGroupBox
)
from PyQt6.QtCore import pyqtSignal


class ControlPanel(QWidget):
    """Panel for controlling plot parameters."""

    variable_changed = pyqtSignal(str)
    time_changed = pyqtSignal()
    level_changed = pyqtSignal()

    def __init__(self):
        super().__init__()
        layout = QVBoxLayout()

        # Variable selection
        var_group = QGroupBox("Variable")
        var_layout = QVBoxLayout()
        self.variable_combo = QComboBox()
        self.variable_combo.currentTextChanged.connect(self.on_variable_changed)
        var_layout.addWidget(self.variable_combo)
        var_group.setLayout(var_layout)
        layout.addWidget(var_group)

        # Time selection
        time_group = QGroupBox("Time Step")
        time_layout = QVBoxLayout()
        self.time_spin = QSpinBox()
        self.time_spin.valueChanged.connect(self.time_changed.emit)
        time_layout.addWidget(QLabel("Time Index:"))
        time_layout.addWidget(self.time_spin)
        time_group.setLayout(time_layout)
        layout.addWidget(time_group)

        # Level selection
        level_group = QGroupBox("Level")
        level_layout = QVBoxLayout()
        self.level_spin = QSpinBox()
        self.level_spin.valueChanged.connect(self.level_changed.emit)
        level_layout.addWidget(QLabel("Level Index:"))
        level_layout.addWidget(self.level_spin)
        level_group.setLayout(level_layout)
        layout.addWidget(level_group)

        # Colormap selection
        cmap_group = QGroupBox("Colormap")
        cmap_layout = QVBoxLayout()
        self.cmap_combo = QComboBox()
        self.cmap_combo.addItems(["viridis", "plasma", "inferno", "magma", "cividis",
                                   "RdYlBu", "RdYlGn", "jet", "cool", "hot"])
        cmap_layout.addWidget(self.cmap_combo)
        cmap_group.setLayout(cmap_layout)
        layout.addWidget(cmap_group)

        # Min/Max values
        range_group = QGroupBox("Value Range")
        range_layout = QVBoxLayout()
        self.vmin_spin = QDoubleSpinBox()
        self.vmin_spin.setMinimum(-1e10)
        self.vmin_spin.setMaximum(1e10)
        self.vmax_spin = QDoubleSpinBox()
        self.vmax_spin.setMinimum(-1e10)
        self.vmax_spin.setMaximum(1e10)
        range_layout.addWidget(QLabel("Min:"))
        range_layout.addWidget(self.vmin_spin)
        range_layout.addWidget(QLabel("Max:"))
        range_layout.addWidget(self.vmax_spin)
        range_group.setLayout(range_layout)
        layout.addWidget(range_group)

        layout.addStretch()
        self.setLayout(layout)

    def on_variable_changed(self):
        """Emit variable changed signal."""
        self.variable_changed.emit(self.variable_combo.currentText())

    def populate_variables(self, data):
        """Populate variable combo box."""
        self.variable_combo.blockSignals(True)
        self.variable_combo.clear()
        self.variable_combo.addItems(list(data.data_vars))
        self.variable_combo.blockSignals(False)

    def populate_time_steps(self, data, var_name):
        """Populate time step spinbox."""
        if var_name in data.data_vars:
            var = data[var_name]
            if "time" in var.dims:
                n_times = var.sizes["time"]
                self.time_spin.setMaximum(n_times - 1)

    def populate_levels(self, data, var_name):
        """Populate level spinbox."""
        if var_name in data.data_vars:
            var = data[var_name]
            n_levels = 1
            if "level" in var.dims:
                n_levels = var.sizes["level"]
            elif "height" in var.dims:
                n_levels = var.sizes["height"]
            self.level_spin.setMaximum(max(0, n_levels - 1))

    def get_selected_variable(self):
        """Get selected variable name."""
        return self.variable_combo.currentText()

    def get_selected_time_index(self):
        """Get selected time index."""
        return self.time_spin.value()

    def get_selected_level_index(self):
        """Get selected level index."""
        return self.level_spin.value()

    def get_colormap(self):
        """Get selected colormap."""
        return self.cmap_combo.currentText()

    def get_vmin(self):
        """Get minimum value."""
        return self.vmin_spin.value() if self.vmin_spin.value() != 0 else None

    def get_vmax(self):
        """Get maximum value."""
        return self.vmax_spin.value() if self.vmax_spin.value() != 0 else None
