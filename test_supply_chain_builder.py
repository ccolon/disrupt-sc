#!/usr/bin/env python3
"""Test supply chain network builder directly."""

import sys
sys.path.append('src')

import pandas as pd
from disruptsc.model.network_builders.supply_chain import build_network_from_transactions
from disruptsc.network.sc_network import ScNetwork
from disruptsc.agents.firm import Firms, Firm
from disruptsc.agents.household import Households, Household
from disruptsc.agents.country import Countries, Country
from disruptsc.parameters import Parameters
from disruptsc import paths
import logging

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')

def test_supply_chain_builder():
    """Test the supply chain network builder function directly."""

    print("Testing supply chain network builder...")

    # Create test agents
    firms = Firms([
        Firm(pid=0, region_sector='ECU_A0116', sector='A0116', od_point=0, region='ECU',
             name='Firm_0', long=-78.5, lat=-1.5, importance=1.0, sector_type='agriculture'),
        Firm(pid=1, region_sector='ECU_A0116', sector='A0116', od_point=1, region='ECU',
             name='Firm_1', long=-78.6, lat=-1.6, importance=1.0, sector_type='agriculture'),
        Firm(pid=2, region_sector='ECU_A0161', sector='A0161', od_point=2, region='ECU',
             name='Firm_2', long=-78.7, lat=-1.7, importance=1.0, sector_type='agriculture')
    ])

    households = Households([
        Household(pid='hh_0', region='ECU', od_point=10, name='Household_0',
                 long=-78.8, lat=-1.8, population=1000, sector_consumption={'ECU_A0116': 100, 'ECU_A0161': 50})
    ])

    countries = Countries([
        Country(pid='imports', region='imports', supply_importance=1.0, od_point=100, long=0, lat=0),
        Country(pid='exports', region='exports', supply_importance=0.5, od_point=101, long=0, lat=0)
    ])

    # Create empty network
    sc_network = ScNetwork()

    # Load test parameters
    scope = "Ecuador_transaction"
    parameters = Parameters.load_parameters(paths.PARAMETER_FOLDER, scope)

    # Test transaction table path
    transaction_table_path = 'data/Ecuador_transaction/Economic/transaction_table.csv'

    print(f"Transaction table path: {transaction_table_path}")
    print(f"Number of firms: {len(firms)}")
    print(f"Number of households: {len(households)}")
    print(f"Number of countries: {len(countries)}")

    # Test the builder function
    try:
        build_network_from_transactions(
            sc_network,
            firms,
            households,
            countries,
            transaction_table_path,
            parameters
        )

        print(f"\n✓ Network creation successful!")
        print(f"Network has {sc_network.number_of_nodes()} nodes")
        print(f"Network has {sc_network.number_of_edges()} edges")

        # Analyze network structure
        print("\nNetwork analysis:")

        # Count different types of links
        domestic_links = 0
        import_links = 0
        household_links = 0
        other_links = 0

        for u, v, data in sc_network.edges(data=True):
            commercial_link = data['object']

            if commercial_link.category == 'domestic':
                domestic_links += 1
            elif commercial_link.category == 'import':
                import_links += 1
            elif hasattr(v, 'agent_type') and v.agent_type == 'household':
                household_links += 1
            else:
                other_links += 1

        print(f"  Domestic firm-to-firm links: {domestic_links}")
        print(f"  Import links: {import_links}")
        print(f"  Household links: {household_links}")
        print(f"  Other links: {other_links}")

        # Sample link analysis
        if sc_network.number_of_edges() > 0:
            sample_edge = list(sc_network.edges(data=True))[0]
            u, v, data = sample_edge
            link = data['object']

            print(f"\nSample commercial link:")
            print(f"  PID: {link.pid}")
            print(f"  Supplier: {link.supplier_id} ({u.agent_type if hasattr(u, 'agent_type') else 'unknown'})")
            print(f"  Buyer: {link.buyer_id} ({v.agent_type if hasattr(v, 'agent_type') else 'unknown'})")
            print(f"  Product: {link.product}")
            print(f"  Category: {link.category}")
            print(f"  Weight: {data.get('weight', 'No weight')}")

        # Check firm connectivity
        print(f"\nFirm connectivity:")
        for firm in firms.values():
            in_degree = sc_network.in_degree(firm)
            out_degree = sc_network.out_degree(firm)
            print(f"  Firm {firm.pid}: {in_degree} suppliers, {out_degree} clients")

        print("\n✓ Supply chain builder test completed successfully!")

    except Exception as e:
        print(f"\n✗ Test failed with error: {e}")
        import traceback
        traceback.print_exc()
        return False

    return True

if __name__ == "__main__":
    success = test_supply_chain_builder()
    if success:
        print("\n🎉 All tests passed!")
    else:
        print("\n❌ Test failed!")
        sys.exit(1)