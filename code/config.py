"""
Configuration module for E-OBS NetCDF to RDF/Turtle conversion pipeline.
Defines namespaces, URI patterns, file paths, and processing parameters.
"""

from pathlib import Path
from rdflib import Namespace, URIRef

# ============================================================================
# BASE PATHS
# ============================================================================
BASE_DIR = Path(__file__).parent.parent
NETCDF_DIR = BASE_DIR / "netcdf"
OUTPUT_DIR = BASE_DIR / "ttl"
OUTPUT_DIR.mkdir(exist_ok=True)

# ============================================================================
# W3C STANDARD ONTOLOGY NAMESPACES
# ============================================================================
# Core RDF/RDFS/OWL
RDF = Namespace("http://www.w3.org/1999/02/22-rdf-syntax-ns#")
RDFS = Namespace("http://www.w3.org/2000/01/rdf-schema#")
XSD = Namespace("http://www.w3.org/2001/XMLSchema#")
OWL = Namespace("http://www.w3.org/2002/07/owl#")

# SOSA/SSN - Sensor/Observation/Actuation
SOSA = Namespace("http://www.w3.org/ns/sosa/")
SSN = Namespace("http://www.w3.org/ns/ssn/")

# Spatial and Temporal
GEO = Namespace("http://www.w3.org/2003/01/geo/wgs84_pos#")
GEO1 = Namespace("http://www.w3.org/2003/01/geo/wgs84_pos#")
GEOSPARQL = Namespace("http://www.opengis.net/ont/geosparql#")
TIME = Namespace("http://www.w3.org/2006/time#")

# Dublin Core Metadata
DCTERMS = Namespace("http://purl.org/dc/terms/")
DC = Namespace("http://purl.org/dc/elements/1.1/")

# QUDT - Quantities, Units, Dimensions and Types
QUDT = Namespace("http://qudt.org/schema/qudt/")
QUDT_UNIT = Namespace("http://qudt.org/vocab/unit/")

# PROV - Provenance
PROV = Namespace("http://www.w3.org/ns/prov#")

# Schema.org
SCHEMA = Namespace("http://schema.org/")

# CF Standard Names (Climate and Forecast)
CF = Namespace("http://vocab.nerc.ac.uk/standard_name/")

# OBOE - Extensible Observation Ontology
OBOE = Namespace("http://ecoinformatics.org/oboe/oboe.1.2/oboe-core.owl#")

# ============================================================================
# PRODUCTION URI PATTERNS (climate-kg.org domain)
# ============================================================================
BASE_URI = "http://climate-kg.org/"
RESOURCE = Namespace(f"{BASE_URI}resource/")
ONTOLOGY = Namespace(f"{BASE_URI}ontology/")
SENSOR = Namespace(f"{BASE_URI}sensor/")
OBSERVATION = Namespace(f"{BASE_URI}observation/")
LOCATION = Namespace(f"{BASE_URI}location/")
DATASET = Namespace(f"{BASE_URI}dataset/")
PROPERTY = Namespace(f"{BASE_URI}property/")

# ============================================================================
# E-OBS VARIABLE MAPPINGS
# ============================================================================
VARIABLE_MAPPINGS = {
    "fg": {
        "name": "mean_wind_speed",
        "label": "Mean Wind Speed",
        "description": "Daily mean wind speed",
        "cf_standard_name": "wind_speed",
        "unit": URIRef(f"{QUDT_UNIT}M-PER-SEC"),
        "unit_label": "m/s",
        "sensor_type": "Anemometer",
        "phenomenon": "WindSpeed"
    },
    "hu": {
        "name": "relative_humidity",
        "label": "Relative Humidity",
        "description": "Daily mean relative humidity",
        "cf_standard_name": "relative_humidity",
        "unit": URIRef(f"{QUDT_UNIT}PERCENT"),
        "unit_label": "%",
        "sensor_type": "Hygrometer",
        "phenomenon": "RelativeHumidity"
    },
    "qq": {
        "name": "global_radiation",
        "label": "Global Radiation",
        "description": "Daily mean global radiation",
        "cf_standard_name": "surface_downwelling_shortwave_flux_in_air",
        "unit": URIRef(f"{QUDT_UNIT}W-PER-M2"),
        "unit_label": "W/m²",
        "sensor_type": "Pyranometer",
        "phenomenon": "SolarRadiation"
    },
    "rr": {
        "name": "precipitation_amount",
        "label": "Precipitation Amount",
        "description": "Daily precipitation amount",
        "cf_standard_name": "precipitation_amount",
        "unit": URIRef(f"{QUDT_UNIT}MilliM"),
        "unit_label": "mm",
        "sensor_type": "Rain Gauge",
        "phenomenon": "Precipitation"
    },
    "tg": {
        "name": "mean_temperature",
        "label": "Mean Temperature",
        "description": "Daily mean temperature",
        "cf_standard_name": "air_temperature",
        "unit": URIRef(f"{QUDT_UNIT}DEG_C"),
        "unit_label": "°C",
        "sensor_type": "Thermometer",
        "phenomenon": "AirTemperature"
    },
    "tn": {
        "name": "minimum_temperature",
        "label": "Minimum Temperature",
        "description": "Daily minimum temperature",
        "cf_standard_name": "air_temperature",
        "unit": URIRef(f"{QUDT_UNIT}DEG_C"),
        "unit_label": "°C",
        "sensor_type": "Thermometer",
        "phenomenon": "MinimumAirTemperature"
    },
    "tx": {
        "name": "maximum_temperature",
        "label": "Maximum Temperature",
        "description": "Daily maximum temperature",
        "cf_standard_name": "air_temperature",
        "unit": URIRef(f"{QUDT_UNIT}DEG_C"),
        "unit_label": "°C",
        "sensor_type": "Thermometer",
        "phenomenon": "MaximumAirTemperature"
    }
}

