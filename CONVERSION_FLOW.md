# NetCDF to RDF/Turtle Conversion Flow

## Pipeline Architecture

```
┌────────────────────────────────┐
│     NetCDF Files (7 vars)      │
│     E-OBS v31.0e               │
│     Size: ~3 MB (sample data)  │
│     Coverage: Europe           │
│     Period: 2020 (366 days)    │
│     Resolution: 0.25°          │
└────────────┬───────────────────┘
             │
             ▼
┌────────────────────────────────┐
│    NetCDF Reader Module        │
│    (netcdf_reader.py)          │
│    - Load dataset with xarray  │
│    - Extract coordinates       │
│    - Filter time range         │
│    - Sample grid (every Nth)   │
│    - Yield observations        │
└────────────┬───────────────────┘
             │
             ▼
┌────────────────────────────────┐
│     RDF Builder Module         │
│     (rdf_builder.py)           │
│     - Create collections       │
│     - Create observations      │
│     - Link via sosa:hasMember  │
│     - Generate URIs            │
│     - Build RDF graph          │
└────────────┬───────────────────┘
             │
             ▼
┌────────────────────────────────┐
│       Validation               │
│       - Check properties       │
│       - Verify structure       │
│       - Count resources        │
└────────────┬───────────────────┘
             │
             ▼
┌────────────────────────────────┐
│    TTL Output Files            │
│    (Turtle serialization)      │
│    Size: ~4 MB per batch       │
│    Contains: ~10K observations │
│    Format: 8-prefix model      │
└────────────────────────────────┘
```

## Processing Steps

### 1. Read NetCDF Data

- **Input**: E-OBS NetCDF files for each variable
- **Process**:
  - Open file using xarray
  - Extract lat/lon coordinates
  - Filter by time range (e.g., 2020-2024)
  - Sample spatial grid (every 10th cell by default)
  - Iterate through time steps
- **Output**: Stream of (time, lat, lon, value) tuples

### 2. Transform to RDF

- **Input**: Observation data from NetCDF reader
- **Process**:
  - Generate URIs for observations, sensors, locations
  - Create ObservationCollection per variable
  - Build SOSA observation triples:
    - Type declaration (sosa:Observation)
    - Feature of interest (location URI)
    - Result (QUDT QuantityValue)
    - Sensor (variable-specific)
    - Property (CF standard name)
    - Time (resultTime)
  - Link observations to collection via sosa:hasMember
- **Output**: RDF graph in memory

### 3. Validate

- **Input**: RDF graph
- **Process**:
  - Check all observations have required properties
  - Verify correct types and structure
  - Count resources (observations, collections, etc.)
  - Report statistics
- **Output**: Validation pass/fail + statistics

### 4. Serialize to Turtle

- **Input**: Validated RDF graph
- **Process**:
  - Bind 8 namespace prefixes
  - Serialize graph to Turtle format
  - Write to timestamped output file
- **Output**: TTL file on disk

## Data Transformation Example

### Input: NetCDF Array Data

```python
# NetCDF structure:
Dataset {
  dimensions:
    time = 366 ;
    latitude = 17 ;
    longitude = 17 ;
  
  variables:
    float tg(time, latitude, longitude);
    float latitude(latitude);
    float longitude(longitude);
    int64 time(time);
    
  data:
    tg[0][0][0] = 15.23  # °C
    latitude[0] = 50.00
    longitude[0] = 3.00
    time[0] = "2020-01-01T00:00:00"
}
```

### Output: RDF/Turtle Triples

```turtle
@prefix cf: <http://vocab.nerc.ac.uk/standard_name/> .
@prefix geo1: <http://www.w3.org/2003/01/geo/wgs84_pos#> .
@prefix oboe: <http://ecoinformatics.org/oboe/oboe.1.2/oboe-core.owl#> .
@prefix observation: <http://climate-kg.org/observation/> .
@prefix qudt: <http://qudt.org/schema/qudt/> .
@prefix sosa: <http://www.w3.org/ns/sosa/> .
@prefix unit: <http://qudt.org/vocab/unit/> .
@prefix xsd: <http://www.w3.org/2001/XMLSchema#> .

# ObservationCollection
observation:eobs_tg_2020_2024 a oboe:ObservationCollection ;
    sosa:hasMember observation:tg_50p00_3p00_20200101T000000 .

# Individual Observation
observation:tg_50p00_3p00_20200101T000000 a sosa:Observation ;
    sosa:hasFeatureOfInterest geo1:grid_50p00_3p00 ;
    sosa:hasResult [
        a qudt:QuantityValue ;
        qudt:numericValue 1.523000e+01 ;
        qudt:unit unit:DEG_C
    ] ;
    sosa:madeBySensor sosa:tg_sensor ;
    sosa:observedProperty cf:air_temperature ;
    sosa:resultTime "2020-01-01T00:00:00"^^xsd:dateTime .
```

## Dataset Coverage

**Spatial:** Europe (gridded at 0.25° resolution)  
**Temporal:** 2020 (366 days, leap year) for test data  
**Variables:** 7 climate variables (fg, hu, qq, rr, tg, tn, tx)  
**Sampling:** Every 10th grid cell (configurable)

## Data Size

### Input (NetCDF)
- **7 files total** (0.25° resolution, sample data)
  - Each variable: ~400-500 KB
  - Total: ~3 MB

### Output (TTL)
- **1 merged file per year range**
  - 1 year, all variables: ~4 MB
  - 5 years, all variables: ~20 MB
  - Contains: ~10,000 observations per year (sampled)

### Data Expansion
NetCDF → TTL conversion typically expands file size by ~10x due to:
- Semantic enrichment with URIs and ontology references
- Explicit relationships and metadata
- Human-readable Turtle format (vs binary NetCDF)
- Collection structures and linking

## Simplified RDF Model

The pipeline uses a **minimal 8-prefix design** for clarity:

1. **cf**: Climate and Forecast standard names
2. **geo1**: WGS84 geographic positions  
3. **oboe**: Observation collections
4. **observation**: Climate-kg.org observations and collections
5. **qudt**: Quantity values and schemas
6. **sosa**: Sensors and observations
7. **unit**: QUDT unit vocabulary
8. **xsd**: XML Schema datatypes

**Key Design Choices:**
- Collections group observations (one per variable and time period)
- Sensors use sosa: prefix (not separate namespace)
- Locations use geo1: prefix (not separate namespace)
- No spatial geometry triples (location URIs are references only)
- No metadata overhead (focus on core observation data)
- Direct CF standard name URIs (no property definitions)

## Performance Characteristics

| Metric | Value |
|--------|-------|
| **Processing Speed** | ~1,200 obs/sec |
| **Memory Usage** | <2 GB |
| **Validation** | ~400ms for 10K observations |
| **Serialization** | ~5 seconds for 4 MB file |

## Configuration Options

Customize behavior in `code/config.py`:

```python
SPATIAL_SAMPLE_EVERY_N = 10  # Sample every Nth grid cell
YEARS_PER_BATCH = 5          # Years per output file
START_YEAR = 1950            # Default start
END_YEAR = 2024              # Default end
MERGE_VARIABLES_PER_BATCH = True  # One file per time batch
```

---

**Input:** `.nc` files with climate measurements  
**Output:** `.ttl` files with semantic climate knowledge graphs
