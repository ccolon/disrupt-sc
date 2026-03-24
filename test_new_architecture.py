#!/usr/bin/env python3
"""
Test script for the complete new simulation architecture.

This validates that the orchestrator, runners, analyzers, and exporters
work together correctly as an integrated system.
"""

import sys
import tempfile
from pathlib import Path
import logging

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / 'src'))

from disruptsc.parameters import Parameters
from disruptsc.paths import PARAMETER_FOLDER
from disruptsc.simulation.core.data_structures import SimulationData
from disruptsc.simulation.orchestration import SimulationOrchestrator
from disruptsc.simulation.runners import (BaseSimulationRunner, DisruptionRunner, 
                                         InitialStateRunner, DestructionRunner)
from disruptsc.simulation.analysis import CompositeAnalyzer
from disruptsc.simulation.export import CompositeExporter

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class MockModel:
    """Mock model for testing the new architecture."""
    
    def __init__(self):
        self.firms = MockAgentCollection('firms')
        self.households = MockAgentCollection('households')
        self.countries = MockAgentCollection('countries')
        self.sc_network = MockSCNetwork()
        self.transport_network = MockTransportNetwork()
        self.firm_table = None
        self.household_table = None
        self.country_table = None
        
    def reset_to_initial_state(self):
        """Reset model state for destruction scenarios."""
        pass


class MockAgentCollection:
    """Mock agent collection for testing."""
    
    def __init__(self, agent_type: str):
        self.agent_type = agent_type
        self.agents = self._create_mock_agents()
    
    def _create_mock_agents(self):
        agents = []
        for i in range(3):
            agent = MockAgent(f'{self.agent_type}_{i}', self.agent_type)
            agents.append(agent)
        return agents
    
    def values(self):
        """Return agents list to be compatible with BaseAgents.values()"""
        return self.agents
    
    def __len__(self):
        """Return length for compatibility with BaseAgents"""
        return len(self.agents)


class MockAgent:
    """Mock agent for testing."""
    
    def __init__(self, agent_id: str, agent_type: str):
        self.id = agent_id
        self.agent_id = agent_id
        self.agent_type = agent_type
        
        # Initialize agent attributes based on type
        if agent_type == 'firms':
            self.sector = f'sector_{agent_id[-1]}'
            self.production = 100.0
            self.capacity_utilization = 1.0
            self.inventory = 50.0
            self.production_capacity = 100.0
        elif agent_type == 'households':
            self.consumption = 150.0
            self.consumption_lost = 0.0
            self.consumption_baseline = 150.0
            self.population = 4
        elif agent_type == 'countries':
            self.gdp = 1000.0
            self.gdp_lost = 0.0
            self.gdp_baseline = 1000.0
            self.imports = 100.0
            self.exports = 120.0
        
        self.od_point = f'node_{agent_id[-1]}'
        self.subregion_province = f'province_{agent_id[-1]}'
        self.subregion_canton = f'canton_{agent_id[-1]}'
    
    def update_production(self):
        """Mock production update."""
        if hasattr(self, 'production'):
            self.production *= 0.95  # Simulate decline
    
    def update_inventory(self):
        """Mock inventory update.""" 
        if hasattr(self, 'inventory'):
            self.inventory *= 0.9  # Simulate inventory consumption
    
    def calculate_capacity_utilization(self):
        """Mock capacity calculation."""
        if hasattr(self, 'production') and hasattr(self, 'production_capacity'):
            self.capacity_utilization = self.production / self.production_capacity
    
    def update_consumption(self):
        """Mock consumption update."""
        if hasattr(self, 'consumption'):
            self.consumption *= 0.95  # Simulate decline
            self.consumption_lost = self.consumption_baseline - self.consumption
    
    def apply_destruction(self, intensity: float):
        """Mock destruction application."""
        if hasattr(self, 'production_capacity'):
            self.production_capacity *= (1 - intensity)
        if hasattr(self, 'consumption_baseline'):
            self.consumption_baseline *= (1 - intensity)


