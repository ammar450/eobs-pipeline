"""
NetCDF Reader module for extracting E-OBS climate data.
Handles efficient reading, spatial/temporal sampling, and data extraction.
"""

import xarray as xr
import numpy as np
import pandas as pd
from pathlib import Path
from typing import Dict, List, Tuple, Optional, Generator
from datetime import datetime
import logging

from config import (
    NETCDF_DIR, NETCDF_FILES, VARIABLE_MAPPINGS,
    SPATIAL_SAMPLE_EVERY_N, TEMPORAL_START_DATE, TEMPORAL_END_DATE
)

logger = logging.getLogger(__name__)


class NetCDFReader:
    """Reads and processes E-OBS NetCDF climate data files."""
    
    def __init__(self, variable_code: str):
        """
        Initialize NetCDF reader for a specific variable.
        
        Args:
            variable_code: E-OBS variable code (e.g., 'tg', 'rr')
        """
        self.variable_code = variable_code
        self.variable_info = VARIABLE_MAPPINGS[variable_code]
        self.file_path = NETCDF_DIR / NETCDF_FILES[variable_code]
        
        if not self.file_path.exists():
            raise FileNotFoundError(f"NetCDF file not found: {self.file_path}")
        
        self.dataset = None
        self._load_dataset()
    
    def _load_dataset(self):
        """Load NetCDF dataset with xarray."""
        logger.info(f"Loading NetCDF file: {self.file_path}")
        
        try:
            # Open dataset (without chunking for simplicity)
            self.dataset = xr.open_dataset(self.file_path)
            
            # Get variable name (usually matches the variable code)
            self.data_var = self._detect_data_variable()
            
            logger.info(f"Loaded dataset with variable: {self.data_var}")
            logger.info(f"Dataset dimensions: {dict(self.dataset.dims)}")
            logger.info(f"Time range: {self.dataset.time.values[0]} to {self.dataset.time.values[-1]}")
            
        except Exception as e:
            logger.error(f"Failed to load NetCDF file: {e}")
            raise
    
    def _detect_data_variable(self) -> str:
        """
        Detect the main data variable in the NetCDF file.
        
        Returns:
            str: Name of the data variable
        """
        # Common E-OBS variable names
        possible_names = [
            self.variable_code,
            self.variable_code.upper(),
            self.variable_info['name'],
            'value',
            'data'
        ]
        
        for var_name in possible_names:
            if var_name in self.dataset.variables:
                return var_name
        
        # If not found, get the first non-coordinate variable
        coord_names = set(self.dataset.coords.keys())
        data_vars = [v for v in self.dataset.data_vars if v not in coord_names]
        
        if data_vars:
            logger.warning(f"Using first data variable: {data_vars[0]}")
            return data_vars[0]
        
        raise ValueError(f"Could not detect data variable in {self.file_path}")
    
    def get_temporal_range(self) -> Tuple[datetime, datetime]:
        """
        Get the temporal range of the dataset.
        
        Returns:
            Tuple[datetime, datetime]: Start and end timestamps
        """
        times = self.dataset.time.values
        start = pd.Timestamp(times[0]).to_pydatetime()
        end = pd.Timestamp(times[-1]).to_pydatetime()
        return start, end
    
    def get_spatial_extent(self) -> Dict[str, float]:
        """
        Get the spatial extent of the dataset.
        
        Returns:
            Dict with min/max latitude and longitude
        """
        lats = self.dataset.latitude.values
        lons = self.dataset.longitude.values
        
        return {
            'lat_min': float(lats.min()),
            'lat_max': float(lats.max()),
            'lon_min': float(lons.min()),
            'lon_max': float(lons.max())
        }
    
    def filter_temporal_range(
        self,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None
    ) -> xr.Dataset:
        """
        Filter dataset by temporal range.
        
        Args:
            start_date: Start date in ISO format (YYYY-MM-DD)
            end_date: End date in ISO format (YYYY-MM-DD)
            
        Returns:
            xr.Dataset: Filtered dataset
        """
        ds = self.dataset
        
        if start_date:
            ds = ds.sel(time=slice(start_date, None))
            logger.info(f"Filtered data from {start_date}")
        
        if end_date:
            ds = ds.sel(time=slice(None, end_date))
            logger.info(f"Filtered data until {end_date}")
        
        return ds
    
    def filter_by_year_range(
        self,
        start_year: int,
        end_year: int
    ) -> xr.Dataset:
        """
        Filter dataset by year range.
        
        Args:
            start_year: Starting year (inclusive)
            end_year: Ending year (inclusive)
            
        Returns:
            xr.Dataset: Filtered dataset
        """
        start_date = f"{start_year}-01-01"
        end_date = f"{end_year}-12-31"
        
        logger.info(f"Filtering data for years {start_year}-{end_year}")
        return self.filter_temporal_range(start_date, end_date)
    
    def sample_spatial_grid(
        self,
        every_n: int = SPATIAL_SAMPLE_EVERY_N
    ) -> Tuple[np.ndarray, np.ndarray]:
        """
        Sample spatial grid at regular intervals.
        
        Args:
            every_n: Sample every Nth grid cell (1 = all cells)
            
        Returns:
            Tuple[np.ndarray, np.ndarray]: Sampled latitude and longitude arrays
        """
        lats = self.dataset.latitude.values[::every_n]
        lons = self.dataset.longitude.values[::every_n]
        
        logger.info(f"Sampled grid: {len(lats)} latitudes × {len(lons)} longitudes "
                   f"(every {every_n} cells)")
        
        return lats, lons
    
    def extract_observations(
        self,
        year_start: int,
        year_end: int,
        spatial_sample: int = SPATIAL_SAMPLE_EVERY_N,
        chunk_size: int = 10000
    ) -> Generator[Dict, None, None]:
        """
        Extract observations as a generator for memory efficiency.
        
        Args:
            year_start: Starting year
            year_end: Ending year
            spatial_sample: Sample every Nth grid cell
            chunk_size: Number of observations per chunk
            
        Yields:
            Dict: Observation data with keys: lat, lon, timestamp, value
        """
        # Filter by year range
        ds = self.filter_by_year_range(year_start, year_end)
        
        # Sample spatial grid
        lats, lons = self.sample_spatial_grid(spatial_sample)
        
        # Get data variable
        data = ds[self.data_var]
        
        # Get time coordinates
        times = ds.time.values
        
        logger.info(f"Extracting observations for {len(times)} time steps, "
                   f"{len(lats)} lats, {len(lons)} lons")
        
        total_observations = 0
        chunk_buffer = []
        
        # Iterate over sampled grid cells
        for lat_idx, lat in enumerate(lats):
            for lon_idx, lon in enumerate(lons):
                # Get nearest indices in the original grid
                lat_idx_orig = int(lat_idx * spatial_sample)
                lon_idx_orig = int(lon_idx * spatial_sample)
                
                # Extract time series for this location
                try:
                    # Select data for this grid cell
                    location_data = data.isel(
                        latitude=lat_idx_orig,
                        longitude=lon_idx_orig
                    ).values
                    
                    # Iterate over time steps
                    for time_idx, time_val in enumerate(times):
                        value = float(location_data[time_idx])
                        
                        # Skip NaN values
                        if np.isnan(value):
                            continue
                        
                        # Convert numpy datetime64 to ISO string
                        timestamp = pd.Timestamp(time_val).isoformat()
                        
                        observation = {
                            'lat': float(lat),
                            'lon': float(lon),
                            'timestamp': timestamp,
                            'value': value
                        }
                        
                        chunk_buffer.append(observation)
                        total_observations += 1
                        
                        # Yield chunk when buffer is full
                        if len(chunk_buffer) >= chunk_size:
                            yield from chunk_buffer
                            chunk_buffer = []
                
                except Exception as e:
                    logger.warning(f"Error extracting data at lat={lat}, lon={lon}: {e}")
                    continue
        
        # Yield remaining observations
        if chunk_buffer:
            yield from chunk_buffer
        
        logger.info(f"✅ Extracted {total_observations} valid observations")
    
    def get_metadata(self) -> Dict[str, any]:
        """
        Extract metadata from NetCDF file.
        
        Returns:
            Dict: Metadata including global attributes and variable attributes
        """
        metadata = {
            'global_attributes': dict(self.dataset.attrs),
            'variable_attributes': dict(self.dataset[self.data_var].attrs),
            'dimensions': dict(self.dataset.dims),
            'coordinates': list(self.dataset.coords.keys()),
            'data_variables': list(self.dataset.data_vars.keys())
        }
        
        return metadata
    
    def close(self):
        """Close the NetCDF dataset."""
        if self.dataset is not None:
            self.dataset.close()
            logger.info(f"Closed NetCDF dataset for {self.variable_code}")
    
    def __enter__(self):
        """Context manager entry."""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.close()
