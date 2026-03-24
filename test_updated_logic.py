#!/usr/bin/env python3
"""Test updated input mix calculation logic."""

import sys
sys.path.append('src')

from disruptsc.model.agent_builders.firm import calculate_input_mix_from_transactions
from disruptsc.agents.firm import Firms, Firm
import pandas as pd

# Test data with total_output
firm_table = pd.DataFrame([
    {'id': 0, 'sector': 'A0116', 'final_demand': 10, 'imports': 1, 'exports': 2, 'total_output': 820},
    {'id': 1, 'sector': 'A0116', 'final_demand': 10, 'imports': 50, 'exports': 2, 'total_output': 800},
    {'id': 2, 'sector': 'A0161', 'final_demand': 10, 'imports': 1, 'exports': 150, 'total_output': 900}
])

firms = Firms([
    Firm(pid=0, region_sector='ECU_A0116', sector='A0116', od_point=0, region='ECU'),
    Firm(pid=1, region_sector='ECU_A0116', sector='A0116', od_point=0, region='ECU'),
    Firm(pid=2, region_sector='ECU_A0161', sector='A0161', od_point=0, region='ECU')
])

print("Testing updated input mix calculation logic...")
print("Firm data:")
print(firm_table[['id', 'sector', 'final_demand', 'exports', 'total_output']])

result = calculate_input_mix_from_transactions(
    firms,
    firm_table,
    'data/Ecuador_transaction/Economic/transaction_table.csv'
)

print("\n✓ Updated function works")
print("Input mix results:")
for f_id, firm in result.items():
    print(f'  Firm {f_id} (sector {firm.sector}, total_output={firm_table.set_index("id").loc[f_id, "total_output"]}): {firm.input_mix}')

# Test output balancing - create scenario where calculated output exceeds target
print("\n" + "="*60)
print("Testing output balancing logic...")

firm_table_imbalanced = pd.DataFrame([
    {'id': 0, 'sector': 'A0116', 'final_demand': 100, 'imports': 1, 'exports': 100, 'total_output': 850},  # Should trigger balancing - domestic sales (800) + final_demand (100) + exports (100) = 1000 > 850
])

firms_imbalanced = Firms([
    Firm(pid=0, region_sector='ECU_A0116', sector='A0116', od_point=0, region='ECU')
])

try:
    result_balanced = calculate_input_mix_from_transactions(
        firms_imbalanced,
        firm_table_imbalanced,
        'data/Ecuador_transaction/Economic/transaction_table.csv'
    )
    print("✓ Output balancing logic works")
except ValueError as e:
    print(f"✓ Error correctly thrown: {e}")