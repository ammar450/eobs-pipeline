"""
Script to create dummy NetCDF files for testing the Climate KG pipeline.
Generates realistic E-OBS-style NetCDF files with proper dimensions and variables.
"""

import numpy as np
import netCDF4 as nc
from datetime import datetime, timedelta
from pathlib import Path

# Configuration
NETCDF_DIR = Path("netcdf")
START_DATE = datetime(2020, 1, 1)
END_DATE = datetime(2020, 12, 31)  # 1 year of data for testing
LAT_MIN, LAT_MAX = 50.0, 54.0
LON_MIN, LON_MAX = 3.0, 7.0
LAT_RES = 0.25  # 0.25 degree resolution
LON_RES = 0.25

# Variable definitions matching config.py
VARIABLES = {
    "fg": {
        "file": "fg_ens_mean_0.25deg_reg_v31.0e.nc",
        "long_name": "Mean wind speed",
        "units": "m/s",
        "standard_name": "wind_speed",
        "value_range": (0, 15)
    },
    "hu": {
        "file": "hu_ens_mean_0.25deg_reg_v31.0e.nc",
        "long_name": "Relative humidity",
        "units": "%",
        "standard_name": "relative_humidity",
        "value_range": (30, 100)
    },
    "qq": {
        "file": "qq_ens_mean_0.25deg_reg_v31.0e.nc",
        "long_name": "Global radiation",
        "units": "W/m²",
        "standard_name": "surface_downwelling_shortwave_flux_in_air",
        "value_range": (0, 300)
    },
    "rr": {
        "file": "rr_ens_mean_0.25deg_reg_v31.0e (1).nc",
        "long_name": "Precipitation amount",
        "units": "mm",
        "standard_name": "precipitation_amount",
        "value_range": (0, 50)
    },
    "tg": {
        "file": "tg_ens_mean_0.25deg_reg_v31.0e.nc",
        "long_name": "Mean temperature",
        "units": "degrees Celsius",
        "standard_name": "air_temperature",
        "value_range": (-10, 30)
    },
    "tn": {
        "file": "tn_ens_mean_0.25deg_reg_v31.0e.nc",
        "long_name": "Minimum temperature",
        "units": "degrees Celsius",
        "standard_name": "air_temperature",
        "value_range": (-15, 25)
    },
    "tx": {
        "file": "tx_ens_mean_0.25deg_reg_v31.0e.nc",
        "long_name": "Maximum temperature",
        "units": "degrees Celsius",
        "standard_name": "air_temperature",
        "value_range": (-5, 35)
    }
}


def create_dummy_netcdf(var_code, var_info):
    """Create a dummy NetCDF file for a variable."""
    
    print(f"Creating {var_code}: {var_info['file']}")
    
    # Create filepath
    filepath = NETCDF_DIR / var_info['file']
    
    # Create dimensions
    lats = np.arange(LAT_MIN, LAT_MAX + LAT_RES, LAT_RES)
    lons = np.arange(LON_MIN, LON_MAX + LON_RES, LON_RES)
    
    # Create time dimension (daily data)
    days = (END_DATE - START_DATE).days + 1
    times = [START_DATE + timedelta(days=i) for i in range(days)]
    
    # Create NetCDF file
    with nc.Dataset(filepath, 'w', format='NETCDF4') as ncfile:
        # Create dimensions
        time_dim = ncfile.createDimension('time', len(times))
        lat_dim = ncfile.createDimension('latitude', len(lats))
        lon_dim = ncfile.createDimension('longitude', len(lons))
        
        # Create coordinate variables
        time_var = ncfile.createVariable('time', 'f8', ('time',))
        lat_var = ncfile.createVariable('latitude', 'f4', ('latitude',))
        lon_var = ncfile.createVariable('longitude', 'f4', ('longitude',))
        
        # Set coordinate attributes
        time_var.units = 'days since 1950-01-01 00:00:00'
        time_var.calendar = 'gregorian'
        time_var.standard_name = 'time'
        time_var.long_name = 'time'
        
        lat_var.units = 'degrees_north'
        lat_var.standard_name = 'latitude'
        lat_var.long_name = 'latitude'
        
        lon_var.units = 'degrees_east'
        lon_var.standard_name = 'longitude'
        lon_var.long_name = 'longitude'
        
        # Fill coordinate values
        time_var[:] = nc.date2num(times, units=time_var.units, calendar=time_var.calendar)
        lat_var[:] = lats
        lon_var[:] = lons
        
        # Create data variable
        data_var = ncfile.createVariable(
            var_code,
            'f4',
            ('time', 'latitude', 'longitude'),
            fill_value=-9999.0
        )
        
        # Set data variable attributes
        data_var.units = var_info['units']
        data_var.standard_name = var_info['standard_name']
        data_var.long_name = var_info['long_name']
        
        # Generate random data within realistic range
        min_val, max_val = var_info['value_range']
        
        # Create spatially and temporally correlated random data
        np.random.seed(42)  # For reproducibility
        
        # Generate base pattern
        for t in range(len(times)):
            # Add seasonal variation for temperature
            if 'temperature' in var_info['long_name'].lower():
                seasonal_factor = np.sin(2 * np.pi * t / 365) * 10
            else:
                seasonal_factor = 0
            
            # Generate spatial pattern with some randomness
            spatial_pattern = np.random.randn(len(lats), len(lons)) * 2
            base_value = (min_val + max_val) / 2 + seasonal_factor
            
            data_var[t, :, :] = base_value + spatial_pattern
            
            # Clip to valid range
            data_var[t, :, :] = np.clip(data_var[t, :, :], min_val, max_val)
        
        # Add global attributes
        ncfile.title = f"E-OBS {var_info['long_name']} ensemble mean"
        ncfile.institution = "European Climate Assessment & Dataset (ECA&D)"
        ncfile.source = "Dummy data for testing"
        ncfile.history = f"Created on {datetime.now().isoformat()}"
        ncfile.Conventions = "CF-1.6"
        ncfile.version = "31.0e"
    
    print(f"  ✓ Created {filepath}")
    print(f"  - Dimensions: time={len(times)}, lat={len(lats)}, lon={len(lons)}")
    print(f"  - Data shape: {(len(times), len(lats), len(lons))}")


def main():
    """Create all dummy NetCDF files."""
    
    print("=" * 70)
    print("Creating Dummy E-OBS NetCDF Files")
    print("=" * 70)
    print(f"Output directory: {NETCDF_DIR.absolute()}")
    print(f"Date range: {START_DATE.date()} to {END_DATE.date()}")
    print(f"Spatial extent: Lat {LAT_MIN}-{LAT_MAX}°, Lon {LON_MIN}-{LON_MAX}°")
    print(f"Resolution: {LAT_RES}°")
    print("=" * 70)
    print()
    
    # Create netcdf directory if it doesn't exist
    NETCDF_DIR.mkdir(exist_ok=True)
    
    # Create each variable file
    for var_code, var_info in VARIABLES.items():
        create_dummy_netcdf(var_code, var_info)
        print()
    
    print("=" * 70)
    print("✓ All dummy NetCDF files created successfully!")
    print("=" * 70)
    print()
    print("Files created:")
    for var_code, var_info in VARIABLES.items():
        filepath = NETCDF_DIR / var_info['file']
        size_mb = filepath.stat().st_size / (1024 * 1024)
        print(f"  - {var_info['file']} ({size_mb:.2f} MB)")


if __name__ == "__main__":
    main()
