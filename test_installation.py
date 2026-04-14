#!/usr/bin/env python3
"""
Quick test script to verify pipeline installation and dependencies.
"""

import sys
from pathlib import Path

print("=" * 80)
print("Climate KG Pipeline - Installation Test")
print("=" * 80)

# Test 1: Python version
print("\n1. Checking Python version...")
python_version = sys.version_info
print(f"   Python {python_version.major}.{python_version.minor}.{python_version.micro}")
if python_version.major >= 3 and python_version.minor >= 9:
    print("   ✅ Python version OK")
else:
    print("   ❌ Python 3.9+ required")
    sys.exit(1)

# Test 2: Import dependencies
print("\n2. Checking dependencies...")
dependencies = {
    'netCDF4': 'NetCDF4',
    'rdflib': 'rdflib',
    'xarray': 'xarray',
    'numpy': 'numpy',
    'pandas': 'pandas'
}

missing = []
for module, name in dependencies.items():
    try:
        __import__(module)
        print(f"   ✅ {name}")
    except ImportError:
        print(f"   ❌ {name} - MISSING")
        missing.append(name)

if missing:
    print(f"\n   ❌ Missing dependencies: {', '.join(missing)}")
    print("   Run: pip install " + " ".join(missing))
    sys.exit(1)

# Test 3: Check directory structure
print("\n3. Checking directory structure...")
base_dir = Path(__file__).parent
required_dirs = {
    'netcdf': base_dir / 'netcdf',
    'ttl': base_dir / 'ttl',
    'code': base_dir / 'code'
}

for name, path in required_dirs.items():
    if path.exists():
        print(f"   ✅ {name}/ directory exists")
    else:
        print(f"   ⚠️  {name}/ directory missing (will be created)")

# Test 4: Check NetCDF files
print("\n4. Checking NetCDF files...")
netcdf_dir = base_dir / 'netcdf'
if netcdf_dir.exists():
    nc_files = list(netcdf_dir.glob('*.nc'))
    print(f"   Found {len(nc_files)} NetCDF files:")
    for nc_file in nc_files:
        size_mb = nc_file.stat().st_size / (1024 * 1024)
        print(f"     - {nc_file.name} ({size_mb:.1f} MB)")
    
    if len(nc_files) == 0:
        print("   ⚠️  No NetCDF files found")
else:
    print("   ⚠️  NetCDF directory not found")

# Test 5: Check module imports
print("\n5. Checking pipeline modules...")
sys.path.insert(0, str(base_dir / 'code'))

try:
    import config
    print("   ✅ config.py")
except Exception as e:
    print(f"   ❌ config.py - {e}")
    sys.exit(1)

try:
    import rdf_builder
    print("   ✅ rdf_builder.py")
except Exception as e:
    print(f"   ❌ rdf_builder.py - {e}")
    sys.exit(1)

try:
    import netcdf_reader
    print("   ✅ netcdf_reader.py")
except Exception as e:
    print(f"   ❌ netcdf_reader.py - {e}")
    sys.exit(1)

try:
    import pipeline
    print("   ✅ pipeline.py")
except Exception as e:
    print(f"   ❌ pipeline.py - {e}")
    sys.exit(1)

# Test 6: Test RDF graph creation
print("\n6. Testing RDF graph creation...")
try:
    from rdf_builder import RDFBuilder
    builder = RDFBuilder()
    
    # Test dataset creation
    dataset_uri = builder.create_dataset('tg', 2020, 2020)
    
    # Test observation creation
    obs_uri = builder.create_observation(
        variable_code='tg',
        lat=52.0,
        lon=4.5,
        timestamp='2020-01-01T00:00:00',
        value=15.3,
        dataset_uri=dataset_uri
    )
    
    # Validate
    if builder.validate_observation(obs_uri):
        print("   ✅ RDF graph creation successful")
        stats = builder.get_statistics()
        print(f"      Triples: {stats['total_triples']}")
        print(f"      Observations: {stats['observations']}")
    else:
        print("   ❌ RDF validation failed")
        sys.exit(1)
        
except Exception as e:
    print(f"   ❌ RDF graph creation failed: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

# Summary
print("\n" + "=" * 80)
print("✅ ALL TESTS PASSED - Pipeline is ready to use!")
print("=" * 80)
print("\nNext steps:")
print("  1. Run test mode:    python code/pipeline.py --test")
print("  2. Process data:     python code/pipeline.py --variables tg --start-year 2020 --end-year 2020")
print("  3. Read the README:  cat code/README.md")
print("=" * 80)
