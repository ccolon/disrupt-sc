"""
Investigate why alternative routes have such small cost increases in Ecuador - Version 2.
Focus on finding routes that actually use real roads (not just virtual edges).
"""

import sys
sys.path.insert(0, 'src')

from disruptsc.parameters import Parameters
from disruptsc.paths import PARAMETER_FOLDER
from disruptsc.model.utils.caching import load_cached_transport_network, load_cached_sc_network
import logging

# Setup logging
logging.basicConfig(level=logging.WARNING)

# Load parameters
scope = "Ecuador"
parameters = Parameters.load_parameters(PARAMETER_FOLDER, scope)

# Load cached components
print("Loading cached data...")
transport_network, transport_edges, transport_nodes = load_cached_transport_network()
sc_network, firms, households, countries = load_cached_sc_network()

# Ingest logistics data
print("Ingesting logistics data...")
parameters.add_variability_to_basic_cost()
transport_network.ingest_logistic_data(parameters.logistics, parameters.time_resolution)

print("\n" + "="*80)
print("ANALYZING ROUTE COSTS")
print("="*80)

# Find links with non-zero, non-virtual routes
non_virtual_links = []
for supplier, buyer in sc_network.edges():
    commercial_link = sc_network[supplier][buyer]['object']

    # Check if route uses actual roads (not just virtual edge)
    if commercial_link.route_length > 5:  # More than just virtual edge
        non_virtual_links.append((supplier, buyer, commercial_link))

print(f"\nFound {len(non_virtual_links)} commercial links with real routes (>5km)")

# Analyze a few examples
print("\nAnalyzing first 10 examples:")
for supplier, buyer, link in non_virtual_links[:10]:
    print(f"\n  {supplier.id_str()} -> {buyer.id_str()}:")
    print(f"    Main route:")
    print(f"      - Cost: {link.route_cost_per_ton:.4f} USD/ton")
    print(f"      - Length: {link.route_length:.2f} km")
    print(f"      - Cost/km: {link.route_cost_per_ton/link.route_length if link.route_length > 0 else 0:.6f} USD/ton/km")

    # Check route edges
    route_edges = link.route.transport_edges
    edge_types = []
    for u, v in route_edges:
        edge_type = transport_network[u][v]['type']
        edge_types.append(edge_type)

    print(f"      - Edge types: {set(edge_types)}")

    if link.alternative_found:
        print(f"    Alternative route:")
        print(f"      - Cost: {link.alternative_route_cost_per_ton:.4f} USD/ton")
        print(f"      - Length: {link.alternative_route_length:.2f} km")
        print(f"      - Cost/km: {link.alternative_route_cost_per_ton/link.alternative_route_length if link.alternative_route_length > 0 else 0:.6f} USD/ton/km")

        cost_diff = link.alternative_route_cost_per_ton - link.route_cost_per_ton
        cost_pct = 100 * cost_diff / link.route_cost_per_ton if link.route_cost_per_ton > 0 else 0

        length_diff = link.alternative_route_length - link.route_length
        length_pct = 100 * length_diff / link.route_length if link.route_length > 0 else 0

        print(f"    Difference:")
        print(f"      - Cost: +{cost_diff:.4f} USD/ton ({cost_pct:+.2f}%)")
        print(f"      - Length: +{length_diff:.2f} km ({length_pct:+.2f}%)")

        # Check if agent is a firm and can calculate price impact
        if supplier.agent_type == 'firm':
            if supplier.finance_manager.eq_finance['sales'] > 0:
                # Calculate relative transport cost change
                relative_transport_cost_change = cost_diff / link.route_cost_per_ton if link.route_cost_per_ton > 0 else 0

                # Calculate price impact using firm's formula
                transport_cost_share = supplier.finance_manager.eq_finance['costs']['transport'] / supplier.finance_manager.eq_finance['sales']
                price_impact = transport_cost_share * relative_transport_cost_change

                print(f"    Price impact (if this were the only link):")
                print(f"      - Transport cost share: {100*transport_cost_share:.4f}%")
                print(f"      - Estimated price change: {100*price_impact:.6f}%")

print("\n" + "="*80)
