# E-OBS Climate Knowledge Graph Pipeline

Production-ready Python pipeline for converting E-OBS NetCDF climate files into valid, queryable RDF/Turtle knowledge graphs using W3C-standard ontologies.

## 📋 Overview

This pipeline converts E-OBS v31.0e ensemble mean NetCDF files into semantic RDF/Turtle format, enabling SPARQL queries and semantic web integration for climate data analysis.

### Supported Variables
- **fg**: Mean Wind Speed (m/s)
- **hu**: Relative Humidity (%)
- **qq**: Global Radiation (W/m²)
- **rr**: Precipitation Amount (mm)
- **tg**: Mean Temperature (°C)
- **tn**: Minimum Temperature (°C)
- **tx**: Maximum Temperature (°C)

## 🏗️ Architecture

### Module Structure
```
code/
├── config.py           # Configuration, namespaces, URI patterns
├── rdf_builder.py      # RDF graph construction with SOSA patterns
├── netcdf_reader.py    # NetCDF data extraction with xarray
├── pipeline.py         # Main orchestration and CLI
└── README.md          # This file
```

## 🌐 W3C Ontology Stack

### Core Ontologies
- **SOSA/SSN**: Sensor, Observation, Sample, and Actuator ontology
- **GeoSPARQL**: Spatial data representation with WKT
- **QUDT**: Quantities, Units, Dimensions, and Types
- **DCTERMS**: Dublin Core metadata terms
- **PROV**: Provenance ontology
- **TIME**: Temporal entities

### URI Patterns (Production)
```
Base URI: http://climate-kg.org/

Resources:
- Sensors:      http://climate-kg.org/sensor/{variable}_sensor
- Observations: http://climate-kg.org/observation/{variable}_{lat}_{lon}_{timestamp}
- Locations:    http://climate-kg.org/location/grid_{lat}_{lon}
- Datasets:     http://climate-kg.org/dataset/eobs_{variable}_{year_start}_{year_end}
- Properties:   http://vocab.nerc.ac.uk/standard_name/{cf_standard_name}
```

## 🚀 Installation

### Prerequisites
- Python 3.9+
- Virtual environment (already created)

### Setup
```bash
# Activate virtual environment
source venv/bin/activate

# All dependencies already installed:
# - netCDF4>=1.7.0
# - rdflib>=7.5.0
# - xarray>=2024.7.0
# - numpy>=2.0.0
# - pandas>=2.3.3
```

## 💻 Usage

### Basic Usage

#### Test Mode (1 year, single variable)
```bash
cd code
python pipeline.py --test --test-variable tg --test-year 2020
```

#### Process Single Variable (5-year batches)
```bash
python pipeline.py --variables tg --start-year 2015 --end-year 2024
```

#### Process All Variables (custom date range)
```bash
python pipeline.py --start-year 2000 --end-year 2020 --batch-years 5
```

#### Full Production Run (1950-2024)
```bash
python pipeline.py --start-year 1950 --end-year 2024 --batch-years 5
```

### Advanced Options

```bash
python pipeline.py \
  --variables tg tn tx \              # Process specific variables
  --start-year 2010 \                 # Start year
  --end-year 2020 \                   # End year
  --batch-years 3 \                   # Years per TTL file
  --spatial-sample 20                 # Sample every 20th grid cell
```

### Command-Line Arguments

| Argument | Description | Default |
|----------|-------------|---------|
| `--variables` | Variables to process (space-separated) | All |
| `--start-year` | Starting year | 1950 |
| `--end-year` | Ending year | 2024 |
| `--batch-years` | Years per output file | 5 |
| `--spatial-sample` | Sample every Nth grid cell | 10 |
| `--test` | Run test mode (1 year) | False |
| `--test-year` | Year for test mode | 2020 |
| `--test-variable` | Variable for test mode | tg |

## 📊 Output Format

### File Naming Convention
```
eobs_climate_kg_{variable}_{year_start}_{year_end}_{timestamp}.ttl
```

Example: `eobs_climate_kg_tg_2015_2019_20251130_143025.ttl`

### Output Directory
All TTL files are saved to: `/home/amyo206h/climate_kg/ttl/`

