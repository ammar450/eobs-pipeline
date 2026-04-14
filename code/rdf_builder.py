"""
RDF Builder module for creating complete SOSA observation patterns.
Handles all RDF graph construction with W3C-standard ontologies.
"""

from rdflib import Graph, URIRef, Literal, BNode
from rdflib.namespace import RDF, RDFS, XSD
from datetime import datetime
from typing import Dict, Any, Optional
import logging

from config import (
    SOSA, SSN, GEO, GEO1, GEOSPARQL, DCTERMS, QUDT, QUDT_UNIT,
    PROV, SCHEMA, CF, ONTOLOGY, PROPERTY, OBOE,
    NAMESPACE_BINDINGS, VARIABLE_MAPPINGS, EOBS_METADATA,
    get_sensor_uri, get_observation_uri, get_location_uri,
    get_dataset_uri, get_property_uri
)

logger = logging.getLogger(__name__)


class RDFBuilder:
    """Builds RDF graphs with complete SOSA observation patterns."""
    
    def __init__(self):
        """Initialize RDF graph with namespace bindings."""
        self.graph = Graph()
        self._bind_namespaces()
        self.sensors_created = set()
        self.locations_created = set()
        self.properties_created = set()
        self.datasets_created = set()
        # Make DCTERMS accessible for batch linking
        self.DCTERMS = DCTERMS
        
    def _bind_namespaces(self):
        """Bind all W3C-standard namespaces to the graph."""
        for prefix, namespace in NAMESPACE_BINDINGS.items():
            self.graph.bind(prefix, namespace)
    
    def create_dataset(self, variable_code: str, year_start: int, year_end: int) -> URIRef:
        """
        Create dataset resource (observation collection).
        
        Args:
            variable_code: E-OBS variable code (e.g., 'tg', 'rr')
            year_start: Starting year of the batch
            year_end: Ending year of the batch
            
        Returns:
            URIRef: Dataset URI
        """
        dataset_uri = URIRef(get_dataset_uri(variable_code, year_start, year_end))
        
        if dataset_uri in self.datasets_created:
            return dataset_uri
        
        # Type declaration - use OBOE ObservationCollection
        self.graph.add((dataset_uri, RDF.type, OBOE.ObservationCollection))
        
        self.datasets_created.add(dataset_uri)
        logger.info(f"Created dataset: {dataset_uri}")
        
        return dataset_uri
    
    def create_sensor(self, variable_code: str) -> URIRef:
        """
        Get sensor URI (no creation needed - just return URI reference).
        
        Args:
            variable_code: E-OBS variable code
            
        Returns:
            URIRef: Sensor URI
        """
        sensor_uri = URIRef(get_sensor_uri(variable_code))
        self.sensors_created.add(sensor_uri)
        return sensor_uri
    
    def create_observable_property(self, variable_code: str) -> URIRef:
        """
        Get observable property URI (CF standard name - no creation needed).
        
        Args:
            variable_code: E-OBS variable code
            
        Returns:
            URIRef: Observable property URI (CF standard name)
        """
        var_info = VARIABLE_MAPPINGS[variable_code]
        cf_uri = URIRef(f"{CF}{var_info['cf_standard_name']}")
        self.properties_created.add(cf_uri)
        return cf_uri
    
    def create_location(self, lat: float, lon: float) -> URIRef:
        """
        Get spatial location URI (no triples added - just tracking).
        
        Args:
            lat: Latitude in decimal degrees
            lon: Longitude in decimal degrees
            
        Returns:
            URIRef: Location URI
        """
        location_uri = URIRef(get_location_uri(lat, lon))
        self.locations_created.add(location_uri)
        logger.debug(f"Location referenced: {location_uri}")
        return location_uri
    
    def create_observation(
        self,
        variable_code: str,
        lat: float,
        lon: float,
        timestamp: str,
        value: float,
        dataset_uri: URIRef
    ) -> URIRef:
        """
        Create simplified SOSA observation matching target pattern.
        
        Args:
            variable_code: E-OBS variable code
            lat: Latitude in decimal degrees
            lon: Longitude in decimal degrees
            timestamp: ISO 8601 timestamp string
            value: Measured value
            dataset_uri: Parent dataset URI
            
        Returns:
            URIRef: Observation URI
        """
        obs_uri = URIRef(get_observation_uri(variable_code, lat, lon, timestamp))
        
        # Type declaration
        self.graph.add((obs_uri, RDF.type, SOSA.Observation))
        
        # hasFeatureOfInterest (spatial location with geo1: prefix)
        location_uri = self.create_location(lat, lon)
        self.graph.add((obs_uri, SOSA.hasFeatureOfInterest, location_uri))
        
        # hasResult (using QUDT for proper unit representation)
        result_node = BNode()
        self.graph.add((obs_uri, SOSA.hasResult, result_node))
        self.graph.add((result_node, RDF.type, QUDT.QuantityValue))
        self.graph.add((result_node, QUDT.numericValue, 
                       Literal(value, datatype=XSD.double)))
        
        var_info = VARIABLE_MAPPINGS[variable_code]
        self.graph.add((result_node, QUDT.unit, var_info['unit']))
        
        # madeBySensor (using sosa: prefix)
        sensor_uri = self.create_sensor(variable_code)
        self.graph.add((obs_uri, SOSA.madeBySensor, sensor_uri))
        
        # observedProperty (CF standard name as direct URIRef)
        property_uri = self.create_observable_property(variable_code)
        self.graph.add((obs_uri, SOSA.observedProperty, property_uri))
        
        # resultTime
        self.graph.add((obs_uri, SOSA.resultTime, 
                       Literal(timestamp, datatype=XSD.dateTime)))
        
        # Link dataset to observation via sosa:hasMember
        self.graph.add((dataset_uri, SOSA.hasMember, obs_uri))
        
        return obs_uri
    
    def validate_observation(self, obs_uri: URIRef) -> bool:
        """
        Validate that an observation has all mandatory SOSA properties.
        
        Args:
            obs_uri: Observation URI to validate
            
        Returns:
            bool: True if valid, False otherwise
        """
        required_properties = [
            SOSA.madeBySensor,
            SOSA.hasResult,
            SOSA.resultTime,
            SOSA.hasFeatureOfInterest,
            SOSA.observedProperty
        ]
        
        for prop in required_properties:
            if not list(self.graph.triples((obs_uri, prop, None))):
                logger.error(f"Observation {obs_uri} missing required property {prop}")
                return False
        
        return True
    
    def validate_graph(self) -> bool:
        """
        Validate entire graph for required patterns and no example.org URIs.
        
        Returns:
            bool: True if valid, False otherwise
        """
        logger.info("Validating RDF graph...")
        
        # Check for example.org URIs (FORBIDDEN)
        for s, p, o in self.graph:
            for node in [s, p, o]:
                if isinstance(node, URIRef) and "example.org" in str(node):
                    logger.error(f"FORBIDDEN: example.org URI found: {node}")
                    return False
        
        # Validate all observations
        observations = list(self.graph.subjects(RDF.type, SOSA.Observation))
        logger.info(f"Validating {len(observations)} observations...")
        
        for obs in observations:
            if not self.validate_observation(obs):
                return False
        
        # Check dataset-observation links
        datasets = list(self.graph.subjects(RDF.type, OBOE.ObservationCollection))
        for dataset in datasets:
            has_members = list(self.graph.objects(dataset, SOSA.hasMember))
            if not has_members:
                logger.error(f"Dataset {dataset} has no sosa:hasMember links")
                return False
        
        logger.info("✅ Graph validation passed!")
        return True
    
    def get_statistics(self) -> Dict[str, int]:
        """Get statistics about the current graph."""
        return {
            "total_triples": len(self.graph),
            "observations": len(list(self.graph.subjects(RDF.type, SOSA.Observation))),
            "sensors": len(self.sensors_created),
            "locations": len(self.locations_created),
            "properties": len(self.properties_created),
            "datasets": len(self.datasets_created)
        }
    
    def serialize(self, output_path: str, format: str = "turtle") -> bool:
        """
        Serialize RDF graph to file.
        
        Args:
            output_path: Output file path
            format: RDF serialization format
            
        Returns:
            bool: True if successful
        """
        try:
            logger.info(f"Serializing graph to {output_path}...")
            self.graph.serialize(destination=output_path, format=format, encoding="utf-8")
            logger.info(f"✅ Successfully wrote {output_path}")
            return True
        except Exception as e:
            logger.error(f"Failed to serialize graph: {e}")
            return False
