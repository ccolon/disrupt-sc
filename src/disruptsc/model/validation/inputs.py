"""
Input file validation module for DisruptSC model.

This module provides comprehensive validation of input files to catch errors
before model initialization and provide clear diagnostic information.
"""

import logging
import pandas as pd
import geopandas as gpd
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Union
import yaml
import numpy as np


class InputValidationError(Exception):
    """Custom exception for input validation errors."""
    pass

class InputValidator:
    """Validates all input files required for DisruptSC model execution."""
    
    def __init__(self, parameters):
        """Initialize validator with loaded parameters."""
        self.parameters = parameters
        self.scope = parameters.scope
        self.input_folder = Path(parameters.filepaths['sector_table']).parent.parent
        self.errors = []
        self.warnings = []
        
    def validate_all_inputs(self) -> Tuple[bool, List[str], List[str]]:
        """
        Validate all required input files.
        
        Returns:
            Tuple of (is_valid, errors, warnings)
        """
        logging.info(f"Starting input validation for scope: {self.scope}")
        
        # Core validation checks
        self._validate_file_existence()

        # Conditional validation based on model configuration
        if hasattr(self.parameters, 'with_transport') and not self.parameters.with_transport:
            logging.info("Skipping transport files validation (with_transport=False)")
        else:
            self._validate_transport_files()

        # Sector table only needed for MRIO mode
        if self.parameters.firm_data_type == "mrio":
            self._validate_sector_table()
        
        # Mode-specific validation
        if self.parameters.firm_data_type == "mrio":
            self._validate_mrio_inputs()
        elif self.parameters.firm_data_type == "transaction_based":
            self._validate_transaction_based_inputs()
        else:
            self.errors.append(f"Unknown firm_data_type: {self.parameters.firm_data_type}. "
                             f"Supported types: 'mrio', 'transaction_based'")
            
        # Parameter consistency checks
        self._validate_parameter_consistency()
        
        # Summary
        is_valid = len(self.errors) == 0
        if is_valid:
            logging.info("✓ All input validation checks passed")
        else:
            logging.error(f"✗ Input validation failed with {len(self.errors)} errors")
            
        return is_valid, self.errors, self.warnings
    
    def _validate_file_existence(self):
        """Check that all required files exist and are readable."""
        required_files = []

        # Only require sector_table and transport files for MRIO mode or when using transport
        if self.parameters.firm_data_type == "mrio":
            required_files.append('sector_table')

        if hasattr(self.parameters, 'with_transport') and self.parameters.with_transport:
            required_files.append('transport_parameters')

        for file_key in required_files:
            filepath = self.parameters.filepaths.get(file_key)
            if filepath and not Path(filepath).exists():
                self.errors.append(f"Required file not found: {filepath}")

        # Check transport mode files only if using transport
        if hasattr(self.parameters, 'with_transport') and self.parameters.with_transport:
            transport_folder = self.input_folder / "Transport"
            if transport_folder.exists():
                for mode in self.parameters.transport_modes:
                    edges_file = transport_folder / f"{mode}_edges.geojson"
                    if not edges_file.exists():
                        self.errors.append(f"Transport file not found: {edges_file}")
    
    def _validate_sector_table(self):
        """Validate the sector table structure and content."""
        filepath = self.parameters.filepaths.get('sector_table')
        if not filepath or not Path(filepath).exists():
            return
            
        try:
            df = pd.read_csv(filepath)
        except Exception as e:
            self.errors.append(f"Cannot read sector_table.csv: {e}")
            return
            
        # Required columns for all modes
        required_cols = ['sector', 'type', 'usd_per_ton']
        missing_cols = [col for col in required_cols if col not in df.columns]
        if missing_cols:
            self.errors.append(f"sector_table.csv missing required columns: {missing_cols}")
            
        # Mode-specific column requirements
        if self.parameters.firm_data_type == "mrio":
            if 'region_sector' not in df.columns and ('region' not in df.columns or 'sector' not in df.columns):
                self.errors.append("sector_table.csv for MRIO mode must have 'region_sector' column or both 'region' and 'sector' columns")
        
        # Data quality checks
        if 'output' in df.columns:
            if (df['output'] < 0).any():
                self.warnings.append("sector_table.csv contains negative output values")
            if (df['output'] == 0).sum() > len(df) * 0.5:
                self.warnings.append("sector_table.csv has many zero output values - check data quality")
                
        # Sector type validation
        if 'type' in df.columns:
            valid_types = ['agriculture', 'construction', 'mining', 'manufacturing', 'utility', 'transport', 'trade',
                           'service', 'services']
            invalid_types = df[~df['type'].isin(valid_types)]['type'].unique()
            if len(invalid_types) > 0:
                self.warnings.append(f"sector_table.csv contains non-standard sector types: {invalid_types}")
    
    def _validate_transport_files(self):
        """Validate transport network GeoJSON files."""
        transport_folder = self.input_folder / "Transport"
        
        for mode in self.parameters.transport_modes:
            edges_file = transport_folder / f"{mode}_edges.geojson"
            if not edges_file.exists():
                self.errors.append(f"{mode} specified in the parameter file but no corresponding geojson")
                continue
                
            try:
                gdf = gpd.read_file(edges_file)
            except Exception as e:
                self.errors.append(f"Cannot read {edges_file}: {e}")
                continue
                
            # Geometry validation
            if not all(gdf.geometry.geom_type == 'LineString'):
                self.errors.append(f"{edges_file}: All geometries must be LineString")
                
            # Required columns
            if 'km' not in gdf.columns:
                self.warnings.append(f"{edges_file}: Missing 'km' column - distances will be calculated")
                
            # Check for reasonable values
            if 'capacity' in gdf.columns:
                if (gdf['capacity'] < 0).any():
                    self.errors.append(f"{edges_file}: Negative capacity values found")
                    
            if 'km' in gdf.columns:
                if (gdf['km'] <= 0).any():
                    self.errors.append(f"{edges_file}: Non-positive distance values found")
                if (gdf['km'] > 10000).any():
                    self.warnings.append(f"{edges_file}: Very long edges (>10,000 km) found - check units")

        if len(self.parameters.transport_modes) > 2:
            if not (transport_folder / f"multimodal_edges.geojson").exists():
                self.errors.append("More than 2 transport modes defined, but no multimodal edges geojson")

    def _validate_mrio_inputs(self):
        """Validate inputs specific to MRIO mode."""
        # MRIO table is mandatory - throw error if missing
        mrio_file = self.parameters.filepaths.get('mrio')
        if not mrio_file:
            self.errors.append("MRIO mode requires 'mrio' filepath to be specified in parameters")
        elif not Path(mrio_file).exists():
            self.errors.append(f"Required MRIO table not found: {mrio_file}")
        else:
            self._validate_mrio_table(mrio_file)
            
        # Spatial files are mandatory - throw error if missing
        self._validate_spatial_files()
    
    def _validate_mrio_table(self, filepath):
        """Validate the multi-regional input-output table structure."""
        try:
            df = pd.read_csv(filepath, index_col=[0, 1], header=[0, 1])
        except Exception as e:
            self.errors.append(f"Cannot read MRIO table as multi-index: {e}")
            return

        # Check for completely empty data (critical error)
        if df.empty or df.isna().all().all():
            self.errors.append("MRIO table is empty or contains only NaN values")
            return
            
        # Check for negative values in intermediate flows (error, not warning)
        intermediate_cols = [col for col in df.columns if not any(
            keyword in str(col).lower() for keyword in ['final', 'export', 'capital', 'government']
        )]
        intermediate_rows = [row for row in df.index if not any(
            keyword in str(row).lower() for keyword in ['value', 'va', 'import', 'tax']
        )]
        if (len(intermediate_cols) == 0) or (len(intermediate_rows) == 0):
            self.errors.append("No matrix of intermediate flows detected in MRIO table")

        intermediate_df = df.loc[intermediate_rows, intermediate_cols]
        if intermediate_df.shape[0] != intermediate_df.shape[1]:
            self.errors.append(f"The intermediary part of the MRIO table must be square: "
                               f"{intermediate_df.shape[0]} rows vs {intermediate_df.shape[1]} columns")
        if (intermediate_df < 0).any().any():
            self.errors.append("MRIO table contains negative intermediate flows")
                
        # Check for extreme imbalance (critical error)
        try:
            row_sums = df.sum(axis=1)
            col_sums = df.sum(axis=0)
            unbalance_message = 'unbalanced (row sums ≠ column sums). Maybe taxes or value-added row is missing.'
            if not np.allclose(row_sums[intermediate_rows], col_sums[intermediate_cols], rtol=0.5):
                self.warnings.append("MRIO table is severely " + unbalance_message)
            elif not np.allclose(row_sums[intermediate_rows], col_sums[intermediate_cols], rtol=0.1):
                self.warnings.append("MRIO table appears " + unbalance_message)
        except Exception as e:
            self.errors.append(f"Cannot compute MRIO table balance: {e}")
    
    def _validate_spatial_files(self):
        """Validate new spatial file structure."""
        spatial_files = {
            'households_spatial': 'households.geojson',
            'countries_spatial': 'countries.geojson', 
            'firms_spatial': 'firms.geojson'
        }
        
        for file_key, filename in spatial_files.items():
            filepath = self.parameters.filepaths.get(file_key)
            if not filepath:
                self.errors.append(f"MRIO mode requires '{file_key}' filepath to be specified in parameters")
                continue
                
            if not Path(filepath).exists():
                self.errors.append(f"Required spatial file not found: {filepath}")
                continue
                
            self._validate_spatial_file(filepath, filename)
        
        # Warn about deprecated files
        deprecated_files = ['region_table']
        for deprecated_key in deprecated_files:
            if self.parameters.filepaths.get(deprecated_key):
                self.warnings.append(f"Deprecated parameter '{deprecated_key}' found. "
                                   f"Use 'households_spatial' and 'countries_spatial' instead.")
        
        # Check for deprecated Disag folder
        spatial_folder = Path(self.parameters.filepaths.get('households_spatial', '')).parent
        disag_folder = spatial_folder / "Disag"
        if disag_folder.exists():
            self.warnings.append("Deprecated Disag/ folder found. Use firms.geojson instead.")
    
    def _validate_spatial_file(self, filepath, filename):
        """Validate individual spatial file structure."""
        try:
            gdf = gpd.read_file(filepath)
        except Exception as e:
            self.errors.append(f"Cannot read {filename}: {e}")
            return
            
        # Check for empty data (critical error)
        if gdf.empty:
            self.errors.append(f"{filename} is empty")
            return
            
        # Check for required identifier column (critical error)
        if 'region' not in gdf.columns:
            self.errors.append(f"{filename} must have a 'region' column")
            
        # Check geometry type (critical error)
        if not all(gdf.geometry.geom_type == 'Point'):
            self.errors.append(f"{filename}: All geometries must be Points")
            
        # Check for missing geometries (critical error)
        if gdf.geometry.isna().any():
            self.errors.append(f"{filename} contains missing geometries")
            
        # Check for duplicate region identifiers (critical error)
        cols_to_checks = ['region', 'geometry']
        for col_to_checks in cols_to_checks:
            if gdf[col_to_checks].isna().any():
                self.errors.append(f"{filename} contains missing {col_to_checks} values")
        
        # Check subregion data quality if present (warning only)
        if 'subregion' in gdf.columns:
            if gdf['subregion'].isna().any():
                missing_count = gdf['subregion'].isna().sum()
                self.warnings.append(f"{filename} contains {missing_count} missing subregion values")

    def _validate_parameter_consistency(self):
        """Validate parameter consistency and reasonable values."""
        # Monetary units consistency
        valid_units = ['USD', 'kUSD', 'mUSD']
        if self.parameters.monetary_units_in_model not in valid_units:
            self.warnings.append(f"Unusual monetary unit in model: {self.parameters.monetary_units_in_model}")
            
        if self.parameters.monetary_units_in_data not in valid_units:
            self.warnings.append(f"Unusual monetary unit in data: {self.parameters.monetary_units_in_data}")
            
        # Cutoff values
        if self.parameters.io_cutoff < 0 or self.parameters.io_cutoff > 1:
            self.warnings.append(f"IO cutoff should typically be between 0 and 1, got: {self.parameters.io_cutoff}")
            
        # Time parameters
        if self.parameters.t_final <= 0:
            self.errors.append(f"t_final must be positive, got: {self.parameters.t_final}")
            
        # Transport modes
        valid_transport_modes = ['roads', 'railways', 'maritime', 'waterways', 'airways', 'pipelines', 'multimodal']
        invalid_modes = [mode for mode in self.parameters.transport_modes if mode not in valid_transport_modes]
        if invalid_modes:
            self.warnings.append(f"Non-standard transport modes specified: {invalid_modes}")

    def _validate_transaction_based_inputs(self):
        """Validate inputs specific to transaction-based mode."""
        # Firm table is required
        firm_file = self.parameters.filepaths.get('firm_table')
        if not firm_file:
            self.errors.append("Transaction-based mode requires 'firm_table' filepath to be specified")
        elif not Path(firm_file).exists():
            self.errors.append(f"Required firm table not found: {firm_file}")
        else:
            self._validate_firm_table(firm_file)

        # Transaction table is required
        transaction_file = self.parameters.filepaths.get('transaction_table')
        if not transaction_file:
            self.errors.append("Transaction-based mode requires 'transaction_table' filepath to be specified")
        elif not Path(transaction_file).exists():
            self.errors.append(f"Required transaction table not found: {transaction_file}")
        else:
            self._validate_transaction_table(transaction_file)

        # Final demand table is required for households
        final_demand_file = self.parameters.filepaths.get('final_demand')
        if not final_demand_file:
            self.errors.append("Transaction-based mode requires 'final_demand' filepath to be specified")
        elif not Path(final_demand_file).exists():
            self.errors.append(f"Required final demand table not found: {final_demand_file}")
        else:
            self._validate_final_demand_table(final_demand_file)

        # Cross-validation between firm and transaction tables
        if firm_file and transaction_file and Path(firm_file).exists() and Path(transaction_file).exists():
            self._validate_firm_transaction_consistency(firm_file, transaction_file)

    def _validate_firm_table(self, filepath):
        """Validate firm table (GeoJSON) structure and content."""
        try:
            gdf = gpd.read_file(filepath)
        except Exception as e:
            self.errors.append(f"Cannot read firm table GeoJSON: {e}")
            return

        # Check required columns
        required_cols = ['id', 'sector', 'final_demand', 'imports', 'exports', 'total_output', 'usd_per_ton', 'sector_type', 'margin', 'transport_share']
        missing_cols = [col for col in required_cols if col not in gdf.columns]
        if missing_cols:
            self.errors.append(f"firm_table.geojson missing required columns: {missing_cols}")

        # Check data types and values
        if 'id' in gdf.columns:
            if gdf['id'].duplicated().any():
                self.errors.append("firm_table.geojson contains duplicate firm IDs")
            if not gdf['id'].dtype in ['int64', 'int32']:
                self.warnings.append("firm_table.geojson: firm IDs should be integers")

        # Check for negative economic values
        economic_cols = ['final_demand', 'imports', 'exports', 'total_output', 'usd_per_ton']
        for col in economic_cols:
            if col in gdf.columns and (gdf[col] < 0).any():
                self.errors.append(f"firm_table.geojson contains negative {col} values")

        # Check proportion/ratio fields are in valid range [0, 1]
        proportion_cols = ['margin', 'transport_share']
        for col in proportion_cols:
            if col in gdf.columns:
                if (gdf[col] < 0).any() or (gdf[col] > 1).any():
                    self.errors.append(f"firm_table.geojson contains {col} values outside range [0, 1]")

        # Check usd_per_ton is positive (conversion factor should not be zero)
        if 'usd_per_ton' in gdf.columns and (gdf['usd_per_ton'] <= 0).any():
            self.errors.append("firm_table.geojson contains zero or negative usd_per_ton values")

        # Validate geometry
        if gdf.geometry.isna().any():
            self.errors.append("firm_table.geojson contains firms with missing geometry")

        # Check if points are within reasonable coordinate bounds
        bounds = gdf.total_bounds
        if abs(bounds[0]) > 180 or abs(bounds[2]) > 180:
            self.warnings.append("firm_table.geojson longitude values seem outside normal range [-180, 180]")
        if abs(bounds[1]) > 90 or abs(bounds[3]) > 90:
            self.warnings.append("firm_table.geojson latitude values seem outside normal range [-90, 90]")

    def _validate_transaction_table(self, filepath):
        """Validate transaction table structure for transaction-based mode."""
        try:
            df = pd.read_csv(filepath)
        except Exception as e:
            self.errors.append(f"Cannot read transaction_table.csv: {e}")
            return

        # Check required columns for transaction-based relationships
        required_cols = ['buyer_firm_id', 'seller_firm_id', 'transaction_value']
        missing_cols = [col for col in required_cols if col not in df.columns]
        if missing_cols:
            self.errors.append(f"transaction_table.csv missing required columns: {missing_cols}")

        # Check data types
        id_cols = ['buyer_firm_id', 'seller_firm_id']
        for col in id_cols:
            if col in df.columns and not df[col].dtype in ['int64', 'int32']:
                self.warnings.append(f"transaction_table.csv: {col} should be integer type")

        # Check for negative transaction values
        if 'transaction_value' in df.columns:
            if (df['transaction_value'] < 0).any():
                self.errors.append("transaction_table.csv contains negative transaction values")
            if (df['transaction_value'] == 0).any():
                self.warnings.append("transaction_table.csv contains zero transaction values")

        # Check for self-transactions
        if 'buyer_firm_id' in df.columns and 'seller_firm_id' in df.columns:
            self_transactions = df['buyer_firm_id'] == df['seller_firm_id']
            if self_transactions.any():
                self.errors.append("transaction_table.csv contains self-transactions (buyer_firm_id == seller_firm_id)")

        # Optional column validations
        optional_cols = ['import_value', 'export_value']
        for col in optional_cols:
            if col in df.columns and (df[col] < 0).any():
                self.errors.append(f"transaction_table.csv contains negative {col} values")

    def _validate_final_demand_table(self, filepath):
        """Validate final demand table structure for transaction-based mode."""
        try:
            # Try to read as multi-index CSV (new format)
            df = pd.read_csv(filepath, header=[0, 1], index_col=[0, 1])
        except Exception:
            # Try to read as simple CSV (old format) and provide guidance
            try:
                simple_df = pd.read_csv(filepath)
                self.errors.append(f"final_demand.csv should use multi-index format with headers [region, sector] and index [region, sector]. "
                                  f"Current format appears to be simple CSV with columns: {list(simple_df.columns)}")
                return
            except Exception as e:
                self.errors.append(f"Cannot read final_demand.csv: {e}")
                return

        # Check required column structure for multi-index format
        if not hasattr(df.columns, 'get_level_values'):
            self.errors.append("final_demand.csv must have multi-index column structure")
            return

        # Check for final_demand column in level 0
        level_0_cols = df.columns.get_level_values(0)
        if 'final_demand' not in level_0_cols:
            self.errors.append("final_demand.csv missing required 'final_demand' column in level 0")

        # Check for negative values
        numeric_cols = df.select_dtypes(include=[np.number]).columns
        for col in numeric_cols:
            if (df[col] < 0).any():
                self.errors.append(f"final_demand.csv contains negative values in column {col}")

        # Check index structure (should be region, sector)
        if not hasattr(df.index, 'get_level_values'):
            self.errors.append("final_demand.csv must have multi-index row structure [region, sector]")
            return

        if df.index.nlevels != 2:
            self.errors.append(f"final_demand.csv index should have exactly 2 levels [region, sector], found: {df.index.nlevels}")

        # Check that index values are strings (region and sector names)
        try:
            regions = df.index.get_level_values(0)
            sectors = df.index.get_level_values(1)

            # Basic sanity checks
            if len(regions) == 0 or len(sectors) == 0:
                self.errors.append("final_demand.csv appears to be empty")

            # Check for duplicated combinations
            if df.index.duplicated().any():
                self.errors.append("final_demand.csv contains duplicate region-sector combinations")

        except Exception as e:
            self.errors.append(f"Error validating final_demand.csv index structure: {e}")

    def _validate_firm_transaction_consistency(self, firm_file, transaction_file):
        """Validate consistency between firm table and transaction table."""
        try:
            firm_gdf = gpd.read_file(firm_file)
            transaction_df = pd.read_csv(transaction_file)
        except Exception as e:
            self.errors.append(f"Error reading files for consistency check: {e}")
            return

        # Get firm IDs from both files
        if 'id' not in firm_gdf.columns:
            return  # Already flagged as error in firm table validation

        firm_ids = set(firm_gdf['id'].astype(int))

        # Check buyer/seller firm IDs exist in firm table
        id_cols = ['buyer_firm_id', 'seller_firm_id']
        for col in id_cols:
            if col in transaction_df.columns:
                transaction_ids = set(transaction_df[col].dropna().astype(int))
                missing_ids = transaction_ids - firm_ids
                if missing_ids:
                    self.errors.append(f"transaction_table.csv contains {col} values not found in firm_table.geojson: {sorted(missing_ids)[:10]}")

        # Check for firms without any transactions (might be intentional)
        if 'buyer_firm_id' in transaction_df.columns and 'seller_firm_id' in transaction_df.columns:
            transaction_firm_ids = set(transaction_df['buyer_firm_id']) | set(transaction_df['seller_firm_id'])
            isolated_firms = firm_ids - transaction_firm_ids
            if isolated_firms:
                self.warnings.append(f"firm_table.geojson contains {len(isolated_firms)} firms with no transactions (may be intentional)")

        # Basic transaction balance check
        if all(col in transaction_df.columns for col in ['buyer_firm_id', 'seller_firm_id', 'transaction_value']):
            self._validate_transaction_balance(transaction_df, firm_gdf)

    def _validate_transaction_balance(self, transaction_df, firm_gdf):
        """Validate that transaction flows are reasonably balanced."""
        # Calculate total outflows and inflows per firm
        outflows = transaction_df.groupby('seller_firm_id')['transaction_value'].sum()
        inflows = transaction_df.groupby('buyer_firm_id')['transaction_value'].sum()

        # Check for firms with only inflows or only outflows (might be problematic)
        firm_ids = set(firm_gdf['id'])
        only_inflows = set(inflows.index) - set(outflows.index)
        only_outflows = set(outflows.index) - set(inflows.index)

        if only_inflows:
            self.warnings.append(f"Found {len(only_inflows)} firms with only inflows (no sales): {sorted(only_inflows)[:5]}")
        if only_outflows:
            self.warnings.append(f"Found {len(only_outflows)} firms with only outflows (no purchases): {sorted(only_outflows)[:5]}")

        # Check for extremely imbalanced transactions
        common_firms = set(inflows.index) & set(outflows.index)
        for firm_id in common_firms:
            inflow = inflows.get(firm_id, 0)
            outflow = outflows.get(firm_id, 0)
            if inflow > 0 and outflow > 0:
                ratio = max(inflow, outflow) / min(inflow, outflow)
                if ratio > 100:  # More than 100x difference
                    self.warnings.append(f"Firm {firm_id} has highly imbalanced transactions: inflow={inflow:.0f}, outflow={outflow:.0f}")


