#!/usr/bin/env python3
"""
Baseline Capture Script for DisruptSC Architecture Migration

This script captures the current behavior of all simulation types
to serve as golden masters for validation during migration.

Usage:
    python scripts/capture_baseline.py [--scope SCOPE] [--simulation-type TYPE] [--output-dir DIR]
"""

import argparse
import json
import logging
import os
import shutil
import sys
import time
import traceback
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))

from disruptsc.main import setup_model
from disruptsc.model.model import Model
from disruptsc.parameters import Parameters
from disruptsc.paths import PARAMETER_FOLDER, OUTPUT_FOLDER
from disruptsc.simulation.factory import ExecutorFactory


class BaselineCapture:
    """Captures baseline simulation results for migration validation."""
    
    def __init__(self, output_dir: Path):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.results = {}
        
        # Setup logging
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(self.output_dir / 'baseline_capture.log'),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger(__name__)

    def get_test_scenarios(self) -> List[Dict[str, str]]:
        """Define all test scenarios to capture."""
        scenarios = []
        
        # Get available scopes
        available_scopes = self._get_available_scopes()
        
        # Basic simulation types for each scope
        basic_types = ["initial_state", "disruption"]
        
        for scope in available_scopes:
            for sim_type in basic_types:
                scenarios.append({
                    'scope': scope,
                    'simulation_type': sim_type,
                    'description': f'{scope} - {sim_type}'
                })
        
        # Destruction scenarios (only for scopes that support them)
        destruction_types = [
            "destruction_sectors", 
            "destruction_provinces", 
            "destruction_cantons",
            "destruction_province_sectors",
            "destruction_canton_sectors"
        ]
        
        # Test destruction types on Ecuador (known to have destruction config)
        if "Ecuador" in available_scopes:
            for dest_type in destruction_types:
                scenarios.append({
                    'scope': "Ecuador",
                    'simulation_type': dest_type,
                    'description': f'Ecuador - {dest_type}'
                })
        
        return scenarios

    def _get_available_scopes(self) -> List[str]:
        """Get list of available parameter scopes."""
        scopes = []
        for file_path in PARAMETER_FOLDER.glob("user_defined_*.yaml"):
            scope = file_path.stem.replace("user_defined_", "")
            scopes.append(scope)
        
        # Add default if exists
        if (PARAMETER_FOLDER / "default.yaml").exists():
            scopes.append("default")
            
        return sorted(scopes)

    def capture_scenario(self, scope: str, simulation_type: str) -> Dict[str, Any]:
        """Capture baseline results for a single scenario."""
        self.logger.info(f"Capturing baseline for {scope} - {simulation_type}")
        
        scenario_results = {
            'scope': scope,
            'simulation_type': simulation_type,
            'timestamp': datetime.now().isoformat(),
            'success': False,
            'error': None,
            'results': {}
        }
        
        try:
            # Load parameters
            parameters = Parameters.load_parameters(PARAMETER_FOLDER, scope)
            parameters.simulation_type = simulation_type
            
            # Set minimal output for baseline capture
            parameters.export_files = True
            # For destruction simulations, use very short duration for baseline capture
            if simulation_type.startswith('destruction_'):
                parameters.t_final = 5  # Very short for destruction baseline
                # Also set short destruction periods for testing
                parameters.destruction_periods = [2, 3, 5]
            else:
                parameters.t_final = min(parameters.t_final, 10)  # Limit duration for other types
            
            # Create temporary output folder manually
            temp_output = self.output_dir / f"temp_{scope}_{simulation_type}"
            temp_output.mkdir(parents=True, exist_ok=True)
            
            # Manually set up export folder (bypass automatic creation)
            parameters.export_folder = temp_output
            if parameters.with_output_folder:
                parameters.export()  # Export parameters to folder
                # Skip the print statement from initialize_exports
            
            # Setup model (with minimal caching for speed)
            cache_params = {
                'transport_network': False,
                'agents': False, 
                'sc_network': False,
                'logistic_routes': False
            }
            model = setup_model(parameters, cache_params)
            
            # Execute simulation
            executor = ExecutorFactory.create_executor(simulation_type, model, parameters)
            simulation = executor.execute()
            
            # Capture key results
            if hasattr(simulation, '__iter__') and not isinstance(simulation, str):
                # Handle list of simulations (Monte Carlo, etc.)
                if len(simulation) > 0:
                    sim_to_analyze = simulation[-1] if simulation else None
                else:
                    sim_to_analyze = None
            else:
                sim_to_analyze = simulation
            
            if sim_to_analyze:
                # Capture loss calculations
                if hasattr(sim_to_analyze, 'household_data') and sim_to_analyze.household_data:
                    try:
                        household_loss = sim_to_analyze.calculate_household_loss(model.household_table)
                        scenario_results['results']['household_loss'] = float(household_loss)
                    except Exception as e:
                        self.logger.warning(f"Could not calculate household loss: {e}")
                
                if hasattr(sim_to_analyze, 'country_data') and sim_to_analyze.country_data:
                    try:
                        country_loss = sim_to_analyze.calculate_country_loss()
                        scenario_results['results']['country_loss'] = float(country_loss)
                    except Exception as e:
                        self.logger.warning(f"Could not calculate country loss: {e}")
                
                # Capture data sizes
                scenario_results['results']['data_sizes'] = {
                    'firm_data_count': len(sim_to_analyze.firm_data),
                    'household_data_count': len(sim_to_analyze.household_data),
                    'country_data_count': len(sim_to_analyze.country_data),
                    'transport_data_count': len(sim_to_analyze.transport_network_data)
                }
            
            # Capture output files if they exist
            output_files = {}
            if temp_output.exists():
                for file_path in temp_output.rglob("*"):
                    if file_path.is_file():
                        rel_path = str(file_path.relative_to(temp_output))
                        output_files[rel_path] = {
                            'size_bytes': file_path.stat().st_size,
                            'exists': True
                        }
                        
                        # For CSV files, also capture headers and row count
                        if file_path.suffix == '.csv':
                            try:
                                with open(file_path, 'r') as f:
                                    first_line = f.readline().strip()
                                    row_count = sum(1 for _ in f) + 1  # +1 for header
                                output_files[rel_path]['csv_headers'] = first_line
                                output_files[rel_path]['row_count'] = row_count
                            except Exception as e:
                                self.logger.warning(f"Could not read CSV {file_path}: {e}")
            
            scenario_results['results']['output_files'] = output_files
            scenario_results['success'] = True
            
            # Save output files to baseline folder
            baseline_output_dir = self.output_dir / 'baselines' / f"{scope}_{simulation_type}"
            if temp_output.exists():
                try:
                    if baseline_output_dir.exists():
                        shutil.rmtree(baseline_output_dir)
                    baseline_output_dir.parent.mkdir(parents=True, exist_ok=True)
                    shutil.copytree(temp_output, baseline_output_dir)
                except Exception as e:
                    self.logger.warning(f"Could not copy baseline files: {e}")
                    # Continue with the rest of the capture
            
            # Cleanup temp folder
            if temp_output.exists():
                shutil.rmtree(temp_output)
                
        except Exception as e:
            scenario_results['error'] = str(e)
            scenario_results['traceback'] = traceback.format_exc()
            self.logger.error(f"Error capturing {scope} - {simulation_type}: {e}")
            self.logger.debug(traceback.format_exc())
        
        return scenario_results

    def capture_all_scenarios(self, filter_scope: Optional[str] = None, 
                            filter_sim_type: Optional[str] = None) -> Dict[str, Any]:
        """Capture baselines for all or filtered scenarios."""
        scenarios = self.get_test_scenarios()
        
        # Apply filters
        if filter_scope:
            scenarios = [s for s in scenarios if s['scope'] == filter_scope]
        if filter_sim_type:
            scenarios = [s for s in scenarios if s['simulation_type'] == filter_sim_type]
        
        self.logger.info(f"Capturing {len(scenarios)} scenarios...")
        
        results = {
            'capture_timestamp': datetime.now().isoformat(),
            'scenarios': {},
            'summary': {
                'total': len(scenarios),
                'successful': 0,
                'failed': 0
            }
        }
        
        for scenario in scenarios:
            scenario_key = f"{scenario['scope']}_{scenario['simulation_type']}"
            
            start_time = time.time()
            scenario_result = self.capture_scenario(scenario['scope'], scenario['simulation_type'])
            elapsed_time = time.time() - start_time
            
            scenario_result['elapsed_time_seconds'] = elapsed_time
            results['scenarios'][scenario_key] = scenario_result
            
            if scenario_result['success']:
                results['summary']['successful'] += 1
                self.logger.info(f"✓ {scenario_key} captured successfully ({elapsed_time:.1f}s)")
            else:
                results['summary']['failed'] += 1
                self.logger.error(f"✗ {scenario_key} failed ({elapsed_time:.1f}s)")
        
        # Save results summary
        with open(self.output_dir / 'baseline_results.json', 'w') as f:
            json.dump(results, f, indent=2, default=str)
        
        self.logger.info(f"Baseline capture complete: {results['summary']['successful']}/{results['summary']['total']} successful")
        return results


def main():
    parser = argparse.ArgumentParser(description='Capture baseline simulation results')
    parser.add_argument('--scope', help='Filter to specific scope (e.g., Ecuador)')
    parser.add_argument('--simulation-type', help='Filter to specific simulation type')
    parser.add_argument('--output-dir', default='baseline_capture', 
                       help='Output directory for baseline results')
    
    args = parser.parse_args()
    
    # Create baseline capture instance
    baseline = BaselineCapture(args.output_dir)
    
    # Run baseline capture
    results = baseline.capture_all_scenarios(
        filter_scope=args.scope,
        filter_sim_type=args.simulation_type
    )
    
    # Print summary
    print("\n" + "="*60)
    print("BASELINE CAPTURE SUMMARY")
    print("="*60)
    print(f"Total scenarios: {results['summary']['total']}")
    print(f"Successful: {results['summary']['successful']}")
    print(f"Failed: {results['summary']['failed']}")
    
    if results['summary']['failed'] > 0:
        print("\nFailed scenarios:")
        for key, scenario in results['scenarios'].items():
            if not scenario['success']:
                print(f"  - {key}: {scenario['error']}")
    
    print(f"\nResults saved to: {baseline.output_dir}")
    

if __name__ == "__main__":
    main()