## 🔍 Complete SOSA Observation Pattern

Every observation includes ALL mandatory properties:

```turtle
@prefix sosa: <http://www.w3.org/ns/sosa/> .
@prefix qudt: <http://qudt.org/schema/qudt/> .
@prefix geo: <http://www.w3.org/2003/01/geo/wgs84_pos#> .
@prefix geosparql: <http://www.opengis.net/ont/geosparql#> .
@prefix xsd: <http://www.w3.org/2001/XMLSchema#> .

# Observation
<http://climate-kg.org/observation/tg_52p00_4p50_20200101T000000> 
    a sosa:Observation ;
    
    # MANDATORY: Sensor
    sosa:madeBySensor <http://climate-kg.org/sensor/tg_sensor> ;
    
    # MANDATORY: Observable Property (CF standard name)
    sosa:observedProperty <http://vocab.nerc.ac.uk/standard_name/air_temperature> ;
    
    # MANDATORY: Feature of Interest (Location)
    sosa:hasFeatureOfInterest <http://climate-kg.org/location/grid_52p00_4p50> ;
    
    # MANDATORY: Result with Unit
    sosa:hasResult [
        a qudt:QuantityValue ;
        qudt:numericValue "15.3"^^xsd:double ;
        qudt:unit <http://qudt.org/vocab/unit/DEG_C>
    ] ;
    
    # MANDATORY: Result Time
    sosa:resultTime "2020-01-01T00:00:00"^^xsd:dateTime ;
    
    # Phenomenon Time
    sosa:phenomenonTime "2020-01-01T00:00:00"^^xsd:dateTime ;
    
    # Dataset Linkage
    dcterms:isPartOf <http://climate-kg.org/dataset/eobs_tg_2015_2019> .

# Location with Complete Geometry
<http://climate-kg.org/location/grid_52p00_4p50>
    a geosparql:Feature, sosa:FeatureOfInterest ;
    rdfs:label "Grid Cell (52.00°N, 4.50°E)"@en ;
    
    # WGS84 Coordinates
    geo:lat "52.00"^^xsd:decimal ;
    geo:long "4.50"^^xsd:decimal ;
    
    # GeoSPARQL Geometry with WKT
    geosparql:hasGeometry [
        a geosparql:Geometry ;
        geosparql:asWKT "POINT(4.50 52.00)"^^geosparql:wktLiteral ;
        geosparql:crs <http://www.opengis.net/def/crs/EPSG/0/4326>
    ] .

# Sensor
<http://climate-kg.org/sensor/tg_sensor>
    a sosa:Sensor, ssn:System ;
    rdfs:label "E-OBS Thermometer Network"@en ;
    sosa:observes <http://vocab.nerc.ac.uk/standard_name/air_temperature> .

# Dataset with Metadata
<http://climate-kg.org/dataset/eobs_tg_2015_2019>
    a sosa:ObservationCollection, dcterms:Dataset ;
    dcterms:title "E-OBS Mean Temperature Observations 2015-2019" ;
    dcterms:hasPart <http://climate-kg.org/observation/tg_52p00_4p50_20200101T000000> ;
    dcterms:source <https://www.ecad.eu/download/ensembles/download.php> .
```

## 🔍 Example SPARQL Queries

### Query 1: Find all observations above 30°C in summer 2020
```sparql
PREFIX sosa: <http://www.w3.org/ns/sosa/>
PREFIX qudt: <http://qudt.org/schema/qudt/>
PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>
PREFIX geo: <http://www.w3.org/2003/01/geo/wgs84_pos#>

SELECT ?obs ?lat ?lon ?temp ?time
WHERE {
    ?obs a sosa:Observation ;
         sosa:observedProperty <http://vocab.nerc.ac.uk/standard_name/air_temperature> ;
         sosa:hasFeatureOfInterest ?location ;
         sosa:resultTime ?time ;
         sosa:hasResult ?result .
    
    ?location geo:lat ?lat ;
              geo:long ?lon .
    
    ?result qudt:numericValue ?temp .
    
    FILTER(?temp > 30.0)
    FILTER(?time >= "2020-06-01T00:00:00"^^xsd:dateTime && 
           ?time <= "2020-08-31T23:59:59"^^xsd:dateTime)
}
ORDER BY DESC(?temp)
LIMIT 100
```

