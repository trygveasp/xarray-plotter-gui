# Xarray Plotter GUI

A lightweight Python plotting program with a graphical user interface for visualizing local GRIB and NetCDF files. Similar to ncview, it uses xarray with Fimex as the engine for efficient data handling and plotting.

## Features

- **Local File Support**: Open and visualize GRIB and NetCDF files from disk
- **Interactive GUI**: User-friendly interface built with PyQt6
- **Variable Selection**: Browse and select variables from multi-variable files
- **Time Navigation**: Step through time dimensions
- **Level Selection**: Handle multi-level data (height, pressure levels, etc.)
- **Customizable Plotting**: Adjust colormap, min/max values, and other plot parameters
- **Fast Rendering**: Leverages xarray and Fimex for efficient data handling

## Requirements

- Python 3.8+
- xarray
- cfgrib (for GRIB support)
- netCDF4
- matplotlib
- PyQt6
- fimex (optional, for advanced features)

## Installation

```bash
git clone https://github.com/trygveasp/xarray-plotter-gui.git
cd xarray-plotter-gui
pip install -r requirements.txt
```

## Usage

```bash
python main.py
```

Then use the GUI to:
1. Click "Open File" to select a GRIB or NetCDF file
2. Select a variable to visualize
3. Adjust time steps and levels using the controls
4. Customize plot appearance with the provided options

## File Structure

```
xarray-plotter-gui/
├── main.py                 # Entry point
├── gui/
│   ├── __init__.py
│   ├── main_window.py      # Main application window
│   ├── plot_widget.py      # Matplotlib plotting widget
│   └── controls.py         # Control panels for variables, time, levels
├── data/
│   ├── __init__.py
│   └── loader.py           # File loading and xarray operations
├── plotting/
│   ├── __init__.py
│   └── renderer.py         # Plotting and rendering logic
├── requirements.txt
└── README.md
```

## License

MIT License