class MockSCNetwork:
    """Mock supply chain network."""
    
    def __init__(self):
        import networkx as nx
        self.graph = nx.DiGraph()
        # Create simple network
        self.graph.add_edges_from([(0, 1), (1, 2), (2, 0)])
    
    def calculate_io_matrix(self):
        """Mock IO matrix calculation."""
        import pandas as pd
        data = {
            'sector_0': [10, 5, 3],
            'sector_1': [8, 12, 6],
            'sector_2': [4, 7, 15]
        }
        return pd.DataFrame(data, index=['sector_0', 'sector_1', 'sector_2'])
    
    def generate_edge_list(self):
        """Mock edge list generation."""
        import pandas as pd
        edges = [
            {'source': 0, 'target': 1, 'weight': 10.0},
            {'source': 1, 'target': 2, 'weight': 8.0},
            {'source': 2, 'target': 0, 'weight': 5.0}
        ]
        return pd.DataFrame(edges)


class MockTransportNetwork:
    """Mock transport network."""
    
    def __init__(self):
        import networkx as nx
        self.graph = nx.Graph()
        # Create simple transport network
        edges = [
            (0, 1, {'capacity': 100, 'transport_mode': 'road'}),
            (1, 2, {'capacity': 80, 'transport_mode': 'rail'}),
            (2, 0, {'capacity': 60, 'transport_mode': 'road'})
        ]
        self.graph.add_edges_from(edges)


def test_orchestrator_creation():
    """Test that orchestrators can be created for different simulation types."""
    logger.info("Testing orchestrator creation...")
    
    # Load parameters
    parameters = Parameters.load_parameters(PARAMETER_FOLDER, 'default')
    model = MockModel()
    
    # Test initial_state orchestrator
    parameters.simulation_type = 'initial_state'
    orchestrator = SimulationOrchestrator(model, parameters)
    assert isinstance(orchestrator.runner, InitialStateRunner)
    logger.info("✓ Initial state orchestrator created successfully")
    
    # Test disruption orchestrator
    parameters.simulation_type = 'disruption'
    orchestrator = SimulationOrchestrator(model, parameters)
    assert isinstance(orchestrator.runner, DisruptionRunner)
    logger.info("✓ Disruption orchestrator created successfully")
    
    # Test destruction orchestrator
    parameters.simulation_type = 'destruction_provinces'
    orchestrator = SimulationOrchestrator(model, parameters)
    assert isinstance(orchestrator.runner, DestructionRunner)
    logger.info("✓ Destruction orchestrator created successfully")
    
    return True


def test_initial_state_execution():
    """Test complete initial state simulation execution."""
    logger.info("Testing initial state simulation execution...")
    
    parameters = Parameters.load_parameters(PARAMETER_FOLDER, 'default')
    parameters.simulation_type = 'initial_state'
    parameters.t_final = 3
    parameters.export_files = True
    
    model = MockModel()
    
    # Create temporary export folder
    with tempfile.TemporaryDirectory() as temp_dir:
        parameters.export_folder = Path(temp_dir)
        
        # Execute simulation
        orchestrator = SimulationOrchestrator(model, parameters)
        result = orchestrator.execute()
        
        # Validate result
        assert result == True  # Initial state returns True
        
        # Check that data was collected
        simulation_data = orchestrator.get_simulation_data()
        assert simulation_data is not None
        logger.info(f"Simulation data collected: {len(simulation_data.firm_data)} firm records")
        
        # Check that analysis was performed
        analysis_results = orchestrator.get_analysis_results()
        assert analysis_results is not None
        assert len(analysis_results.export_tables) > 0
        logger.info(f"Analysis results: {len(analysis_results.export_tables)} export tables")
        
        # Check that files were exported
        export_files = list(Path(temp_dir).glob("*.csv"))
        assert len(export_files) > 0
        logger.info(f"Export files created: {len(export_files)}")
    
    logger.info("✓ Initial state simulation execution completed successfully")
    return True


