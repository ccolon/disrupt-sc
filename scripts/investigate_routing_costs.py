"""
Investigate why alternative routes have such small cost increases in Ecuador.
"""

import sys
sys.path.insert(0, 'src')

from disruptsc.parameters import Parameters
from disruptsc.paths import PARAMETER_FOLDER
from disruptsc.model.model import Model
from disruptsc.model.utils.caching import load_cached_transport_network, load_cached_agent_data, load_cached_sc_network, load_cached_logistic_routes
import logging

# Setup logging
logging.basicConfig(level=logging.INFO)

# Load parameters
scope = "Ecuador"
parameters = Parameters.load_parameters(PARAMETER_FOLDER, scope)

# Load cached components
print("Loading cached data...")
transport_network, transport_edges, transport_nodes = load_cached_transport_network()
mrio, sector_table, firms, firm_table, households, household_table, countries = load_cached_agent_data()

sc_network, firms, households, countries = load_cached_sc_network()

# Ingest logistics data
print("\nIngesting logistics data...")
parameters.add_variability_to_basic_cost()
transport_network.ingest_logistic_data(parameters.logistics, parameters.time_resolution)

# Check some commercial links
print("\n" + "="*80)
print("INVESTIGATING ROUTE COSTS")
print("="*80)

# Find a country with multiple clients
country = countries['COL']
print(f"\nCountry: {country.id_str()}")
print(f"Cost profile: {country.cost_profile}")
print(f"USD per ton: {country.usd_per_ton}")

# Get some clients
clients = list(sc_network.out_edges(country))[:5]
print(f"\nChecking {len(clients)} commercial links...")

for _, buyer in clients:
    commercial_link = sc_network[country][buyer]['object']

    print(f"\n  Link to {buyer.id_str()}:")
    print(f"    - Main route cost: {commercial_link.route_cost_per_ton:.6f} USD/ton")
    print(f"    - Main route length: {commercial_link.route_length:.2f} km")

    if commercial_link.alternative_found:
        print(f"    - Alt route cost: {commercial_link.alternative_route_cost_per_ton:.6f} USD/ton")
        print(f"    - Alt route length: {commercial_link.alternative_route_length:.2f} km")

        cost_diff = commercial_link.alternative_route_cost_per_ton - commercial_link.route_cost_per_ton
        length_diff = commercial_link.alternative_route_length - commercial_link.route_length

        if commercial_link.route_cost_per_ton > 0:
            cost_pct = 100 * cost_diff / commercial_link.route_cost_per_ton
            print(f"    - Cost difference: {cost_diff:.6f} USD/ton ({cost_pct:.4f}%)")

        if commercial_link.route_length > 0:
            length_pct = 100 * length_diff / commercial_link.route_length
            print(f"    - Length difference: {length_diff:.2f} km ({length_pct:.2f}%)")
    else:
        print(f"    - No alternative route found yet")

# Check a firm example
print(f"\n{'-'*80}")
firm = list(firms.values())[0]
print(f"\nFirm: {firm.id_str()}")
print(f"Cost profile: {firm.cost_profile}")
print(f"USD per ton: {firm.usd_per_ton}")
print(f"Target margin: {firm.finance_manager.target_margin}")
print(f"Transport share: {firm.finance_manager.transport_share}")
print(f"EQ sales: {firm.finance_manager.eq_finance['sales']}")
print(f"EQ transport cost: {firm.finance_manager.eq_finance['costs']['transport']}")

# Get some clients
firm_clients = list(sc_network.out_edges(firm))[:3]
print(f"\nChecking {len(firm_clients)} commercial links...")

for _, buyer in firm_clients:
    commercial_link = sc_network[firm][buyer]['object']

    print(f"\n  Link to {buyer.id_str()}:")
    print(f"    - Main route cost: {commercial_link.route_cost_per_ton:.6f} USD/ton")
    print(f"    - Main route length: {commercial_link.route_length:.2f} km")

    if commercial_link.alternative_found:
        print(f"    - Alt route cost: {commercial_link.alternative_route_cost_per_ton:.6f} USD/ton")
        print(f"    - Alt route length: {commercial_link.alternative_route_length:.2f} km")

        cost_diff = commercial_link.alternative_route_cost_per_ton - commercial_link.route_cost_per_ton
        if commercial_link.route_cost_per_ton > 0:
            cost_pct = 100 * cost_diff / commercial_link.route_cost_per_ton
            print(f"    - Cost difference: {cost_diff:.6f} USD/ton ({cost_pct:.4f}%)")

            # Calculate what this means for price
            if firm.finance_manager.eq_finance['sales'] > 0:
                transport_cost_share = firm.finance_manager.eq_finance['costs']['transport'] / firm.finance_manager.eq_finance['sales']
                price_impact = transport_cost_share * cost_pct / 100
                print(f"    - Transport cost share of sales: {100*transport_cost_share:.4f}%")
                print(f"    - Estimated price impact: {100*price_impact:.6f}%")

print("\n" + "="*80)