def validate_inputs(parameters) -> Tuple[bool, List[str], List[str]]:
    """
    Convenience function to validate all inputs for a given parameter set.
    
    Args:
        parameters: Loaded Parameters object
        
    Returns:
        Tuple of (is_valid, errors, warnings)
    """
    validator = InputValidator(parameters)
    return validator.validate_all_inputs()


def main():
    """Command-line interface for input validation."""
    import argparse
    import sys
    from disruptsc.parameters import Parameters
    from disruptsc import paths
    
    parser = argparse.ArgumentParser(description="Validate DisruptSC input files")
    parser.add_argument("scope", help="Region/scope to validate")
    parser.add_argument("--version", action="version", version=f"DisruptSC {__import__('disruptsc').__version__}")
    args = parser.parse_args()
    
    try:
        parameters = Parameters.load_parameters(paths.PARAMETER_FOLDER, args.scope)
        is_valid, errors, warnings = validate_inputs(parameters)
        
        # Print results
        if warnings:
            print("WARNINGS:")
            for warning in warnings:
                print(f"  ⚠ {warning}")
            print()
            
        if errors:
            print("ERRORS:")
            for error in errors:
                print(f"  ✗ {error}")
            print()
            print(f"Validation failed with {len(errors)} errors")
            sys.exit(1)
        else:
            print("✓ All validation checks passed!")
            
    except Exception as e:
        print(f"Validation failed with exception: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()