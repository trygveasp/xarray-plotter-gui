"""Control panel for variable, time, and level selection."""

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QComboBox,
    QSpinBox, QDoubleSpinBox, QGroupBox, QPushButton
)
from PyQt6.QtCore import pyqtSignal, QTimer


class ControlPanel(QWidget):
    """Panel for controlling plot parameters."""

    variable_changed = pyqtSignal(str)
    time_changed = pyqtSignal()
    level_changed = pyqtSignal()
    vertical_dim_changed = pyqtSignal(str)

    def __init__(self):
        super().__init__()
        self.current_data = None
        self.animation_timer = QTimer()
        self.animation_timer.timeout.connect(self.advance_time_step)
        self.animation_speed = 500  # milliseconds
        
        layout = QVBoxLayout()

        # Vertical dimension selection
        vert_group = QGroupBox("Vertical Dimension")
        vert_layout = QVBoxLayout()
        self.vert_dim_combo = QComboBox()
        self.vert_dim_combo.currentTextChanged.connect(self.on_vertical_dim_changed)
        vert_layout.addWidget(QLabel("Select dimension:"))
        vert_layout.addWidget(self.vert_dim_combo)
        vert_group.setLayout(vert_layout)
        layout.addWidget(vert_group)

        # Variable selection
        var_group = QGroupBox("Variable")
        var_layout = QVBoxLayout()
        self.variable_combo = QComboBox()
        self.variable_combo.currentTextChanged.connect(self.on_variable_changed)
        var_layout.addWidget(self.variable_combo)
        var_group.setLayout(var_layout)
        layout.addWidget(var_group)

        # Time selection with animation
        time_group = QGroupBox("Time Step")
        time_layout = QVBoxLayout()
        
        time_control_layout = QHBoxLayout()
        self.time_spin = QSpinBox()
        self.time_spin.valueChanged.connect(self.time_changed.emit)
        time_control_layout.addWidget(QLabel("Index:"))
        time_control_layout.addWidget(self.time_spin)
        time_layout.addLayout(time_control_layout)

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
        layout.addWidget(time_group)

        # Level selection
        level_group = QGroupBox("Level")
        level_layout = QVBoxLayout()
        self.level_spin = QSpinBox()
        self.level_spin.valueChanged.connect(self.level_changed.emit)
        level_layout.addWidget(QLabel("Level Index:"))
        level_layout.addWidget(self.level_spin)
        self.level_value_label = QLabel("")
        level_layout.addWidget(self.level_value_label)
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

    def on_vertical_dim_changed(self, vert_dim):
        """Handle vertical dimension change and update variables."""
        if self.current_data and vert_dim:
            self.update_variables_by_dimension(vert_dim)
            self.vertical_dim_changed.emit(vert_dim)

    def on_variable_changed(self):
        """Emit variable changed signal."""
        self.variable_changed.emit(self.variable_combo.currentText())

    def set_current_data(self, data):
        """Set the current dataset and update dimension list."""
        self.current_data = data
        self.populate_vertical_dimensions(data)

    def populate_vertical_dimensions(self, data):
        """Populate vertical dimension combo box with sorted dimensions."""
        vertical_dims = self._get_vertical_dimensions(data)
        
        self.vert_dim_combo.blockSignals(True)
        self.vert_dim_combo.clear()
        
        # Sort dimensions with preferred order
        preferred_order = ["level", "height", "pressure", "sigma"]
        sorted_dims = sorted(vertical_dims, 
                            key=lambda x: (preferred_order.index(x.lower()) 
                                          if x.lower() in preferred_order else len(preferred_order)))
        
        if sorted_dims:
            self.vert_dim_combo.addItems(sorted_dims)
        else:
            self.vert_dim_combo.addItem("None")
        
        self.vert_dim_combo.blockSignals(False)

    def update_variables_by_dimension(self, vert_dim):
        """Update variable list based on selected vertical dimension."""
        if not self.current_data:
            return

        filtered_vars = []
        
        if vert_dim == "None":
            # Include all variables
            filtered_vars = list(self.current_data.data_vars)
        else:
            # Include only variables with this vertical dimension
            for var_name in self.current_data.data_vars:
                var = self.current_data[var_name]
                if vert_dim in var.dims or (vert_dim.lower() in 
                                           [d.lower() for d in var.dims]):
                    filtered_vars.append(var_name)

        self.variable_combo.blockSignals(True)
        self.variable_combo.clear()
        self.variable_combo.addItems(sorted(filtered_vars))
        self.variable_combo.blockSignals(False)

    def populate_variables(self, data):
        """Populate variable combo box."""
        self.set_current_data(data)

    def populate_time_steps(self, data, var_name):
        """Populate time step spinbox."""
        if var_name in data.data_vars:
            var = data[var_name]
            if "time" in var.dims:
                n_times = var.sizes["time"]
                self.time_spin.setMaximum(n_times - 1)
            else:
                self.time_spin.setMaximum(0)

    def populate_levels(self, data, var_name):
        """Populate level spinbox and display level values."""
        if var_name in data.data_vars:
            var = data[var_name]
            n_levels = 1
            level_dim = None
            level_values = None
            
            # Find the level dimension
            for dim in ["level", "height", "pressure", "sigma"]:
                if dim in var.dims:
                    n_levels = var.sizes[dim]
                    level_dim = dim
                    if dim in data.coords:
                        level_values = data.coords[dim].values
                    break
            
            self.level_spin.setMaximum(max(0, n_levels - 1))
            
            # Display current level value
            if level_values is not None and level_dim:
                current_idx = self.level_spin.value()
                try:
                    level_val = level_values[current_idx]
                    self.level_value_label.setText(f"{level_dim}: {level_val:.1f}")
                except (IndexError, TypeError):
                    self.level_value_label.setText("")

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

    def get_selected_variable(self):
        """Get selected variable name."""
        return self.variable_combo.currentText()

    def get_selected_time_index(self):
        """Get selected time index."""
        return self.time_spin.value()

    def get_selected_level_index(self):
        """Get selected level index."""
        return self.level_spin.value()

    def get_selected_vertical_dim(self):
        """Get selected vertical dimension."""
        vert_dim = self.vert_dim_combo.currentText()
        return vert_dim if vert_dim != "None" else None

    def get_colormap(self):
        """Get selected colormap."""
        return self.cmap_combo.currentText()

    def get_vmin(self):
        """Get minimum value."""
        return self.vmin_spin.value() if self.vmin_spin.value() != 0 else None

    def get_vmax(self):
        """Get maximum value."""
        return self.vmax_spin.value() if self.vmax_spin.value() != 0 else None

    @staticmethod
    def _get_vertical_dimensions(data):
        """Get list of vertical dimensions in dataset."""
        vertical_dim_names = ["level", "height", "pressure", "sigma", "isobaric", "depth"]
        found_dims = set()
        
        for var in data.data_vars.values():
            for dim in var.dims:
                if dim.lower() in vertical_dim_names:
                    found_dims.add(dim)
        
        return sorted(list(found_dims))
