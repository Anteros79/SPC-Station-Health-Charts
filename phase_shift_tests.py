import json
import sys
from datetime import datetime, timedelta
from spc_processor import process_data, parse_csv  # Assuming spc_processor is in same dir

# Helper to generate CSV string
def generate_csv(station, measure, dates, values):
    lines = [f'station,measure,date,value']
    for date_str, value in zip(dates, values):
        lines.append(f'{station},"{measure}",{date_str},{value}')
    return '\n'.join(lines)

# Baseline: 20 stable points around CL=50, MR=5 exactly (alternating ±2.5)
BASELINE_START = datetime(2023, 1, 1)
baseline_dates = [(BASELINE_START + timedelta(days=i)).strftime('%Y-%m-%d') for i in range(20)]
baseline_values = [50 + ((-1)**i * 2.5) for i in range(20)]  # 47.5,52.5,47.5,... MR=5

# Helper for normal small variation
def normal_values(n):
    return [50 + ((-1)**i * 2.5) for i in range(n)]

# Test 1: Rule 1 - Point beyond limits
def test_rule1():
    print("=== Test 1: Rule 1 (Point Beyond Limits) ===")
    monitoring_dates = [(BASELINE_START + timedelta(days=20 + i)).strftime('%Y-%m-%d') for i in range(10)]
    monitoring_values = normal_values(5) + [70] + normal_values(4)  # Normal, outlier, normal
    all_dates = baseline_dates + monitoring_dates
    all_values = baseline_values + monitoring_values
    csv_text = generate_csv('TEST', 'Test Measure', all_dates, all_values)
    result = process_data(csv_text)
    print(json.dumps(result, indent=2))
    print("\nExpected: 2 phases, shift at index 25 (outlier), x_signal_count=1")

# Test 2: Rule 2 - 2 of 3 beyond 2σ same side
def test_rule2():
    print("=== Test 2: Modified Rule 2 (2-of-3 >2σ same side) ===")
    monitoring_dates = [(BASELINE_START + timedelta(days=20 + i)).strftime('%Y-%m-%d') for i in range(10)]
    # pts 22-24 total: normal 0,1; 2=60,3=59,4=51 (2 upper >58.86)
    monitoring_values = normal_values(2) + [60, 59, 51] + normal_values(5)
    all_dates = baseline_dates + monitoring_dates
    all_values = baseline_values + monitoring_values
    csv_text = generate_csv('TEST', 'Test Measure', all_dates, all_values)
    result = process_data(csv_text)
    print(json.dumps(result, indent=2))
    print("\nExpected: 2 phases, shift around index 22-23, x_signal_count=0 (no limit violation)")

# Test 3: Rule 4 - 7 consecutive above CL
def test_rule4():
    print("=== Test 3: Rule 4 (7 Consecutive Above CL) ===")
    monitoring_dates = [(BASELINE_START + timedelta(days=20 + i)).strftime('%Y-%m-%d') for i in range(10)]
    monitoring_values = [55] * 10  # All above 50
    all_dates = baseline_dates + monitoring_dates
    all_values = baseline_values + monitoring_values
    csv_text = generate_csv('TEST', 'Test Measure', all_dates, all_values)
    result = process_data(csv_text)
    print(json.dumps(result, indent=2))
    print("\nExpected: 2 phases, shift at start of run (index ~20), x_signal_count=0")

# Test 4a: Combination Rule 4 then Rule 1
def test_comb1():
    print("=== Test 4a: Combination Rule 4 then Rule 1 ===")
    monitoring_dates = [(BASELINE_START + timedelta(days=20 + i)).strftime('%Y-%m-%d') for i in range(12)]
    monitoring_values = [55] * 7 + normal_values(2) + [70] + normal_values(3)  # Run 7 above, normal, outlier
    all_dates = baseline_dates + monitoring_dates
    all_values = baseline_values + monitoring_values
    csv_text = generate_csv('TEST', 'Test Measure', all_dates, all_values)
    result = process_data(csv_text)
    print(json.dumps(result, indent=2))
    print("\nExpected: 2 phases (Rule 4 first), then possibly 3rd for outlier, but check signal_count")

# Test 4b: No shift
def test_no_shift():
    print("=== Test 4b: No Shift (Negative) ===")
    monitoring_dates = [(BASELINE_START + timedelta(days=20 + i)).strftime('%Y-%m-%d') for i in range(10)]
    monitoring_values = normal_values(10)  # All normal variation
    all_dates = baseline_dates + monitoring_dates
    all_values = baseline_values + monitoring_values
    csv_text = generate_csv('TEST', 'Test Measure', all_dates, all_values)
    result = process_data(csv_text)
    print(json.dumps(result, indent=2))
    print("\nExpected: 1 phase, stable=true")

# Test 5: Edge - Insufficient data
def test_edge_insufficient():
    print("=== Test 5: Edge - <20 points ===")
    short_dates = [(BASELINE_START + timedelta(days=i)).strftime('%Y-%m-%d') for i in range(10)]
    short_values = normal_values(10)
    csv_text = generate_csv('TEST', 'Test Measure', short_dates, short_values)
    result = process_data(csv_text)
    print(json.dumps(result, indent=2))
    print("\nExpected: 1 phase, limits from all data")

# Run all tests
if __name__ == '__main__':
    test_rule1()
    test_rule2()
    test_rule4()
    test_comb1()
    test_no_shift()
    test_edge_insufficient()
    print("All tests completed.")
