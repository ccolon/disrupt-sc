#!/usr/bin/env python3
"""
Migration Validation Framework for DisruptSC Architecture Refactoring

This framework validates that the new architecture produces equivalent
results to the baseline (pre-migration) implementation.

Usage:
    python scripts/migration_validator.py --baseline-dir baseline_capture
"""

import argparse
import json
import logging
import sys
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple
import pandas as pd
import numpy as np

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))


class MigrationValidator:
    """Validates new architecture against baseline results."""
    
    def __init__(self, baseline_dir: Path):
        self.baseline_dir = Path(baseline_dir)
        self.baseline_results = self._load_baseline_results()
        
        # Setup logging
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s'
        )
        self.logger = logging.getLogger(__name__)
        
        # Validation tolerances
        self.float_tolerance = 1e-6  # For floating point comparisons
        self.percentage_tolerance = 0.01  # For percentage-based metrics
        
    def _load_baseline_results(self) -> Dict[str, Any]:
        """Load baseline results from JSON file."""
        baseline_file = self.baseline_dir / 'baseline_results.json'
        if not baseline_file.exists():
            raise FileNotFoundError(f"Baseline results not found: {baseline_file}")
            
        with open(baseline_file, 'r') as f:
            return json.load(f)
    
    def validate_scenario(self, scenario_key: str, new_results: Dict[str, Any]) -> Dict[str, Any]:
        """
        Validate new implementation results against baseline for a single scenario.
        
        Args:
            scenario_key: Key identifying the scenario (e.g., "Ecuador_disruption")
            new_results: Results from new implementation
            
        Returns:
            Dict with validation results
        """
        validation_result = {
            'scenario': scenario_key,
            'overall_success': True,
            'checks': [],
            'errors': [],
            'warnings': []
        }
        
        # Check if baseline exists for this scenario
        if scenario_key not in self.baseline_results.get('scenarios', {}):
            validation_result['errors'].append(f"No baseline found for scenario: {scenario_key}")
            validation_result['overall_success'] = False
            return validation_result
        
        baseline = self.baseline_results['scenarios'][scenario_key]
        
        # Skip validation if baseline failed
        if not baseline.get('success', False):
            validation_result['warnings'].append(f"Baseline failed for {scenario_key}, skipping validation")
            return validation_result
        
        # Validate key metrics
        self._validate_loss_metrics(baseline, new_results, validation_result)
        self._validate_data_sizes(baseline, new_results, validation_result)  
        self._validate_output_files(scenario_key, baseline, new_results, validation_result)
        
        return validation_result
    
    def _validate_loss_metrics(self, baseline: Dict, new_results: Dict, validation_result: Dict):
        """Validate loss calculation metrics."""
        baseline_results = baseline.get('results', {})
        
        # Validate household loss
        if 'household_loss' in baseline_results and 'household_loss' in new_results:
            baseline_loss = float(baseline_results['household_loss'])
            new_loss = float(new_results['household_loss'])
            
            if self._floats_equal(baseline_loss, new_loss):
                validation_result['checks'].append({
                    'check': 'household_loss',
                    'status': 'PASS',
                    'baseline': baseline_loss,
                    'new': new_loss,
                    'difference': abs(new_loss - baseline_loss)
                })
            else:
                validation_result['checks'].append({
                    'check': 'household_loss', 
                    'status': 'FAIL',
                    'baseline': baseline_loss,
                    'new': new_loss,
                    'difference': abs(new_loss - baseline_loss)
                })
                validation_result['errors'].append(
                    f"Household loss mismatch: baseline={baseline_loss}, new={new_loss}"
                )
                validation_result['overall_success'] = False
        
        # Validate country loss  
        if 'country_loss' in baseline_results and 'country_loss' in new_results:
            baseline_loss = float(baseline_results['country_loss'])
            new_loss = float(new_results['country_loss'])
            
            if self._floats_equal(baseline_loss, new_loss):
                validation_result['checks'].append({
                    'check': 'country_loss',
                    'status': 'PASS', 
                    'baseline': baseline_loss,
                    'new': new_loss,
                    'difference': abs(new_loss - baseline_loss)
                })
            else:
                validation_result['checks'].append({
                    'check': 'country_loss',
                    'status': 'FAIL',
                    'baseline': baseline_loss, 
                    'new': new_loss,
                    'difference': abs(new_loss - baseline_loss)
                })
                validation_result['errors'].append(
                    f"Country loss mismatch: baseline={baseline_loss}, new={new_loss}"
                )
                validation_result['overall_success'] = False
    
    def _validate_data_sizes(self, baseline: Dict, new_results: Dict, validation_result: Dict):
        """Validate that data collection sizes match."""
        baseline_sizes = baseline.get('results', {}).get('data_sizes', {})
        new_sizes = new_results.get('data_sizes', {})
        
        for size_key in ['firm_data_count', 'household_data_count', 'country_data_count']:
            if size_key in baseline_sizes and size_key in new_sizes:
                baseline_count = baseline_sizes[size_key]
                new_count = new_sizes[size_key]
                
                if baseline_count == new_count:
                    validation_result['checks'].append({
                        'check': size_key,
                        'status': 'PASS',
                        'baseline': baseline_count,
                        'new': new_count
                    })
                else:
                    validation_result['checks'].append({
                        'check': size_key,
                        'status': 'FAIL', 
                        'baseline': baseline_count,
                        'new': new_count
                    })
                    validation_result['errors'].append(
                        f"Data size mismatch for {size_key}: baseline={baseline_count}, new={new_count}"
                    )
                    validation_result['overall_success'] = False
    
    def _validate_output_files(self, scenario_key: str, baseline: Dict, new_results: Dict, validation_result: Dict):
        """Validate output file structure and content."""
        baseline_files = baseline.get('results', {}).get('output_files', {})
        new_files = new_results.get('output_files', {})
        
        # Check that key files exist in both  
        for file_path in baseline_files:
            if file_path not in new_files:
                validation_result['errors'].append(f"Missing output file: {file_path}")
                validation_result['overall_success'] = False
            else:
                # Validate CSV headers if applicable
                baseline_file = baseline_files[file_path]
                new_file = new_files[file_path] 
                
                if 'csv_headers' in baseline_file and 'csv_headers' in new_file:
                    if baseline_file['csv_headers'] == new_file['csv_headers']:
                        validation_result['checks'].append({
                            'check': f'{file_path}_headers',
                            'status': 'PASS'
                        })
                    else:
                        validation_result['checks'].append({
                            'check': f'{file_path}_headers',
                            'status': 'FAIL',
                            'baseline': baseline_file['csv_headers'],
                            'new': new_file['csv_headers']  
                        })
                        validation_result['errors'].append(
                            f"CSV headers mismatch in {file_path}"
                        )
                        validation_result['overall_success'] = False
        
        # Check for unexpected new files
        for file_path in new_files:
            if file_path not in baseline_files:
                validation_result['warnings'].append(f"New output file not in baseline: {file_path}")
    
    def _floats_equal(self, a: float, b: float, tolerance: Optional[float] = None) -> bool:
        """Check if two floats are equal within tolerance."""
        if tolerance is None:
            tolerance = self.float_tolerance
            
        if a == 0 and b == 0:
            return True
        elif a == 0 or b == 0:
            return abs(a - b) < tolerance
        else:
            # Use relative tolerance for non-zero values
            relative_diff = abs(a - b) / max(abs(a), abs(b))
            return relative_diff < tolerance
    
    def validate_all_scenarios(self, new_results_by_scenario: Dict[str, Dict]) -> Dict[str, Any]:
        """
        Validate all scenarios and return summary.
        
        Args:
            new_results_by_scenario: Dict mapping scenario_key to new results
            
        Returns:
            Overall validation summary
        """
        validation_summary = {
            'total_scenarios': 0,
            'successful_validations': 0,
            'failed_validations': 0,
            'skipped_validations': 0,
            'scenario_results': {},
            'overall_success': True
        }
        
        for scenario_key, new_results in new_results_by_scenario.items():
            self.logger.info(f"Validating scenario: {scenario_key}")
            
            validation_result = self.validate_scenario(scenario_key, new_results)
            validation_summary['scenario_results'][scenario_key] = validation_result
            validation_summary['total_scenarios'] += 1
            
            if validation_result['overall_success']:
                validation_summary['successful_validations'] += 1
                self.logger.info(f"✓ {scenario_key} validation PASSED")
            else:
                validation_summary['failed_validations'] += 1
                validation_summary['overall_success'] = False
                self.logger.error(f"✗ {scenario_key} validation FAILED")
                
                # Log specific errors
                for error in validation_result['errors']:
                    self.logger.error(f"  - {error}")
        
        return validation_summary
    
    def run_validation_test(self) -> bool:
        """
        Run a validation test using synthetic data.
        This tests the validation framework itself.
        """
        self.logger.info("Running validation framework self-test...")
        
        # Create synthetic test data that should pass
        synthetic_new_results = {}
        
        for scenario_key, baseline_scenario in self.baseline_results.get('scenarios', {}).items():
            if baseline_scenario.get('success', False):
                # Create new results that match baseline
                baseline_results = baseline_scenario.get('results', {})
                synthetic_new_results[scenario_key] = {
                    'household_loss': baseline_results.get('household_loss', 0),
                    'country_loss': baseline_results.get('country_loss', 0),
                    'data_sizes': baseline_results.get('data_sizes', {}),
                    'output_files': baseline_results.get('output_files', {})
                }
        
        # Run validation
        validation_summary = self.validate_all_scenarios(synthetic_new_results)
        
        if validation_summary['overall_success']:
            self.logger.info("✓ Validation framework self-test PASSED")
            return True
        else:
            self.logger.error("✗ Validation framework self-test FAILED")
            return False


def main():
    parser = argparse.ArgumentParser(description='Validate migration against baseline')
    parser.add_argument('--baseline-dir', required=True,
                       help='Directory containing baseline results')
    parser.add_argument('--test', action='store_true',
                       help='Run validation framework self-test')
    
    args = parser.parse_args()
    
    # Create validator
    validator = MigrationValidator(args.baseline_dir)
    
    if args.test:
        # Run self-test
        success = validator.run_validation_test()
        sys.exit(0 if success else 1)
    else:
        print("Validation framework ready.")
        print(f"Baseline loaded: {len(validator.baseline_results.get('scenarios', {}))} scenarios")
        print("Use this validator programmatically to validate new implementation results.")


if __name__ == "__main__":
    main()