# ============================================================================
# NETCDF FILE PATTERNS
# ============================================================================
NETCDF_FILES = {
    "fg": "fg_ens_mean_0.25deg_reg_v31.0e.nc",
    "hu": "hu_ens_mean_0.25deg_reg_v31.0e.nc",
    "qq": "qq_ens_mean_0.25deg_reg_v31.0e.nc",
    "rr": "rr_ens_mean_0.25deg_reg_v31.0e (1).nc",
    "tg": "tg_ens_mean_0.25deg_reg_v31.0e.nc",
    "tn": "tn_ens_mean_0.25deg_reg_v31.0e.nc",
    "tx": "tx_ens_mean_0.25deg_reg_v31.0e.nc"
}

# ============================================================================
# PROCESSING PARAMETERS
# ============================================================================
# Time batching configuration
YEARS_PER_BATCH = 5  # Process N years per TTL file (all variables merged)
START_YEAR = 1950
END_YEAR = 2024

# List of all variables to process
VARIABLES = ["fg", "hu", "qq", "rr", "tg", "tn", "tx"]

# Variable-specific start years (based on data availability)
# Pipeline will dynamically skip variables with no data for a given batch
VARIABLE_START_YEARS = {
    'fg': 1980,  # Wind speed starts from 1980
    'hu': 1950,
    'qq': 1950,
    'rr': 1950,
    'tg': 1950,
    'tn': 1950,
    'tx': 1950
}

# Spatial sampling configuration
SPATIAL_SAMPLE_EVERY_N = 10  # Sample every Nth grid cell (1 = all cells)

# Temporal range (None = all available data)
TEMPORAL_START_DATE = None  # e.g., "1950-01-01"
TEMPORAL_END_DATE = None    # e.g., "2024-12-31"

# Performance tuning
CHUNK_SIZE = 10000  # Number of observations per processing chunk
MAX_MEMORY_GB = 8   # Maximum memory usage

# Merge mode: One TTL file per time batch with all variables
MERGE_VARIABLES_PER_BATCH = True

# ============================================================================
# VALIDATION PARAMETERS
# ============================================================================
VALIDATION_ENABLED = True
VALIDATE_WITH_RAPPER = True  # Requires rapper CLI tool
REQUIRED_PROPERTIES = [
    SOSA.madeBySensor,
    SOSA.hasResult,
    SOSA.resultTime,
    SOSA.hasFeatureOfInterest,
    SOSA.observedProperty
]

# ============================================================================
# E-OBS DATASET METADATA
# ============================================================================
EOBS_METADATA = {
    "title": "E-OBS Ensemble Mean Climate Data v31.0e",
    "description": "High-resolution gridded climate data for Europe from the E-OBS dataset",
    "version": "31.0e",
    "resolution": "0.25 degrees",
    "temporal_coverage": "1950-2024",
    "spatial_coverage": "Europe",
    "source": "https://www.ecad.eu/download/ensembles/download.php",
    "citation": "Cornes et al. (2018), An Ensemble Version of the E-OBS Temperature and Precipitation Data Sets, J. Geophys. Res. Atmos., 123.",
    "license": "https://www.ecad.eu/download/ensembles/download.php#datafiles",
    "publisher": "European Climate Assessment & Dataset (ECA&D)"
}

# ============================================================================
# RDF SERIALIZATION OPTIONS
# ============================================================================
RDF_FORMAT = "turtle"
RDF_ENCODING = "utf-8"
PRETTY_PRINT = True

# ============================================================================
# LOGGING CONFIGURATION
# ============================================================================
LOG_LEVEL = "INFO"
LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"

# ============================================================================
# URI GENERATION HELPERS
# ============================================================================
def get_sensor_uri(variable_code: str) -> str:
    """Generate URI for sensor."""
    return f"{SOSA}{variable_code}_sensor"

def get_observation_uri(variable_code: str, lat: float, lon: float, timestamp: str) -> str:
    """Generate unique URI for observation."""
    # Clean timestamp for URI (remove special characters)
    ts_clean = timestamp.replace("-", "").replace(":", "").replace(" ", "T")
    lat_str = f"{lat:.2f}".replace(".", "p").replace("-", "m")
    lon_str = f"{lon:.2f}".replace(".", "p").replace("-", "m")
    return f"{OBSERVATION}{variable_code}_{lat_str}_{lon_str}_{ts_clean}"

def get_location_uri(lat: float, lon: float) -> str:
    """Generate URI for grid cell location."""
    lat_str = f"{lat:.2f}".replace(".", "p").replace("-", "m")
    lon_str = f"{lon:.2f}".replace(".", "p").replace("-", "m")
    return f"{GEO1}grid_{lat_str}_{lon_str}"

def get_dataset_uri(variable_code: str, year_start: int, year_end: int) -> str:
    """Generate URI for dataset batch."""
    return f"{OBSERVATION}eobs_{variable_code}_{year_start}_{year_end}"

def get_property_uri(cf_standard_name: str) -> str:
    """Generate URI for observable property."""
    return f"{PROPERTY}{cf_standard_name}"

# ============================================================================
# NAMESPACE BINDINGS FOR RDF SERIALIZATION
# ============================================================================
NAMESPACE_BINDINGS = {
    "cf": CF,
    "geo1": GEO1,
    "observation": OBSERVATION,
    "qudt": QUDT,
    "sosa": SOSA,
    "unit": QUDT_UNIT,
    "xsd": XSD,
    "oboe": OBOE
}
