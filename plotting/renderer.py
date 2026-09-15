"""Rendering logic for plots."""

import matplotlib.pyplot as plt
import numpy as np


class Renderer:
    """Render 2D data as images."""

    @staticmethod
    def render_2d(data_array, title="", cmap="viridis", vmin=None, vmax=None):
        """Render a 2D data array.

        Parameters
        ----------
        data_array : xarray.DataArray or numpy.ndarray
            2D data to render
        title : str
            Title for the plot
        cmap : str
            Colormap name
        vmin : float, optional
            Minimum value for colormap
        vmax : float, optional
            Maximum value for colormap

        Returns
        -------
        matplotlib.figure.Figure
            The figure object
        """
        fig, ax = plt.subplots(figsize=(10, 8))

        # Handle xarray DataArray
        if hasattr(data_array, "values"):
            values = data_array.values
        else:
            values = data_array

        # Plot
        im = ax.imshow(
            values,
            origin="lower",
            cmap=cmap,
            vmin=vmin,
            vmax=vmax,
            aspect="auto"
        )

        ax.set_title(title, fontsize=14, fontweight="bold")
        ax.set_xlabel("X")
        ax.set_ylabel("Y")
        cbar = fig.colorbar(im, ax=ax)
        cbar.set_label("Value")

        plt.tight_layout()
        return fig
