"""Matplotlib plotting widget for PyQt6."""

from PyQt6.QtWidgets import QWidget, QVBoxLayout
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg
from matplotlib.figure import Figure
import matplotlib.pyplot as plt


class PlotWidget(QWidget):
    """Widget for displaying matplotlib plots."""

    def __init__(self):
        super().__init__()
        self.figure = Figure(figsize=(8, 6), dpi=100)
        self.canvas = FigureCanvasQTAgg(self.figure)
        layout = QVBoxLayout()
        layout.addWidget(self.canvas)
        self.setLayout(layout)

    def plot_data(self, data_array, title="", cmap="viridis", vmin=None, vmax=None):
        """Plot a 2D data array.

        Parameters
        ----------
        data_array : xarray.DataArray
            2D data array to plot
        title : str
            Title for the plot
        cmap : str
            Colormap name
        vmin : float, optional
            Minimum value for colormap
        vmax : float, optional
            Maximum value for colormap
        """
        self.figure.clear()
        ax = self.figure.add_subplot(111)

        # Plot the data
        im = ax.imshow(
            data_array.values,
            origin="lower",
            cmap=cmap,
            vmin=vmin,
            vmax=vmax,
            aspect="auto"
        )

        ax.set_title(title)
        ax.set_xlabel("X")
        ax.set_ylabel("Y")
        self.figure.colorbar(im, ax=ax, label="Value")
        self.figure.tight_layout()
        self.canvas.draw()
