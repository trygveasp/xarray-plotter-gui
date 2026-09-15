"""Control panel for variable selection."""

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QComboBox, QGroupBox
)
from PyQt6.QtCore import pyqtSignal


class ControlPanel(QWidget):
    """Panel for controlling variable selection."""

    variable_changed = pyqtSignal(str)
    vertical_dim_changed = pyqtSignal(str)

    def __init__(self):
        super().__init__()
        self.current_data = None
        
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

    def get_selected_variable(self):
        """Get selected variable name."""
        return self.variable_combo.currentText()

    def get_selected_vertical_dim(self):
        """Get selected vertical dimension."""
        vert_dim = self.vert_dim_combo.currentText()
        return vert_dim if vert_dim != "None" else None

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