def test_disruption_execution():
    """Test complete disruption simulation execution."""
    logger.info("Testing disruption simulation execution...")
    
    parameters = Parameters.load_parameters(PARAMETER_FOLDER, 'default')
    parameters.simulation_type = 'disruption'
    parameters.t_final = 5
    parameters.export_files = True
    parameters.disruptions = [
        {
            'type': 'capital_destruction',
            'intensity': 0.3,
            'start_time': 1
        }
    ]
    
    model = MockModel()
    
    # Create temporary export folder
    with tempfile.TemporaryDirectory() as temp_dir:
        parameters.export_folder = Path(temp_dir)
        
        # Execute simulation
        orchestrator = SimulationOrchestrator(model, parameters)
        result = orchestrator.execute()
        
        # Validate result (should be LegacyCompatibleSimulation)
        assert result is not None
        assert hasattr(result, 'calculate_household_loss')
        assert hasattr(result, 'calculate_country_loss')
        
        # Test legacy methods
        household_loss = result.calculate_household_loss()
        country_loss = result.calculate_country_loss()
        assert isinstance(household_loss, (int, float))
        assert isinstance(country_loss, (int, float))
        logger.info(f"Loss calculations: household={household_loss}, country={country_loss}")
        
        # Check data collection
        simulation_data = orchestrator.get_simulation_data()
        assert len(simulation_data.firm_data) > 0
        assert len(simulation_data.household_data) > 0
        
        # Check analysis results
        analysis_results = orchestrator.get_analysis_results()
        assert 'household' in analysis_results.metrics
        assert 'country' in analysis_results.metrics
        
        # Check exports
        export_files = list(Path(temp_dir).glob("*.csv"))
        assert len(export_files) > 0
        logger.info(f"Export files created: {[f.name for f in export_files]}")
    
    logger.info("✓ Disruption simulation execution completed successfully")
    return True


def test_destruction_execution():
    """Test destruction simulation execution."""
    logger.info("Testing destruction simulation execution...")
    
    parameters = Parameters.load_parameters(PARAMETER_FOLDER, 'default')
    parameters.simulation_type = 'destruction_provinces'
    parameters.t_final = 3
    parameters.destruction_periods = [1, 2, 3]
    parameters.export_files = True
    
    model = MockModel()
    
    # Create temporary export folder
    with tempfile.TemporaryDirectory() as temp_dir:
        parameters.export_folder = Path(temp_dir)
        
        # Execute simulation
        orchestrator = SimulationOrchestrator(model, parameters)
        result = orchestrator.execute()
        
        # Validate result
        assert result is not None
        assert hasattr(result, 'calculate_household_loss')
        
        # Test period-specific loss calculations
        for period in parameters.destruction_periods:
            period_loss = result.calculate_household_loss(time_steps=[period])
            assert isinstance(period_loss, (int, float))
        
        # Check batch processing metadata
        simulation_data = orchestrator.get_simulation_data()
        assert 'destruction_scenarios' in simulation_data.metadata
        assert simulation_data.metadata['destruction_scenarios'] > 0
        logger.info(f"Destruction scenarios executed: {simulation_data.metadata['destruction_scenarios']}")
        
        # Check that data contains scenario information
        firm_data_with_scenarios = [d for d in simulation_data.firm_data if 'scenario_id' in d]
        assert len(firm_data_with_scenarios) > 0
        logger.info(f"Firm records with scenario info: {len(firm_data_with_scenarios)}")
    
    logger.info("✓ Destruction simulation execution completed successfully")
    return True


