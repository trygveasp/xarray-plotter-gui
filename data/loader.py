"""Data loader for GRIB and NetCDF files."""

import xarray as xr
from pathlib import Path


class DataLoader:
    """Load GRIB and NetCDF files using xarray."""

    def __init__(self):
        """Initialize data loader."""
        pass

    def load_file(self, file_path):
        """Load a GRIB or NetCDF file.

        Parameters
        ----------
        file_path : str or Path
            Path to the file to load

        Returns
        -------
        xarray.Dataset
            Loaded dataset

        Raises
        ------
        ValueError
            If file format is not supported
        FileNotFoundError
            If file does not exist
        """
        file_path = Path(file_path)

        if not file_path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")

        # Determine file type and load accordingly
        if file_path.suffix.lower() in [".grib", ".grib2", ".grb", ".grb2"]:
            return self._load_grib(file_path)
        elif file_path.suffix.lower() in [".nc", ".netcdf"]:
            return self._load_netcdf(file_path)
        elif file_path.suffix.lower() in [".grbfp"]:
            return self._load_fimex(file_path)
        else:
            raise ValueError(f"Unsupported file format: {file_path.suffix}")

    def _load_grib(self, file_path):
        """Load GRIB file.

        Parameters
        ----------
        file_path : Path
            Path to GRIB file

        Returns
        -------
        xarray.Dataset
            Loaded dataset
        """
        try:
            # Try loading with cfgrib engine
            ds = xr.open_dataset(file_path, engine="cfgrib")
            return ds
        except Exception as e:
            raise RuntimeError(f"Failed to load GRIB file: {str(e)}")

    def _load_netcdf(self, file_path):
        """Load NetCDF file.

        Parameters
        ----------
        file_path : Path
            Path to NetCDF file

        Returns
        -------
        xarray.Dataset
            Loaded dataset
        """
        try:
            ds = xr.open_dataset(file_path)
            return ds
        except Exception as e:
            raise RuntimeError(f"Failed to load NetCDF file: {str(e)}")

    def _load_fimex(self, file_path):
        """Load file with fimex engine.

        Parameters
        ----------
        file_path : Path
            Path to NetCDF file

        Returns
        -------
        xarray.Dataset
            Loaded dataset
        """
        try:
            file_path = str(file_path)
            ds = xr.open_dataset(file_path, engine="fimex")
            return ds
        except Exception as e:
            raise RuntimeError(f"Failed to load file with fimex: {str(e)}")
