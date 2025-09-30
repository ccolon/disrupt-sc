"""
Supply Chain Network Builder Functions

This module contains functions for building supply chain networks from different data sources.
- build_network_from_transactions(): For transaction-based mode using predefined firm-firm relationships
- build_network_from_mrio(): For MRIO-based mode using algorithmic supplier selection
"""

import pandas as pd
import logging
from tqdm import tqdm
from disruptsc.network.sc_network import ScNetwork
from disruptsc.network.commercial_link import CommercialLink


def build_network_from_transactions(
    sc_network: ScNetwork,
    firms: "Firms",
    households: "Households",
    countries: "Countries",
    transaction_table_path: str,
    parameters: "Parameters"
) -> None:
    """
    Build supply chain network from predefined transaction data.

    This function creates firm-to-firm commercial links directly from transaction_table.csv,
    skipping the domestic supplier selection algorithms. International connections and
    household connections still use random selection.

    Args:
        sc_network: Empty ScNetwork to populate
        firms: Firm agents
        households: Household agents
        countries: Country agents
        transaction_table_path: Path to transaction_table.csv
        parameters: Model parameters
    """

    logging.info("Building supply chain network from transaction data...")

    # Load transaction data
    logging.info(f"Loading transaction data from {transaction_table_path}")
    transaction_df = pd.read_csv(transaction_table_path)

    # Validate transaction data structure
    required_columns = ['buyer_firm_id', 'seller_firm_id', 'transaction_value']
    missing_columns = [col for col in required_columns if col not in transaction_df.columns]
    if missing_columns:
        raise ValueError(f"Transaction table missing required columns: {missing_columns}")

    # Filter domestic firm-to-firm transactions
    domestic_transactions = transaction_df

    logging.info(f"Found {len(domestic_transactions)} domestic firm-to-firm transactions")

    # Create domestic firm-to-firm links from transaction data
    logging.info("[Firms-to-Firms] Creating domestic firm-to-firm commercial links...")

    created_links = 0
    skipped_links = 0

    for _, transaction in tqdm(domestic_transactions.iterrows(), total=len(domestic_transactions), desc="Creating commercial links"):
        buyer_id = int(transaction['buyer_firm_id'])
        seller_id = int(transaction['seller_firm_id'])
        transaction_value = transaction['transaction_value']

        # Validate that firms exist
        if buyer_id not in firms or seller_id not in firms:
            skipped_links += 1
            continue

        buyer_firm = firms[buyer_id]
        seller_firm = firms[seller_id]

        # Determine product info - use seller's region_sector to match MRIO format
        product_sector = seller_firm.region_sector

        # Create commercial link
        commercial_link = CommercialLink(
            pid=f"{seller_id}->{buyer_id}",
            supplier_id=seller_id,
            buyer_id=buyer_id,
            product=product_sector,
            product_type=firms[seller_id].sector_type,
            category="domestic_B2B"
        )

        # Add edge to network
        sc_network.add_edge(seller_firm, buyer_firm, object=commercial_link, weight=transaction_value)

        # Update firm client/supplier relationships
        if buyer_id not in seller_firm.clients:
            seller_firm.clients[buyer_id] = {
                'sector': product_sector,
                'share': 0,  # Will be calculated later
                'transport_share': 0
            }

        if seller_id not in buyer_firm.suppliers:
            buyer_firm.suppliers[seller_id] = {
                'sector': product_sector,  # Now using region_sector format (e.g., "ECU_A0116")
                'weight': 1.0,  # Default weight for transaction-based mode
                'share': 0,  # Will be calculated later
                'transport_share': 0,
                'satisfaction': 1  # Default satisfaction
            }

        created_links += 1

    logging.info(f"Created {created_links} commercial links, skipped {skipped_links}")

    logging.info('[Countries-to-Firms] Firms selecting countries as importer...')
    for firm in tqdm(firms.values(), total=len(firms)):
        for input, coefficient in firm.input_mix.items():
            if 'imports' in input:
                country_name = input.split('_')[0]
                supplying_country = countries[country_name]
                commercial_link = CommercialLink(
                           pid=str(country_name) + "->" + str(firm.pid),
                           product=input,
                           product_type="imports",
                           category="import",
                           origin_node=supplying_country.od_point,
                           destination_node=firm.od_point,
                           supplier_id=country_name,
                           buyer_id=firm.pid)
                sc_network.add_edge(supplying_country, firm, object=commercial_link)
                commercial_link.determine_transportation_mode(parameters.logistics['sector_types_to_shipment_method'])
                # Associate a weight, which includes the I/O technical coefficient
                sc_network[supplying_country][firm]['weight'] = coefficient
                # The firm saves the name of the supplier, its sector, its weight (without I/O technical coefficient)
                firm.suppliers[country_name] = {'sector': input, 'weight': 1, "satisfaction": 1}
                # The supplier saves the name of the client, its sector, and distance to it.
                # The share of sales cannot be calculated now
                distance = firm.distance_to_other(supplying_country)
                supplying_country.clients[firm.pid] = {'sector': firm.sector, 'share': 0, 'transport_share': 0,
                                                       'distance': distance}

    # Now handle households selecting domestic firms (unchanged logic)
    logging.info('[Firms-to-Households] selecting domestic retailers...')
    for household in tqdm(households.values(), total=len(households)):
        household.select_suppliers(
            sc_network, firms, countries,
            parameters.weight_localization_household,
            parameters.nb_suppliers_per_input,
            parameters.logistics['sector_types_to_shipment_method'],
            import_label="imports"  # Default for transaction mode
        )

    # Handle countries selecting domestic firms for exports (transaction mode)
    logging.info('[Firms-to-Countries] Countries selecting domestic firms for exports (transaction mode)')
    from disruptsc.agents.country import calculate_suppliers_per_sector_transaction

    # Calculate supplier counts using transaction mode logic (10% of firms per sector)
    suppliers_per_sector = calculate_suppliers_per_sector_transaction(firms, export_share=0.1)

    for country in tqdm(countries.values(), total=len(countries)):
        country.select_suppliers(sc_network, firms, countries, suppliers_per_sector,
                                 parameters.logistics['sector_types_to_shipment_method'])

    logging.info(f'Supply chain network created with {sc_network.number_of_edges()} total commercial links')


