"""
Investigate Ecuador routing - check the actual cached logistic routes from the simulation.
"""

import sys
sys.path.insert(0, 'src')

from disruptsc.parameters import Parameters
from disruptsc.paths import PARAMETER_FOLDER
from disruptsc.model.utils.caching import load_cached_logistic_routes
import logging

# Setup logging
logging.basicConfig(level=logging.WARNING)

# Load parameters
scope = "Ecuador"
parameters = Parameters.load_parameters(PARAMETER_FOLDER, scope)

# Load cached logistic routes (the ones actually used in simulation)
print("Loading cached logistic routes...")
sc_network, transport_network, commercial_link_table, firms, households, countries = load_cached_logistic_routes()

print("\n" + "="*80)
print("ANALYZING CACHED LOGISTIC ROUTES")
print("="*80)

# Find links with non-zero costs
non_zero_cost_links = []
zero_cost_links = []
long_routes = []

for supplier, buyer in sc_network.edges():
    commercial_link = sc_network[supplier][buyer]['object']

    if commercial_link.route_cost_per_ton > 0:
        non_zero_cost_links.append((supplier, buyer, commercial_link))

    if commercial_link.route_cost_per_ton == 0:
        zero_cost_links.append((supplier, buyer, commercial_link))

    if commercial_link.route_length > 5:
        long_routes.append((supplier, buyer, commercial_link))

print(f"\nRoute statistics:")
print(f"  - Total links: {len(list(sc_network.edges()))}")
print(f"  - Links with cost > 0: {len(non_zero_cost_links)}")
print(f"  - Links with cost = 0: {len(zero_cost_links)}")
print(f"  - Links with length > 5km: {len(long_routes)}")

if len(non_zero_cost_links) > 0:
    print(f"\n{'-'*80}")
    print("Sample links with NON-ZERO cost:")
    for supplier, buyer, link in non_zero_cost_links[:10]:
        print(f"\n  {supplier.id_str()} -> {buyer.id_str()}:")
        print(f"    - Cost: {link.route_cost_per_ton:.6f} USD/ton")
        print(f"    - Length: {link.route_length:.2f} km")

        if link.alternative_found:
            print(f"    - Alt cost: {link.alternative_route_cost_per_ton:.6f} USD/ton")
            print(f"    - Alt length: {link.alternative_route_length:.2f} km")

            cost_diff = link.alternative_route_cost_per_ton - link.route_cost_per_ton
            if link.route_cost_per_ton > 0:
                cost_pct = 100 * cost_diff / link.route_cost_per_ton
                print(f"    - Cost increase: {cost_pct:.4f}%")

# Check what the route actually looks like
if len(non_zero_cost_links) > 0:
    supplier, buyer, link = non_zero_cost_links[0]
    print(f"\n{'-'*80}")
    print(f"Detailed inspection of: {supplier.id_str()} -> {buyer.id_str()}")
    print(f"\nMain route edges:")
    for u, v in link.route.transport_edges:
        edge_data = transport_network[u][v]
        print(f"  {u} -> {v}:")
        print(f"    - Type: {edge_data['type']}")
        print(f"    - Length: {edge_data['km']:.2f} km")

        # Check for cost_per_ton attributes
        cost_attrs = [key for key in edge_data.keys() if 'cost_per_ton' in key]
        if cost_attrs:
            for attr in cost_attrs[:3]:  # Show first 3 cost attributes
                print(f"    - {attr}: {edge_data[attr]:.6f}")

print("\n" + "="*80)
