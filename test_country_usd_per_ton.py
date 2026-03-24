#!/usr/bin/env python3
"""Test that country usd_per_ton values are correctly extracted from imports.csv."""

import sys
sys.path.append('src')

from disruptsc.model.agent_builders.country import _extract_trade_data_from_csv

def test_country_usd_per_ton():
    """Test extraction of usd_per_ton from imports.csv."""

    print("Testing country usd_per_ton extraction from imports.csv...")

    # Test the CSV extraction function
    import_table, export_table, buying_countries, selling_countries, country_usd_per_ton = _extract_trade_data_from_csv(
        exports_filepath='data/Ecuador_transaction/Economic/exports.csv',
        imports_filepath='data/Ecuador_transaction/Economic/imports.csv',
        time_resolution='day',
        target_units='USD',
        input_units='mUSD'
    )

    print(f"Countries found: {list(set(buying_countries) | set(selling_countries))}")
    print(f"Country usd_per_ton values: {country_usd_per_ton}")

    # Verify the expected values
    expected_values = {
        'USA': (1000 + 1200 + 800 + 1500) / 4,  # Average across sectors
        'COL': (1000 + 800) / 2,  # Average across sectors
        'PER': (1200 + 1500) / 2   # Average across sectors
    }

    print(f"Expected values: {expected_values}")

    # Check values
    all_correct = True
    for country, expected_value in expected_values.items():
        if country in country_usd_per_ton:
            actual_value = country_usd_per_ton[country]
            if abs(actual_value - expected_value) < 0.01:
                print(f"✓ {country}: {actual_value} (matches expected {expected_value})")
            else:
                print(f"✗ {country}: {actual_value} (expected {expected_value})")
                all_correct = False
        else:
            print(f"✗ {country}: Missing from extracted data")
            all_correct = False

    if all_correct:
        print("\n✓ All usd_per_ton values extracted correctly from imports.csv!")
        return True
    else:
        print("\n✗ Some usd_per_ton values are incorrect!")
        return False

if __name__ == "__main__":
    success = test_country_usd_per_ton()
    if success:
        print("\n🎉 Test passed!")
    else:
        print("\n❌ Test failed!")
        sys.exit(1)