def test_component_integration():
    """Test integration between components."""
    logger.info("Testing component integration...")
    
    parameters = Parameters.load_parameters(PARAMETER_FOLDER, 'default')
    parameters.simulation_type = 'disruption'
    parameters.t_final = 3
    
    model = MockModel()
    
    # Test runner → analyzer → exporter pipeline
    runner = DisruptionRunner(model, parameters)
    simulation_data = runner.execute()
    assert len(simulation_data.firm_data) > 0
    logger.info("✓ Runner execution successful")
    
    analyzer = CompositeAnalyzer(parameters)
    analysis_results = analyzer.analyze(simulation_data)
    assert len(analysis_results.metrics) > 0
    assert len(analysis_results.export_tables) > 0
    logger.info("✓ Analyzer execution successful")
    
    with tempfile.TemporaryDirectory() as temp_dir:
        parameters.export_files = True
        exporter = CompositeExporter(parameters)
        export_success = exporter.export(analysis_results, Path(temp_dir))
        assert export_success
        
        # Verify files were created
        csv_files = list(Path(temp_dir).glob("*.csv"))
        json_files = list(Path(temp_dir).glob("*.json"))
        assert len(csv_files) > 0
        assert len(json_files) > 0
        logger.info(f"✓ Exporter created {len(csv_files)} CSV and {len(json_files)} JSON files")
    
    logger.info("✓ Component integration test successful")
    return True


def test_legacy_compatibility():
    """Test backward compatibility with existing interfaces."""
    logger.info("Testing legacy compatibility...")
    
    parameters = Parameters.load_parameters(PARAMETER_FOLDER, 'default')
    parameters.simulation_type = 'disruption'
    parameters.t_final = 3
    parameters.export_files = False  # Disable actual export for this test
    
    model = MockModel()
    
    # Execute through orchestrator
    orchestrator = SimulationOrchestrator(model, parameters)
    result = orchestrator.execute()
    
    # Test that result has all expected legacy methods
    legacy_methods = [
        'calculate_household_loss',
        'calculate_country_loss',
        'export_sc_network_matrices',
        'export_times_series',
        'log_and_export_summary_results'
    ]
    
    for method_name in legacy_methods:
        assert hasattr(result, method_name), f"Missing legacy method: {method_name}"
        logger.info(f"✓ Legacy method available: {method_name}")
    
    # Test that legacy attributes exist
    legacy_attributes = ['firm_data', 'household_data', 'country_data', 'transport_network_data']
    for attr_name in legacy_attributes:
        assert hasattr(result, attr_name), f"Missing legacy attribute: {attr_name}"
        logger.info(f"✓ Legacy attribute available: {attr_name}")
    
    # Test method calls with various parameter combinations
    assert result.calculate_household_loss() >= 0
    assert result.calculate_household_loss(calculation_type="stock", value_type="absolute") >= 0
    assert result.calculate_household_loss(calculation_type="flow", value_type="relative") >= 0
    assert result.calculate_country_loss() >= 0
    logger.info("✓ Legacy method calls working correctly")
    
    logger.info("✓ Legacy compatibility test successful")
    return True


def main():
    """Run all architecture tests."""
    logger.info("Starting complete new architecture tests...")
    
    try:
        # Test orchestrator creation
        if not test_orchestrator_creation():
            logger.error("Orchestrator creation tests failed")
            return False
        
        # Test initial state execution
        if not test_initial_state_execution():
            logger.error("Initial state execution tests failed")
            return False
        
        # Test disruption execution
        if not test_disruption_execution():
            logger.error("Disruption execution tests failed")
            return False
        
        # Test destruction execution
        if not test_destruction_execution():
            logger.error("Destruction execution tests failed")
            return False
        
        # Test component integration
        if not test_component_integration():
            logger.error("Component integration tests failed")
            return False
        
        # Test legacy compatibility
        if not test_legacy_compatibility():
            logger.error("Legacy compatibility tests failed")
            return False
        
        logger.info("🎉 All new architecture tests passed!")
        logger.info("✅ The new simulation architecture is working correctly")
        logger.info("✅ All components integrate properly")
        logger.info("✅ Legacy compatibility is maintained")
        logger.info("✅ Ready for migration to production")
        
        return True
        
    except Exception as e:
        logger.error(f"Architecture tests failed with error: {e}")
        import traceback
        logger.error(traceback.format_exc())
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)