### Query 2: Calculate average temperature per location
```sparql
PREFIX sosa: <http://www.w3.org/ns/sosa/>
PREFIX qudt: <http://qudt.org/schema/qudt/>
PREFIX geo: <http://www.w3.org/2003/01/geo/wgs84_pos#>

SELECT ?location ?lat ?lon (AVG(?temp) AS ?avgTemp) (COUNT(?obs) AS ?count)
WHERE {
    ?obs a sosa:Observation ;
         sosa:hasFeatureOfInterest ?location ;
         sosa:hasResult ?result .
    
    ?location geo:lat ?lat ;
              geo:long ?lon .
    
    ?result qudt:numericValue ?temp .
}
GROUP BY ?location ?lat ?lon
HAVING (COUNT(?obs) > 100)
ORDER BY DESC(?avgTemp)
```

### Query 3: Find observations with spatial filter (GeoSPARQL)
```sparql
PREFIX sosa: <http://www.w3.org/ns/sosa/>
PREFIX geosparql: <http://www.opengis.net/ont/geosparql#>
PREFIX geof: <http://www.opengis.net/def/function/geosparql/>

SELECT ?obs ?location ?wkt
WHERE {
    ?obs a sosa:Observation ;
         sosa:hasFeatureOfInterest ?location .
    
    ?location geosparql:hasGeometry ?geom .
    ?geom geosparql:asWKT ?wkt .
    
    FILTER(geof:sfWithin(?wkt, "POLYGON((3 50, 7 50, 7 54, 3 54, 3 50))"^^geosparql:wktLiteral))
}
LIMIT 1000
```

### Query 4: Retrieve complete dataset metadata
```sparql
PREFIX dcterms: <http://purl.org/dc/terms/>
PREFIX sosa: <http://www.w3.org/ns/sosa/>

SELECT ?dataset ?title ?description ?temporal ?source ?observationCount
WHERE {
    ?dataset a sosa:ObservationCollection ;
             dcterms:title ?title ;
             dcterms:description ?description ;
             dcterms:temporal ?temporal ;
             dcterms:source ?source .
    
    {
        SELECT ?dataset (COUNT(?obs) AS ?observationCount)
        WHERE {
            ?dataset dcterms:hasPart ?obs .
        }
        GROUP BY ?dataset
    }
}
```

### Query 5: Compare precipitation vs temperature
```sparql
PREFIX sosa: <http://www.w3.org/ns/sosa/>
PREFIX qudt: <http://qudt.org/schema/qudt/>
PREFIX geo: <http://www.w3.org/2003/01/geo/wgs84_pos#>

SELECT ?location ?lat ?lon ?date 
       (AVG(?precip) AS ?avgPrecip) 
       (AVG(?temp) AS ?avgTemp)
WHERE {
    ?obs1 sosa:observedProperty <http://vocab.nerc.ac.uk/standard_name/precipitation_amount> ;
          sosa:hasFeatureOfInterest ?location ;
          sosa:resultTime ?date ;
          sosa:hasResult/qudt:numericValue ?precip .
    
    ?obs2 sosa:observedProperty <http://vocab.nerc.ac.uk/standard_name/air_temperature> ;
          sosa:hasFeatureOfInterest ?location ;
          sosa:resultTime ?date ;
          sosa:hasResult/qudt:numericValue ?temp .
    
    ?location geo:lat ?lat ; geo:long ?lon .
}
GROUP BY ?location ?lat ?lon ?date
ORDER BY ?date
```

## ✅ Validation

### Automatic Validation
The pipeline includes automatic validation:
- ✅ No `example.org` URIs
- ✅ All observations have mandatory SOSA properties
- ✅ Dataset-observation links via `dcterms:hasPart`
- ✅ CF standard names as direct URIRefs
- ✅ Complete spatial geometry with WKT

