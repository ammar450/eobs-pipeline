# Climate KG Pipeline - Troubleshooting Guide

## Common Issues and Solutions

### 1. Installation Issues

#### Problem: "No module named 'netCDF4'"
```bash
# Solution: Activate virtual environment
source venv/bin/activate
pip install netCDF4
```

#### Problem: "Python version too old"
```bash
# Check version
python --version

# Need Python 3.9+. If not available, load module:
module load python/3.9
python3.9 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

---

### 2. Runtime Errors

#### Problem: "NetCDF file not found"
```bash
# Check files exist
ls -lh netcdf/*.nc

# Verify config paths
python -c "from code.config import NETCDF_DIR; print(NETCDF_DIR)"
```

#### Problem: "Memory error" or "Killed"
```python
# Edit code/config.py - reduce sampling:
SPATIAL_SAMPLE_EVERY_N = 20  # Increase from 10
TIME_BATCH_YEARS = 2         # Reduce from 5

# Or process fewer years:
python code/pipeline.py --start-year 2020 --end-year 2020
```

#### Problem: "No valid observations extracted"
```bash
# Check NetCDF file contents
python -c "
import xarray as xr
ds = xr.open_dataset('netcdf/tg_ens_mean_0.25deg_reg_v31.0e.nc')
print(ds)
print('Variables:', list(ds.data_vars))
print('Time range:', ds.time.values[0], 'to', ds.time.values[-1])
"
```

---

### 3. Validation Errors

#### Problem: "Graph validation failed"
```bash
# Check logs for specific errors
cat ttl/pipeline.log | grep ERROR

# Common causes:
# 1. Missing mandatory properties - check rdf_builder.py
# 2. example.org URIs - check config.py BASE_URI
# 3. Invalid RDF syntax - check Turtle serialization
```

#### Problem: "Rapper validation failed"
```bash
# Check if rapper is installed
which rapper

# Install if missing (Ubuntu/Debian)
sudo apt-get install raptor2-utils

# Or disable in config.py
VALIDATE_WITH_RAPPER = False
```

#### Problem: "rapper: <stdin>:42: syntax error"
```bash
# View the problematic line
head -n 50 ttl/your_file.ttl

# Usually indicates malformed URIs or literals
# Check for special characters in data
```

---

### 4. Performance Issues

#### Problem: "Processing too slow"
```python
# Optimize in code/config.py:

# Increase spatial sampling (fewer grid cells)
SPATIAL_SAMPLE_EVERY_N = 20  # or 50 for very fast

# Smaller time batches
TIME_BATCH_YEARS = 2

# Larger chunks (more memory, faster)
CHUNK_SIZE = 50000
```

#### Problem: "Files too large"
```python
# Reduce spatial sampling
SPATIAL_SAMPLE_EVERY_N = 20

# Smaller time batches
TIME_BATCH_YEARS = 2

# Or process specific regions only (edit netcdf_reader.py)
```

---

### 5. Data Issues

#### Problem: "All values are NaN"
```bash
# Inspect NetCDF variable
python -c "
import xarray as xr
ds = xr.open_dataset('netcdf/tg_ens_mean_0.25deg_reg_v31.0e.nc')
print('Variables:', list(ds.data_vars))
# Try each variable name
for var in ds.data_vars:
    print(f'{var}:', ds[var].values.shape)
    print('  Sample:', ds[var].values[0, 0, 0])
"
```

#### Problem: "Timestamps incorrect"
```bash
# Check time coordinate
python -c "
import xarray as xr
ds = xr.open_dataset('netcdf/tg_ens_mean_0.25deg_reg_v31.0e.nc')
print('Time units:', ds.time.attrs)
print('First 5 times:', ds.time.values[:5])
"
```

---

### 6. SPARQL Query Issues

#### Problem: "No results from SPARQL query"
```sparql
# Debug: Check what exists
SELECT * WHERE { ?s ?p ?o } LIMIT 100

# Check specific types
SELECT (COUNT(?obs) as ?count) WHERE { 
    ?obs a <http://www.w3.org/ns/sosa/Observation> 
}

# Verify namespaces match
SELECT DISTINCT ?type WHERE { ?s a ?type }
```

#### Problem: "Fuseki won't load TTL file"
```bash
# Validate file first
rapper -i turtle ttl/your_file.ttl 2>&1 | head -20

# Check file size
ls -lh ttl/your_file.ttl

# Try smaller batch if too large
python code/pipeline.py --test
```

---

### 7. Output Issues

#### Problem: "No TTL files generated"
```bash
# Check logs
cat ttl/pipeline.log

# Run with verbose output
python code/pipeline.py --test 2>&1 | tee test_output.log

# Verify write permissions
ls -ld ttl/
```

#### Problem: "example.org URIs in output"
```bash
# This should NEVER happen - check config.py
grep -n "example.org" code/config.py

# Should find NONE in code
grep -r "example.org" code/

# If found in output, regenerate:
rm ttl/*.ttl
python code/pipeline.py --test
```

---

### 8. Module Import Errors

#### Problem: "ModuleNotFoundError: No module named 'config'"
```bash
# Run from correct directory
cd /home/amyo206h/climate_kg
python code/pipeline.py --test

# Or add to PYTHONPATH
export PYTHONPATH=/home/amyo206h/climate_kg/code:$PYTHONPATH
```

#### Problem: "ImportError: cannot import name 'X'"
```bash
# Check Python version
python --version  # Must be 3.9+

# Reinstall dependencies
pip install --upgrade -r requirements.txt
```

---

### 9. HPC/Cluster Specific

#### Problem: "Command not found" on HPC
```bash
# Load required modules
module load python/3.9
module load netcdf

# Activate environment
source venv/bin/activate
```

#### Problem: "Job killed by scheduler"
```bash
# Request more memory in job script
#SBATCH --mem=16G
#SBATCH --time=4:00:00

# Or reduce processing:
python code/pipeline.py --spatial-sample 50 --batch-years 2
```

---

### 10. Testing & Debugging

#### Quick Test Checklist
```bash
# 1. Test installation
python test_installation.py

# 2. Test with minimal data
python code/pipeline.py --test --test-year 2020

# 3. Check one variable, one year
python code/pipeline.py --variables tg --start-year 2020 --end-year 2020

# 4. Validate output
ls -lh ttl/*.ttl
rapper -i turtle ttl/*.ttl

# 5. Check logs
tail -100 ttl/pipeline.log
```

#### Enable Debug Logging
```python
# Edit code/config.py
LOG_LEVEL = "DEBUG"  # Change from "INFO"

# Then run pipeline
python code/pipeline.py --test
```

---

## Getting Help

### Check Documentation
```bash
# Main README
cat code/README.md

# Summary
cat SUMMARY.md

# Module docstrings
python -c "import code.rdf_builder; help(code.rdf_builder.RDFBuilder)"
```

### Useful Commands
```bash
# Check environment
which python
pip list | grep -E "netCDF4|rdflib|xarray"

# Check NetCDF files
ncdump -h netcdf/tg_ens_mean_0.25deg_reg_v31.0e.nc | head -50

# Monitor resources
# During processing:
watch -n 1 'ps aux | grep python | grep -v grep'
```

### Contact Information
For E-OBS data issues: https://www.ecad.eu/contact.php
For RDF/SPARQL issues: Check W3C documentation

---

## Prevention Tips

1. **Always test first**: Use `--test` mode before full runs
2. **Start small**: Process 1 year before 74 years
3. **Monitor resources**: Watch memory/disk during processing
4. **Validate incrementally**: Check each output file
5. **Keep logs**: Save pipeline.log for debugging
6. **Backup config**: Before modifying config.py
7. **Version control**: Use git for code changes

---

## Emergency Recovery

### Pipeline Hangs
```bash
# Kill process
pkill -f pipeline.py

# Check for zombie processes
ps aux | grep python

# Clean partial files
rm ttl/*_incomplete.ttl

# Restart from last successful batch
# Check logs for last completed year
```

### Disk Full
```bash
# Check space
df -h

# Remove old logs
rm ttl/pipeline.log.old

# Compress old TTL files
gzip ttl/eobs_climate_kg_*_2015_*.ttl
```

### Corrupted Output
```bash
# Validate all files
for f in ttl/*.ttl; do
    echo "Checking $f"
    rapper -i turtle "$f" > /dev/null 2>&1 || echo "FAILED: $f"
done

# Remove invalid files
# (Back up first!)
# rm ttl/failed_file.ttl

# Regenerate specific batch
python code/pipeline.py --variables tg --start-year 2015 --end-year 2015
```

---

**Last Updated**: 2025-11-30  
**Version**: 1.0
