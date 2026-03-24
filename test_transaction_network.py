#!/usr/bin/env python3
"""Test transaction-based supply chain network creation."""

import sys
sys.path.append('src')

from disruptsc.model.model import Model
from disruptsc.parameters import Parameters
from disruptsc import paths
import logging

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')

def test_transaction_based_network():
    """Test building supply chain network from transaction data."""

    print("Testing transaction-based supply chain network creation...")

    # Load parameters for transaction-based mode
    scope = "Ecuador_transaction"
    parameters = Parameters.load_parameters(paths.PARAMETER_FOLDER, scope)

    # Ensure we're in transaction-based mode
    parameters.firm_data_type = "transaction_based"

    print(f"Firm data type: {parameters.firm_data_type}")
    print(f"Transaction table path: {parameters.filepaths.get('transaction_table', 'Not set')}")

    # Create model instance
    model = Model(parameters=parameters)

    # Initialize up to supply chain network
    print("\n1. Setting up transport network...")
    model.setup_transport_network()

    print("\n2. Setting up agents...")
    model.setup_agents()

    print(f"Created {len(model.firms)} firms")
    print(f"Created {len(model.households)} households")
    print(f"Created {len(model.countries)} countries")

    print("\n3. Setting up supply chain network...")
    model.setup_sc_network()

    print(f"Created supply chain network with {model.sc_network.number_of_edges()} edges")
    print(f"Network has {model.sc_network.number_of_nodes()} nodes")

    # Analyze network structure
    print("\n4. Network analysis:")

    # Count different types of links
    domestic_links = 0
    import_links = 0
    household_links = 0

    for u, v, data in model.sc_network.edges(data=True):
        commercial_link = data['object']

        if commercial_link.category == 'domestic':
            domestic_links += 1
        elif commercial_link.category == 'import':
            import_links += 1
        elif hasattr(v, 'agent_type') and v.agent_type == 'household':
            household_links += 1

    print(f"  Domestic firm-to-firm links: {domestic_links}")
    print(f"  Import links: {import_links}")
    print(f"  Household links: {household_links}")

    # Check firm connectivity
    connected_firms = set()
    for node in model.sc_network.nodes():
        if hasattr(node, 'agent_type') and node.agent_type == 'firm':
            connected_firms.add(node.pid)

    print(f"  Connected firms: {len(connected_firms)} out of {len(model.firms)}")

    # Sample firm analysis
    if len(model.firms) > 0:
        sample_firm_id = list(model.firms.keys())[0]
        sample_firm = model.firms[sample_firm_id]

        print(f"\n5. Sample firm analysis (Firm {sample_firm_id}):")
        print(f"  Sector: {sample_firm.sector}")
        print(f"  Suppliers: {len(sample_firm.suppliers)}")
        print(f"  Clients: {len(sample_firm.clients)}")
        print(f"  Input mix: {sample_firm.input_mix}")

        # Check suppliers and clients
        suppliers_in_network = [s for s in sample_firm.suppliers.keys()
                               if any(edge[0].pid == s for edge in model.sc_network.in_edges(sample_firm))]
        clients_in_network = [c for c in sample_firm.clients.keys()
                             if any(edge[1].pid == c for edge in model.sc_network.out_edges(sample_firm))]

        print(f"  Suppliers in network: {len(suppliers_in_network)}")
        print(f"  Clients in network: {len(clients_in_network)}")

    print("\n✓ Transaction-based network creation test completed successfully!")

if __name__ == "__main__":
    test_transaction_based_network()