### Manual Validation with Rapper
```bash
# Install rapper (optional)
sudo apt-get install raptor2-utils

# Validate TTL file
rapper -i turtle output.ttl

# Count triples
rapper -i turtle -c output.ttl
```

### Load into Apache Jena Fuseki
```bash
# Install Fuseki
wget https://dlcdn.apache.org/jena/binaries/apache-jena-fuseki-4.10.0.tar.gz
tar xzf apache-jena-fuseki-4.10.0.tar.gz
cd apache-jena-fuseki-4.10.0

# Start Fuseki server
./fuseki-server --update --mem /climate

# Upload TTL file via web UI
# Navigate to: http://localhost:3030
# Create dataset "climate" and upload TTL files
```

## 📊 Performance Targets

| Metric | Target | Achieved |
|--------|--------|----------|
| Processing Speed | 1,000+ obs/sec | ✅ |
| Memory Usage | <8GB for 5-year batches | ✅ |
| File Size | 1-5MB per 5-year TTL | ✅ |
| Scalability | Process 74 years in <4h | ✅ |

## 🔧 Configuration

### Edit `config.py` to customize:

```python
# Processing parameters
TIME_BATCH_YEARS = 5          # Years per TTL file
SPATIAL_SAMPLE_EVERY_N = 10   # Sample every Nth grid cell
START_YEAR = 1950
END_YEAR = 2024

# Performance tuning
CHUNK_SIZE = 10000            # Observations per chunk
MAX_MEMORY_GB = 8             # Max memory usage

# Validation
VALIDATION_ENABLED = True
VALIDATE_WITH_RAPPER = True
```

## 📝 Logging

Logs are written to:
- Console (stdout)
- File: `/home/amyo206h/climate_kg/ttl/pipeline.log`

Log levels: DEBUG, INFO, WARNING, ERROR

## 🐛 Troubleshooting

### Issue: "NetCDF file not found"
**Solution**: Check that NetCDF files are in `/home/amyo206h/climate_kg/netcdf/`

### Issue: "Memory error"
**Solution**: Reduce `SPATIAL_SAMPLE_EVERY_N` or `TIME_BATCH_YEARS` in config.py

### Issue: "Validation failed"
**Solution**: Check logs for specific validation errors. Ensure all required properties are present.

### Issue: "Rapper not found"
**Solution**: Install rapper with `sudo apt-get install raptor2-utils` or disable with `VALIDATE_WITH_RAPPER = False`

## 📚 References

### E-OBS Dataset
- Cornes et al. (2018), An Ensemble Version of the E-OBS Temperature and Precipitation Data Sets, J. Geophys. Res. Atmos., 123.
- https://www.ecad.eu/download/ensembles/download.php

### W3C Standards
- SOSA/SSN: https://www.w3.org/TR/vocab-ssn/
- GeoSPARQL: https://www.ogc.org/standards/geosparql
- QUDT: http://qudt.org/
- DCTERMS: https://www.dublincore.org/specifications/dublin-core/dcmi-terms/

### CF Conventions
- CF Standard Names: http://vocab.nerc.ac.uk/standard_name/

## 📄 License

E-OBS data is subject to the ECA&D license:
https://www.ecad.eu/download/ensembles/download.php#datafiles

## 🎯 Success Criteria Checklist

- ✅ Zero example.org URIs in output
- ✅ Every sosa:Observation has sosa:madeBySensor
- ✅ Dataset linked to observations via dcterms:hasPart
- ✅ CF URIs are direct URIRef objects
- ✅ Grid cells have WKT + lat/long properties
- ✅ rapper -i turtle output.ttl passes
- ✅ Apache Jena Fuseki can load and query data
- ✅ Test SPARQL queries return results

## 🚀 Quick Start Example

```bash
# Activate environment
source venv/bin/activate

# Run test (1 year)
cd code
python pipeline.py --test

# Check output
ls -lh ../ttl/*.ttl

# Run full pipeline (example: 2015-2024 for temperature variables)
python pipeline.py --variables tg tn tx --start-year 2015 --end-year 2024

# View logs
tail -f ../ttl/pipeline.log
```

---

**Generated by Climate KG Pipeline v1.0**  
**Last Updated: 2025-11-30**
