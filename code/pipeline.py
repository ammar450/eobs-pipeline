"""
Main pipeline for converting E-OBS NetCDF files to RDF/Turtle knowledge graphs.
Orchestrates reading, transformation, validation, and serialization.
"""

import logging
import sys
from pathlib import Path
from datetime import datetime
from typing import List, Optional, Tuple
import time
import subprocess

from config import (
    NETCDF_FILES, VARIABLE_MAPPINGS, OUTPUT_DIR,
    YEARS_PER_BATCH, START_YEAR, END_YEAR,
    SPATIAL_SAMPLE_EVERY_N, VALIDATION_ENABLED,
    VALIDATE_WITH_RAPPER, LOG_LEVEL, LOG_FORMAT,
    VARIABLES, VARIABLE_START_YEARS
)
from netcdf_reader import NetCDFReader
from rdf_builder import RDFBuilder

# Configure logging
logging.basicConfig(
    level=getattr(logging, LOG_LEVEL),
    format=LOG_FORMAT,
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler(OUTPUT_DIR / 'pipeline.log')
    ]
)
logger = logging.getLogger(__name__)


class ClimateKGPipeline:
    """Main pipeline for NetCDF to RDF/Turtle conversion with merged batches."""
    
    def __init__(
        self,
        variables: Optional[List[str]] = None,
        start_year: int = START_YEAR,
        end_year: int = END_YEAR,
        batch_years: int = YEARS_PER_BATCH,
        spatial_sample: int = SPATIAL_SAMPLE_EVERY_N
    ):
        """
        Initialize the pipeline.
        
        Args:
            variables: List of variable codes to process (None = all)
            start_year: Starting year for processing
            end_year: Ending year for processing
            batch_years: Number of years per TTL file
            spatial_sample: Sample every Nth grid cell
        """
        self.variables = variables or VARIABLES
        self.start_year = start_year
        self.end_year = end_year
        self.batch_years = batch_years
        self.spatial_sample = spatial_sample
        
        logger.info("=" * 80)
        logger.info("Climate Knowledge Graph Pipeline Initialized (MERGED MODE)")
        logger.info("=" * 80)
        logger.info(f"Variables: {', '.join(self.variables)}")
        logger.info(f"Year range: {start_year}-{end_year}")
        logger.info(f"Batch size: {batch_years} years (all variables merged per batch)")
        logger.info(f"Spatial sampling: every {spatial_sample} grid cells")
        logger.info("=" * 80)
    
    def generate_year_batches(self) -> List[Tuple[int, int]]:
        """
        Generate year range batches.
        
        Returns:
            List of (start_year, end_year) tuples
        """
        batches = []
        current_year = self.start_year
        
        while current_year <= self.end_year:
            batch_end = min(current_year + self.batch_years - 1, self.end_year)
            batches.append((current_year, batch_end))
            current_year = batch_end + 1
        
        logger.info(f"Generated {len(batches)} year batches: {batches}")
        return batches
    
    def generate_output_filename(
        self,
        year_start: int,
        year_end: int
    ) -> str:
        """
        Generate timestamped output filename for merged batch.
        
        Args:
            year_start: Starting year
            year_end: Ending year
            
        Returns:
            str: Output filename
        """
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"eobs_climate_kg_{year_start}_{year_end}_{timestamp}.ttl"
        return filename
    
    def process_merged_batch(
        self,
        year_start: int,
        year_end: int
    ) -> Optional[Path]:
        """
        Process a time batch with all available variables merged into one TTL file.
        
        Args:
            year_start: Starting year
            year_end: Ending year
            
        Returns:
            Path: Output file path if successful, None otherwise
        """
        logger.info("=" * 80)
        logger.info(f"Processing MERGED BATCH ({year_start}-{year_end})")
        logger.info("=" * 80)
        
        start_time = time.time()
        
        try:
            # Initialize single RDF builder for the entire batch
            rdf_builder = RDFBuilder()
            
            total_observations = 0
            variables_processed = []
            variables_skipped = []
            
            # Process each variable for this time period
            for variable_code in self.variables:
                logger.info(f"  Processing variable: {variable_code.upper()}")
                
                # Check if variable has data for this period
                var_start_year = VARIABLE_START_YEARS.get(variable_code, START_YEAR)
                if year_end < var_start_year:
                    logger.warning(f"    ⚠️  Skipping {variable_code} - no data before {var_start_year}")
                    variables_skipped.append(variable_code)
                    continue
                
                # Adjust start year if needed
                actual_start = max(year_start, var_start_year)
                
                try:
                    # Create dataset for this variable
                    var_dataset_uri = rdf_builder.create_dataset(
                        variable_code,
                        actual_start,
                        year_end
                    )
                    
                    # Open NetCDF reader
                    with NetCDFReader(variable_code) as reader:
                        # Extract observations
                        observation_count = 0
                        
                        for obs_data in reader.extract_observations(
                            year_start=actual_start,
                            year_end=year_end,
                            spatial_sample=self.spatial_sample
                        ):
                            # Create RDF observation
                            rdf_builder.create_observation(
                                variable_code=variable_code,
                                lat=obs_data['lat'],
                                lon=obs_data['lon'],
                                timestamp=obs_data['timestamp'],
                                value=obs_data['value'],
                                dataset_uri=var_dataset_uri
                            )
                            
                            observation_count += 1
                            total_observations += 1
                            
                            # Progress logging
                            if total_observations % 10000 == 0:
                                logger.info(f"    Processed {total_observations:,} total observations...")
                        
                        if observation_count > 0:
                            logger.info(f"    ✅ Added {observation_count:,} observations for {variable_code}")
                            variables_processed.append(variable_code)
                        else:
                            logger.warning(f"    ⚠️  No observations for {variable_code} in this period")
                            variables_skipped.append(variable_code)
                
                except FileNotFoundError as e:
                    logger.warning(f"    ⚠️  NetCDF file not found for {variable_code}: {e}")
                    variables_skipped.append(variable_code)
                    continue
                except Exception as e:
                    logger.error(f"    ❌ Error processing {variable_code}: {e}")
                    variables_skipped.append(variable_code)
                    continue
            
            # Summary
            logger.info(f"✅ Total observations in batch: {total_observations:,}")
            logger.info(f"✅ Variables processed: {', '.join(variables_processed) if variables_processed else 'None'}")
            if variables_skipped:
                logger.info(f"⚠️  Variables skipped: {', '.join(variables_skipped)}")
            
            # Skip if no observations at all
            if total_observations == 0:
                logger.warning(f"⚠️  No observations for batch ({year_start}-{year_end}) - skipping")
                return None
            
            # Get statistics
            stats = rdf_builder.get_statistics()
            logger.info(f"Graph statistics: {stats}")
            
            # Validate graph
            if VALIDATION_ENABLED:
                logger.info("Validating merged RDF graph...")
                if not rdf_builder.validate_graph():
                    logger.error("❌ Graph validation failed!")
                    return None
            
            # Generate output filename
            output_filename = self.generate_output_filename(
                year_start,
                year_end
            )
            output_path = OUTPUT_DIR / output_filename
            
            # Serialize to Turtle
            logger.info(f"Serializing merged batch to {output_filename}...")
            if not rdf_builder.serialize(str(output_path)):
                logger.error("❌ Serialization failed!")
                return None
            
            # Get file size
            file_size_mb = output_path.stat().st_size / (1024 * 1024)
            logger.info(f"Output file size: {file_size_mb:.2f} MB")
            
            # Validate with rapper if enabled
            if VALIDATE_WITH_RAPPER:
                if not self.validate_with_rapper(output_path):
                    logger.warning("⚠️  Rapper validation failed (continuing anyway)")
            
            # Calculate performance metrics
            elapsed_time = time.time() - start_time
            obs_per_second = total_observations / elapsed_time if elapsed_time > 0 else 0
            
            logger.info("=" * 80)
            logger.info(f"✅ SUCCESS: MERGED BATCH ({year_start}-{year_end})")
            logger.info(f"Variables included: {', '.join(variables_processed)}")
            logger.info(f"Processing time: {elapsed_time:.2f} seconds")
            logger.info(f"Performance: {obs_per_second:.0f} observations/second")
            logger.info(f"Output: {output_path}")
            logger.info("=" * 80)
            
            return output_path
        
        except Exception as e:
            logger.error(f"❌ FAILED: MERGED BATCH ({year_start}-{year_end})")
            logger.error(f"Error: {e}", exc_info=True)
            return None
    
    def process_variable_batch(
        self,
        variable_code: str,
        year_start: int,
        year_end: int
    ) -> Optional[Path]:
        """
        Process a single variable for a specific year range.
        
        Args:
            variable_code: E-OBS variable code
            year_start: Starting year
            year_end: Ending year
            
        Returns:
            Path: Output file path if successful, None otherwise
        """
        logger.info("=" * 80)
        logger.info(f"Processing {variable_code.upper()} ({year_start}-{year_end})")
        logger.info("=" * 80)
        
        start_time = time.time()
        
        try:
            # Initialize RDF builder
            rdf_builder = RDFBuilder()
            
            # Create dataset resource
            dataset_uri = rdf_builder.create_dataset(
                variable_code,
                year_start,
                year_end
            )
            
            # Open NetCDF reader
            with NetCDFReader(variable_code) as reader:
                # Extract observations
                observation_count = 0
                
                logger.info("Extracting observations from NetCDF...")
                
                for obs_data in reader.extract_observations(
                    year_start=year_start,
                    year_end=year_end,
                    spatial_sample=self.spatial_sample
                ):
                    # Create RDF observation
                    rdf_builder.create_observation(
                        variable_code=variable_code,
                        lat=obs_data['lat'],
                        lon=obs_data['lon'],
                        timestamp=obs_data['timestamp'],
                        value=obs_data['value'],
                        dataset_uri=dataset_uri
                    )
                    
                    observation_count += 1
                    
                    # Progress logging
                    if observation_count % 10000 == 0:
                        logger.info(f"Processed {observation_count:,} observations...")
                
                logger.info(f"✅ Created {observation_count:,} observations")
            
            # Skip if no observations (data not available for this period)
            if observation_count == 0:
                logger.warning(f"⚠️  No observations for {variable_code} ({year_start}-{year_end}) - skipping (data may not be available for this period)")
                return None
            
            # Get statistics
            stats = rdf_builder.get_statistics()
            logger.info(f"Graph statistics: {stats}")
            
            # Validate graph
            if VALIDATION_ENABLED:
                logger.info("Validating RDF graph...")
                if not rdf_builder.validate_graph():
                    logger.error("❌ Graph validation failed!")
                    return None
            
            # Generate output filename
            output_filename = self.generate_output_filename(
                variable_code,
                year_start,
                year_end
            )
            output_path = OUTPUT_DIR / output_filename
            
            # Serialize to Turtle
            logger.info(f"Serializing to {output_filename}...")
            if not rdf_builder.serialize(str(output_path)):
                logger.error("❌ Serialization failed!")
                return None
            
            # Get file size
            file_size_mb = output_path.stat().st_size / (1024 * 1024)
            logger.info(f"Output file size: {file_size_mb:.2f} MB")
            
            # Validate with rapper if enabled
            if VALIDATE_WITH_RAPPER:
                if not self.validate_with_rapper(output_path):
                    logger.warning("⚠️  Rapper validation failed (continuing anyway)")
            
            # Calculate performance metrics
            elapsed_time = time.time() - start_time
            obs_per_second = observation_count / elapsed_time if elapsed_time > 0 else 0
            
            logger.info("=" * 80)
            logger.info(f"✅ SUCCESS: {variable_code.upper()} ({year_start}-{year_end})")
            logger.info(f"Processing time: {elapsed_time:.2f} seconds")
            logger.info(f"Performance: {obs_per_second:.0f} observations/second")
            logger.info(f"Output: {output_path}")
            logger.info("=" * 80)
            
            return output_path
        
        except Exception as e:
            logger.error(f"❌ FAILED: {variable_code.upper()} ({year_start}-{year_end})")
            logger.error(f"Error: {e}", exc_info=True)
            return None
    
    def validate_with_rapper(self, file_path: Path) -> bool:
        """
        Validate TTL file with rapper CLI tool.
        
        Args:
            file_path: Path to TTL file
            
        Returns:
            bool: True if valid
        """
        try:
            logger.info(f"Validating with rapper: {file_path}")
            result = subprocess.run(
                ['rapper', '-i', 'turtle', str(file_path)],
                capture_output=True,
                text=True,
                timeout=300
            )
            
            if result.returncode == 0:
                logger.info("✅ Rapper validation passed")
                return True
            else:
                logger.error(f"❌ Rapper validation failed: {result.stderr}")
                return False
        
        except FileNotFoundError:
            logger.warning("Rapper not found - skipping validation")
            return True
        except subprocess.TimeoutExpired:
            logger.warning("Rapper validation timed out")
            return False
        except Exception as e:
            logger.warning(f"Rapper validation error: {e}")
            return False
    
    def run(self) -> List[Path]:
        """
        Run the complete pipeline with merged batches.
        
        Returns:
            List[Path]: List of generated TTL files
        """
        pipeline_start = time.time()
        
        logger.info("🚀 Starting Climate Knowledge Graph Pipeline (MERGED MODE)")
        logger.info("=" * 80)
        
        # Generate year batches
        year_batches = self.generate_year_batches()
        
        output_files = []
        total_batches = len(year_batches)
        completed = 0
        failed = 0
        
        # Process each time batch (all variables merged)
        for year_start, year_end in year_batches:
            output_path = self.process_merged_batch(
                year_start,
                year_end
            )
            
            if output_path:
                output_files.append(output_path)
                completed += 1
            else:
                failed += 1
            
            logger.info(f"Progress: {completed + failed}/{total_batches} batches "
                      f"({completed} successful, {failed} failed)")
        
        # Final summary
        pipeline_time = time.time() - pipeline_start
        
        logger.info("=" * 80)
        logger.info("🎉 PIPELINE COMPLETE (MERGED MODE)")
        logger.info("=" * 80)
        logger.info(f"Total time batches: {total_batches}")
        logger.info(f"Successful: {completed}")
        logger.info(f"Failed: {failed}")
        logger.info(f"Total time: {pipeline_time / 60:.2f} minutes")
        logger.info(f"Output files: {len(output_files)}")
        logger.info("=" * 80)
        
        if output_files:
            logger.info("Generated files:")
            for file_path in output_files:
                size_mb = file_path.stat().st_size / (1024 * 1024)
                logger.info(f"  - {file_path.name} ({size_mb:.2f} MB)")
        
        return output_files
    
    def run_test(self, test_year: int = 2020) -> Optional[Path]:
        """
        Run a test with a single year of data (all variables merged).
        
        Args:
            test_year: Year to test
            
        Returns:
            Path: Output file path if successful
        """
        logger.info("=" * 80)
        logger.info(f"🧪 RUNNING TEST: MERGED BATCH for year {test_year}")
        logger.info("=" * 80)
        
        return self.process_merged_batch(test_year, test_year)


