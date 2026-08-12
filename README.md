# E-OBS Climate Knowledge Graph Pipeline

**Production-ready Python pipeline for converting E-OBS NetCDF climate data into semantic RDF/Turtle knowledge graphs using W3C-standard ontologies.**

[![Python 3.9+](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/)
[![RDFLib 7.x](https://img.shields.io/badge/rdflib-7.x-green.svg)](https://rdflib.readthedocs.io/)
[![SOSA/SSN](https://img.shields.io/badge/ontology-SOSA%2FSSN-orange.svg)](https://www.w3.org/TR/vocab-ssn/)

---

## 📋 Overview

This pipeline transforms E-OBS v31.0e ensemble mean NetCDF files into queryable RDF/Turtle format following W3C semantic web standards. The system generates SOSA (Sensor, Observation, Sample, and Actuator) observation patterns organized into observation collections, enabling SPARQL queries and semantic integration for climate data analysis. 

This GitHub repository documents only the transformation pipeline into RDF. To see an agent that uses the knowledge graph, see https://github.com/ammar450/climate-chat-agent.

### Key Features

✅ W3C SOSA/SSN ontology patterns  
✅ Streamlined 8-prefix namespace design  
✅ Observation collections by variable and time period  
✅ CF Standard Names alignment  
✅ Scalable multi-year, multi-variable processing  
✅ Production URIs (climate-kg.org domain)  
✅ Built-in RDF graph validation  

### Supported Climate Variables

5 climate variables: **fg** (wind speed), **hu** (humidity), **qq** (radiation), **rr** (precipitation), **tg** (mean temp)


### Data Model 

<img width="922" height="352" alt="final_data_model (1)" src="https://github.com/user-attachments/assets/e87f7352-870e-47d1-88db-4838b639205e" />

### Conversion Pipeline 

<img width="1669" height="726" alt="pipeline" src="https://github.com/user-attachments/assets/4e516440-ddd3-4033-8e10-0f6f54eb8e10" />

---

## 🚀 Quick Start

### Prerequisites

- Python 3.9+ (tested with Python 3.13)
- E-OBS NetCDF files (v31.0e ensemble mean, 0.25° resolution)

### Installation

```bash
# Clone/download repository
cd code

# Activate virtual environment
.\.venv\Scripts\Activate.ps1  # Windows
# source .venv/bin/activate    # Linux/Mac

# Verify installation
python test_installation.py
```

### Basic Usage

```bash
# Quick test (1 year, 1 variable)
python pipeline.py --test

# Process all variables for one year
python pipeline.py --start-year 2020 --end-year 2020

# Process multi-year range
python pipeline.py --start-year 2020 --end-year 2024

# Specific variables
python pipeline.py --variables tg tn tx --start-year 2015 --end-year 2024
```

**Output**: Generated `.ttl` files in `ttl/` directory with naming pattern `eobs_climate_kg_{year_start}_{year_end}_{timestamp}.ttl`

---

## 📚 Documentation

| Document | Description |
|----------|-------------|
| **[Architecture & Workflow](docs/ARCHITECTURE.md)** | Repository structure, pipeline workflow, module details |
| **[RDF Model](docs/RDF_MODEL.md)** | Ontologies, URI patterns, SOSA patterns, design principles |
| **[SPARQL Examples](docs/SPARQL_EXAMPLES.md)** | Query examples for common use cases |
| **[Performance](docs/PERFORMANCE.md)** | Benchmarks, scalability, optimization tips |
| **[Configuration](TROUBLESHOOTING.md)** | Advanced options, troubleshooting guide |
| **[Contributing](docs/CONTRIBUTING.md)** | License, citation, contributing guidelines |
| [PROJECT_OVERVIEW.txt](PROJECT_OVERVIEW.txt) | Comprehensive project guide |
| [CONVERSION_FLOW.md](CONVERSION_FLOW.md) | Detailed data transformation flow |

---

## 🔧 Common Operations

### Output Statistics

| Time Range | Variables | Observations | File Size |
|------------|-----------|--------------|-----------|
| 1 year (2020) | All 5 | ~10,000 | ~4 MB |
| 5 years (2020-2024) | All 5 | ~10,000 | ~4 MB |

*Note: Based on sampled data (every 10th grid cell)*

### Command-Line Options

| Option | Description | Default |
|--------|-------------|---------|
| `--test` | Run test mode (quick validation) | - |
| `--variables` | Select specific variables (e.g., `tg tn tx`) | all |
| `--start-year` | Starting year | 1950 |
| `--end-year` | Ending year | 2024 |
| `--batch-years` | Years per output file | 5 |
| `--spatial-sample` | Sample every Nth grid cell | 10 |

### Validation

```bash
# Run installation test
python test_installation.py

# Run pipeline test
python code/pipeline.py --test

# Check output file
ls -lh ttl/*.ttl
```

---

## ⚡ Quick References

### Supported Variables

| Code | Description | Unit | CF Standard Name |
|------|-------------|------|------------------|
| **fg** | Mean Wind Speed | m/s | `wind_speed` |
| **hu** | Relative Humidity | % | `relative_humidity` |
| **qq** | Global Radiation | W/m² | `surface_downwelling_shortwave_flux_in_air` |
| **rr** | Precipitation Amount | mm | `precipitation_amount` |
| **tg** | Mean Temperature | °C | `air_temperature` |

### Key Resources

- **E-OBS Dataset**: https://www.ecad.eu/download/ensembles/download.php
- **SOSA/SSN Ontology**: https://www.w3.org/TR/vocab-ssn/
- **RDFLib Documentation**: https://rdflib.readthedocs.io/
- **CF Standard Names**: http://vocab.nerc.ac.uk/standard_name/

**Status**: ✅ Production Ready | **Last Updated**: July 23, 2026

For detailed information, see the [documentation](#-documentation) section above.

---

## 🙏 Acknowledgments

The work has been funded by the European Project EOSC Data Commons. A dump of the knowledge graph is available at https://doi.org/10.34740/kaggle/ds/10081642. 

If you reuse the EOBS knowledge graph, please cite:

```bash

@inproceedings{yousafEOBSKnowledgeGraph2026,
	address = {Ghent, Belgium},
	title = {The EOBS knowledge graph: A knowledge graph of European climate observations},
	booktitle = {SEMANTiCS 2026 - Poster and Demo Track},
	author = {Yousaf, Ammar and Degbelo, Auriol},
	year = {2026},
}


```