def build_network_from_mrio(
    sc_network: ScNetwork,
    firms: "Firms",
    households: "Households",
    countries: "Countries",
    mrio: "Mrio",
    sector_table: pd.DataFrame,
    parameters: "Parameters",
    transport_network: "TransportNetwork"
) -> None:
    """
    Build supply chain network using MRIO-based algorithmic supplier selection.

    This function implements the original MRIO-based network building logic,
    where agents select their suppliers using algorithms based on localization
    weights and sector compatibility.

    Args:
        sc_network: Empty ScNetwork to populate
        firms: Firm agents
        households: Household agents
        countries: Country agents
        mrio: Multi-Regional Input-Output data
        sector_table: Sector classification table
        transaction_table: Transaction data (for supplier-buyer network mode)
        parameters: Model parameters
        transport_network: Transport network for routing
    """

    logging.info("Building supply chain network using MRIO-based supplier selection...")

    # Use existing MRIO-based network building
    logging.info('Households are selecting their retailers (domestic B2C flows and import B2C flows)')
    for household in tqdm(households.values(), total=len(households)):
        household.select_suppliers(sc_network, firms, countries,
                                   parameters.weight_localization_household,
                                   parameters.nb_suppliers_per_input,
                                   parameters.logistics['sector_types_to_shipment_method'],
                                   import_label=mrio.import_label,
                                   transport_network=transport_network)

    logging.info('Exporters are being selected by purchasing countries (export B2B flows)')
    logging.info('and trading countries are being connected (transit flows)')
    from disruptsc.agents.country import calculate_suppliers_per_sector_mrio

    # Calculate supplier counts using MRIO sector table
    suppliers_per_sector = calculate_suppliers_per_sector_mrio(firms, sector_table)

    for country in tqdm(countries.values(), total=len(countries)):
        country.select_suppliers(sc_network, firms, countries, suppliers_per_sector,
                                 parameters.logistics['sector_types_to_shipment_method'])

    logging.info(
        f'Firms are selecting their domestic and international suppliers (import B2B flows) '
        f'(domestic B2B flows). Weight localisation is {parameters.weight_localization_firm}'
    )

    for firm in tqdm(firms.values(), total=len(firms)):
        firm.select_suppliers(sc_network, firms, countries,
                              parameters.nb_suppliers_per_input,
                              parameters.weight_localization_firm,
                              parameters.logistics['sector_types_to_shipment_method'],
                              import_label=mrio.import_label,
                              transport_network=transport_network)

    unconnected_nodes = sc_network.identify_disconnected_nodes(firms, countries, households)
    if len(unconnected_nodes) > 0:
        for agent_type, unconnected_node_ids in unconnected_nodes.items():
            logging.warning(f"{len(unconnected_node_ids)} {agent_type} are not in the sc network: "
                            f"they have no suppliers, no clients. We remove them.")
            if agent_type == "firms":
                for unconnected_firm_id in unconnected_node_ids:
                    # sc_network.add_node(firms[unconnected_firm_id])
                    del firms[unconnected_firm_id]
            if agent_type == "countries":
                for unconnected_country_id in unconnected_node_ids:
                    del countries[unconnected_country_id]
            if agent_type == "households":
                for unconnected_household_id in unconnected_node_ids:
                    del households[unconnected_household_id]

    # Iteratively remove firms without clients until convergence
    total_removed = 0
    max_iterations = 10
    for iteration in range(max_iterations):
        removed_count = sc_network.remove_useless_commercial_links()
        if removed_count == 0:
            logging.info(f"Converged after {iteration + 1} iterations")
            break
        total_removed += removed_count

        # Remove firms from model collections that were removed from sc_network
        current_firm_pids_in_network = {node.pid for node in sc_network.nodes()
                                        if hasattr(node, 'agent_type') and node.agent_type == "firm"}
        firms_to_remove = set(firms.keys()) - current_firm_pids_in_network
        for firm_id in firms_to_remove:
            del firms[firm_id]
    else:
        logging.warning(f"Reached maximum iterations ({max_iterations}) without convergence")

    logging.info(f"Total firms removed in cleanup: {total_removed}")

    # Final validation: Check for any remaining firms without clients
    remaining_firms_without_clients = sc_network.identify_firms_without_clients()
    if remaining_firms_without_clients:
        logging.warning(
            f"Warning: {len(remaining_firms_without_clients)} firms still without clients after cleanup")
    else:
        logging.info("Cleanup successful: All remaining firms have clients")

    logging.info(f'Nb of commercial links: {sc_network.number_of_edges()}')

    # connected_countries = [node.pid for node in sc_network.nodes if node.agent_type == "country"]
    # unconnected_countries = set(countries) - set(connected_countries)
    # for unconnected_country in unconnected_countries:
    #     logging.info(f"Country {unconnected_country} is not connected, removing it")
    #     del countries[unconnected_country]

    logging.info('The nodes and edges of the supplier--buyer have been created')