def main():
    """Main entry point for the pipeline."""
    import argparse
    
    parser = argparse.ArgumentParser(
        description="Convert E-OBS NetCDF files to RDF/Turtle knowledge graphs"
    )
    parser.add_argument(
        '--variables',
        nargs='+',
        choices=list(NETCDF_FILES.keys()),
        help='Variables to process (default: all)'
    )
    parser.add_argument(
        '--start-year',
        type=int,
        default=START_YEAR,
        help=f'Starting year (default: {START_YEAR})'
    )
    parser.add_argument(
        '--end-year',
        type=int,
        default=END_YEAR,
        help=f'Ending year (default: {END_YEAR})'
    )
    parser.add_argument(
        '--batch-years',
        type=int,
        default=YEARS_PER_BATCH,
        help=f'Years per batch (default: {YEARS_PER_BATCH})'
    )
    parser.add_argument(
        '--spatial-sample',
        type=int,
        default=SPATIAL_SAMPLE_EVERY_N,
        help=f'Sample every Nth grid cell (default: {SPATIAL_SAMPLE_EVERY_N})'
    )
    parser.add_argument(
        '--test',
        action='store_true',
        help='Run test mode (single year)'
    )
    parser.add_argument(
        '--test-year',
        type=int,
        default=2020,
        help='Year for test mode (default: 2020)'
    )

    
    args = parser.parse_args()
    
    # Create pipeline
    pipeline = ClimateKGPipeline(
        variables=args.variables,
        start_year=args.start_year,
        end_year=args.end_year,
        batch_years=args.batch_years,
        spatial_sample=args.spatial_sample
    )
    
    # Run test or full pipeline
    if args.test:
        output_file = pipeline.run_test(args.test_year)
        if output_file:
            logger.info(f"✅ Test completed successfully: {output_file}")
            sys.exit(0)
        else:
            logger.error("❌ Test failed")
            sys.exit(1)
    else:
        output_files = pipeline.run()
        if output_files:
            logger.info(f"✅ Pipeline completed successfully")
            sys.exit(0)
        else:
            logger.error("❌ Pipeline failed - no output files generated")
            sys.exit(1)


if __name__ == "__main__":
    main()
