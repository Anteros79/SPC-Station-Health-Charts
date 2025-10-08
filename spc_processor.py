"""
Statistical Process Control (SPC) Data Processor
Converts CSV data to SPC charts with phase detection
"""

import csv
import json
import math
from datetime import datetime
from typing import List, Dict, Any, Tuple
from io import StringIO


def parse_csv(csv_text: str) -> List[Dict[str, Any]]:
    """Parse CSV text into data points"""
    reader = csv.DictReader(StringIO(csv_text))
    data_points = []
    
    for row in reader:
        try:
            print(f"Debug SPC - Row: {row}")
            print(f"Debug SPC - Value string: '{row['value']}'")
            value_float = float(row['value'])
            print(f"Debug SPC - Value float: {value_float}")
            
            data_points.append({
                'station': row['station'].strip(),
                'measure': row['measure'].strip(),
                'date': row['date'].strip(),
                'value': value_float
            })
        except (ValueError, KeyError) as e:
            print(f"Warning: Skipping invalid row: {e}")
            print(f"Row data: {row}")
            continue
    
    print(f"Debug SPC - Total data points created: {len(data_points)}")
    if len(data_points) == 0:
        print("ERROR: No valid data points found!")
    return data_points


def calculate_initial_limits(values: List[float]) -> Tuple[float, float]:
    """Calculate center line and moving range bar"""
    if len(values) == 0:
        return 0.0, 0.0
    if len(values) == 1:
        return values[0], 0.0
    
    cl = sum(values) / len(values)
    
    moving_ranges = [abs(values[i] - values[i-1]) for i in range(1, len(values))]
    mR_bar = sum(moving_ranges) / len(moving_ranges) if moving_ranges else 0.0
    
    return cl, mR_bar


def calculate_standard_deviation_odds(value: float, center_line: float, standard_deviation: float) -> float:
    """
    Calculate odds of observing a point as extreme as current value.
    Returns odds in format suitable for "1 in X" display.
    """
    if standard_deviation == 0 or standard_deviation < 0.0001:
        return 1.0
    
    z_score = abs(value - center_line) / standard_deviation
    
    def normal_cdf(x):
        return 0.5 * (1 + math.erf(x / math.sqrt(2)))
    
    # Two-tailed probability: P(|Z| >= z_score)
    probability_extreme = 2 * (1 - normal_cdf(z_score))
    
    if probability_extreme <= 0.0001:
        return 10000.0  # Cap at 1 in 10,000
    
    odds = 1 / probability_extreme
    return round(odds, 0)


def find_phase_end(values: List[float], cl: float, ucl: float, lcl: float) -> int:
    """Find where phase ends using Wheeler's Rules
    
    Wheeler's Rules for detecting special causes:
    Rule #1: Point beyond control limits (outside UCL/LCL)
    Rule #4: 7 consecutive points on one side of centerline
    
    Returns index where current phase should end (signal detected)
    """
    RUN_LENGTH = 7
    
    if len(values) == 0:
        return 0
    
    consecutive_above = 0
    consecutive_below = 0
    
    for i, value in enumerate(values):
        # RULE #1: Point outside control limits
        if value > ucl or value < lcl:
            # Signal! Phase ends at the point BEFORE this outlier
            # The outlier starts the new phase
            return max(0, i - 1)
        
        # RULE #4: Track 7-point runs
        if value > cl:
            consecutive_above += 1
            consecutive_below = 0
        elif value < cl:
            consecutive_below += 1
            consecutive_above = 0
        else:
            # Point exactly on centerline - doesn't reset counter
            pass
        
        # Signal detected: 7 consecutive on one side
        if consecutive_above >= RUN_LENGTH or consecutive_below >= RUN_LENGTH:
            # Phase ends at the point BEFORE the run started
            return max(0, i - RUN_LENGTH)
    
    # No signal found - entire dataset is one phase
    return len(values) - 1


def detect_phases(data_points: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Detect phases and recalculate control limits when process shifts occur
    
    Proper SPC phase detection:
    1. Start with baseline data (minimum 20 points)
    2. Calculate limits from ONLY that baseline
    3. Extend phase forward, watching for 8-point run signal
    4. When signal detected, start new phase at signal point
    """
    if len(data_points) < 2:
        return {
            'points': data_points,
            'phases': []
        }
    
    # Sort by date (properly parse dates for correct chronological order)
    def parse_date(date_str):
        try:
            # Handle M/D/YYYY format
            return datetime.strptime(date_str.strip(), '%m/%d/%Y')
        except ValueError:
            try:
                # Handle YYYY-MM-DD format
                return datetime.strptime(date_str.strip(), '%Y-%m-%d')
            except ValueError:
                # Fallback to string comparison if parsing fails
                return date_str
    
    sorted_data = sorted(data_points, key=lambda x: parse_date(x['date']))
    values = [p['value'] for p in sorted_data]
    
    phases = []
    augmented_points = [dict(p) for p in sorted_data]
    
    current_start = 0
    phase_number = 1
    MIN_BASELINE = 20  # Minimum points to establish a baseline
    
    while current_start < len(values):
        # Get baseline data for this phase (at least 20 points, or whatever's left)
        baseline_end = min(current_start + MIN_BASELINE, len(values))
        baseline_values = values[current_start:baseline_end]
        
        if not baseline_values:
            break
        
        # Calculate limits from baseline ONLY
        cl, mR_bar = calculate_initial_limits(baseline_values)
        ucl = cl + 2.66 * mR_bar
        lcl = max(0, cl - 2.66 * mR_bar)
        
        # Now look for signal in data AFTER baseline using Wheeler's Rules
        remaining_values = values[baseline_end:]
        signal_offset = find_phase_end(remaining_values, cl, ucl, lcl)
        
        # Phase ends at baseline + signal offset
        phase_end = baseline_end + signal_offset
        
        # Use actual phase data to calculate final limits
        phase_values = values[current_start:phase_end + 1]
        cl, mR_bar = calculate_initial_limits(phase_values)
        ucl = cl + 2.66 * mR_bar  # NPL: 2.66 sigma
        lcl = max(0, cl - 2.66 * mR_bar)
        
        phases.append({
            'startIndex': current_start,
            'endIndex': phase_end,
            'cl': round(cl, 2),
            'ucl': round(ucl, 2),
            'lcl': round(lcl, 2),
            'phaseNumber': phase_number
        })
        
        # Augment points with this phase's limits and odds calculation
        for i in range(current_start, min(phase_end + 1, len(augmented_points))):
            augmented_points[i]['cl'] = round(cl, 2)
            augmented_points[i]['ucl'] = round(ucl, 2)
            augmented_points[i]['lcl'] = round(lcl, 2)
            
            # Calculate standard deviation for odds calculation
            # Using mR_bar as an approximation of standard deviation
            # (mR_bar / 1.128 is approximately equal to standard deviation for normal distribution)
            std_dev = mR_bar / 1.128 if mR_bar > 0 else 0.001  # Avoid division by zero
            
            # Calculate odds for this data point
            odds = calculate_standard_deviation_odds(augmented_points[i]['value'], cl, std_dev)
            augmented_points[i]['odds'] = odds
        
        current_start = phase_end + 1
        phase_number += 1
    
    return {
        'points': augmented_points,
        'phases': phases
    }


def generate_moving_range_data(individuals_data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Generate Moving Range data from Individuals data
    
    Moving Range = |X[i] - X[i-1]|
    Used to monitor process variation
    """
    sorted_data = sorted(individuals_data, key=lambda x: x['date'])
    mr_data = []
    
    for i in range(1, len(sorted_data)):
        mr_value = abs(sorted_data[i]['value'] - sorted_data[i-1]['value'])
        mr_data.append({
            'station': sorted_data[i]['station'],
            'measure': sorted_data[i]['measure'] + ' (Moving Range)',
            'date': sorted_data[i]['date'],
            'value': mr_value
        })
    
    return mr_data


def apply_phases_to_mr(mr_points: List[Dict[str, Any]], x_phases: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Apply X chart's phase boundaries to Moving Range data.
    This ensures X and mR charts have identical phase structure.
    
    Wheeler's Methodology:
    - Phases are determined by the Individuals (X) chart
    - mR chart uses the same phase boundaries
    - mR limits are calculated within each phase
    """
    if not mr_points or not x_phases:
        return {'points': mr_points, 'phases': []}
    
    # Sort mR points by date
    def parse_date(date_str):
        try:
            return datetime.strptime(date_str.strip(), '%m/%d/%Y')
        except ValueError:
            try:
                return datetime.strptime(date_str.strip(), '%Y-%m-%d')
            except ValueError:
                return date_str
    
    sorted_mr = sorted(mr_points, key=lambda x: parse_date(x['date']))
    augmented_points = [dict(p) for p in sorted_mr]
    
    # Apply each phase from X chart to mR data
    mr_phases = []
    for phase in x_phases:
        # Get mR values within this phase's index range
        # Note: mR has one fewer point than X (since mR[i] = |X[i] - X[i-1]|)
        phase_start = max(0, phase['startIndex'] - 1)  # Adjust for mR offset
        phase_end = min(phase['endIndex'] - 1, len(sorted_mr) - 1)
        
        if phase_start >= len(sorted_mr):
            continue
            
        phase_values = [sorted_mr[i]['value'] for i in range(phase_start, phase_end + 1)]
        
        if not phase_values:
            continue
        
        # Calculate mR limits for this phase
        mR_bar = sum(phase_values) / len(phase_values)
        ucl_mr = mR_bar * 3.268  # mR chart UCL
        lcl_mr = 0  # mR chart LCL is always 0
        
        mr_phases.append({
            'startIndex': phase_start,
            'endIndex': phase_end,
            'cl': round(mR_bar, 2),
            'ucl': round(ucl_mr, 2),
            'lcl': 0,
            'phaseNumber': phase['phaseNumber']
        })
        
        # Augment mR points with phase limits and odds
        for i in range(phase_start, min(phase_end + 1, len(augmented_points))):
            augmented_points[i]['cl'] = round(mR_bar, 2)
            augmented_points[i]['ucl'] = round(ucl_mr, 2)
            augmented_points[i]['lcl'] = 0
            
            # Calculate odds for mR point
            std_dev = mR_bar / 1.128 if mR_bar > 0 else 0.001
            odds = calculate_standard_deviation_odds(augmented_points[i]['value'], mR_bar, std_dev)
            augmented_points[i]['odds'] = odds
    
    return {
        'points': augmented_points,
        'phases': mr_phases
    }


def detect_xmr_signal_type(x_data: Dict, mr_data: Dict) -> Dict[str, Any]:
    """
    Determine which chart(s) are signaling for coordinated XmR analysis.
    Wheeler's approach: Both charts share identical phase structure.
    """
    x_phases = x_data.get('phases', [])
    mr_phases = mr_data.get('phases', [])
    
    # Both charts MUST have identical phase counts
    x_signals = len(x_phases) - 1  # Subtract baseline
    mr_signals = len(mr_phases) - 1
    
    # Verify phase synchronization
    phase_synchronized = (x_signals == mr_signals)
    
    # Add point-specific signal detection
    x_points = x_data.get('points', [])
    mr_points = mr_data.get('points', [])
    
    # Check each point to see if it's signaling in both charts
    for i, x_point in enumerate(x_points):
        if i < len(mr_points):
            mr_point = mr_points[i]
            
            # Check if this specific point is signaling in X chart
            x_signal = x_point['value'] > x_point['ucl'] or x_point['value'] < x_point['lcl']
            
            # Check if this specific point is signaling in mR chart
            mr_signal = mr_point['value'] > mr_point['ucl'] or mr_point['value'] < mr_point['lcl']
            
            # Add point-specific signal information
            x_point['x_signal'] = x_signal
            x_point['mr_signal'] = mr_signal
            x_point['both_signaling'] = x_signal and mr_signal
            x_point['x_only_signal'] = x_signal and not mr_signal
            x_point['mr_only_signal'] = mr_signal and not x_signal
            
            mr_point['x_signal'] = x_signal
            mr_point['mr_signal'] = mr_signal
            mr_point['both_signaling'] = x_signal and mr_signal
            mr_point['x_only_signal'] = x_signal and not mr_signal
            mr_point['mr_only_signal'] = mr_signal and not x_signal
    
    signal_info = {
        'x_signal_count': x_signals,
        'mr_signal_count': mr_signals,
        'both_signaling': x_signals > 0 and mr_signals > 0,  # Global status
        'x_only': x_signals > 0 and mr_signals == 0,
        'mr_only': mr_signals > 0 and x_signals == 0,
        'stable': x_signals == 0 and mr_signals == 0,
        'phase_synchronized': phase_synchronized
    }
    
    return signal_info


def generate_histogram_data(individuals_data: List[Dict[str, Any]], bins: int = 20) -> Dict[str, Any]:
    """
    Generate histogram data for distribution visualization (belly chart).
    Shows how data is distributed to assess normality.
    """
    if not individuals_data:
        return {'bins': [], 'frequencies': [], 'normal_curve': []}
    
    values = [p['value'] for p in individuals_data]
    mean = sum(values) / len(values)
    
    # Calculate standard deviation
    variance = sum((x - mean) ** 2 for x in values) / len(values)
    std_dev = math.sqrt(variance)
    
    # Create histogram bins
    min_val = min(values)
    max_val = max(values)
    bin_width = (max_val - min_val) / bins
    
    histogram_bins = []
    frequencies = []
    
    for i in range(bins):
        bin_start = min_val + i * bin_width
        bin_end = bin_start + bin_width
        bin_center = (bin_start + bin_end) / 2
        
        # Count values in this bin
        count = sum(1 for v in values if bin_start <= v < bin_end)
        
        histogram_bins.append(round(bin_center, 2))
        frequencies.append(count)
    
    # Generate normal distribution curve for overlay
    normal_curve = []
    for bin_center in histogram_bins:
        z = (bin_center - mean) / std_dev if std_dev > 0 else 0
        # Normal PDF scaled to match histogram
        pdf_value = (1 / (std_dev * math.sqrt(2 * math.pi))) * math.exp(-0.5 * z ** 2)
        # Scale to histogram total
        scaled_value = pdf_value * len(values) * bin_width
        normal_curve.append(round(scaled_value, 2))
    
    return {
        'bins': histogram_bins,
        'frequencies': frequencies,
        'normal_curve': normal_curve,
        'mean': round(mean, 2),
        'std_dev': round(std_dev, 2),
        'total_points': len(values)
    }


def process_data(csv_text: str) -> Dict[str, Any]:
    """Process CSV data and return structured chart data
    
    Generates both X chart (Individuals) and mR chart (Moving Range)
    following Wheeler's XmR methodology
    """
    data_points = parse_csv(csv_text)
    
    if not data_points:
        return {'error': 'No valid data points found'}
    
    # Group by station and measure
    grouped = {}
    for point in data_points:
        station = point['station']
        measure = point['measure']
        
        if station not in grouped:
            grouped[station] = {}
        if measure not in grouped[station]:
            grouped[station][measure] = []
        
        grouped[station][measure].append(point)
    
    # Process each station/measure combination
    # Generate BOTH X chart and mR chart
    chart_data = {}
    for station, measures in grouped.items():
        chart_data[station] = {}
        for measure, points in measures.items():
            # Step 1: Detect phases using X chart (Individuals) ONLY
            x_chart_data = detect_phases(points)
            
            # Step 2: Generate mR data from same points
            mr_points = generate_moving_range_data(points)
            mr_chart_data = None
            
            if mr_points:
                # Step 3: Apply X chart's phase boundaries to mR chart
                # This ensures both charts have IDENTICAL phase structure
                mr_chart_data = apply_phases_to_mr(mr_points, x_chart_data['phases'])
                
                # Step 4: Detect signal coordination
                signal_info = detect_xmr_signal_type(x_chart_data, mr_chart_data)
                x_chart_data['signal_info'] = signal_info
                mr_chart_data['signal_info'] = signal_info
            
            # Step 5: Store X and mR charts
            chart_data[station][measure] = x_chart_data
            if mr_chart_data:
                mr_measure = measure + ' (Moving Range)'
                chart_data[station][mr_measure] = mr_chart_data
            
            # Step 6: Generate distribution chart LAST
            histogram_data = generate_histogram_data(points)
            histogram_measure = measure + ' (Distribution)'
            chart_data[station][histogram_measure] = {
                'histogram': histogram_data,
                'type': 'distribution'
            }
    
    return {
        'success': True,
        'chartData': chart_data,
        'stations': list(grouped.keys())
    }


def generate_demo_data() -> str:
    """Generate demo CSV data"""
    from datetime import date, timedelta
    import random
    
    stations = ['JFK', 'LAX', 'ORD']
    measures = ['Turnaround Time', 'Baggage Handling Errors', 'Gate Availability Delay']
    
    lines = ['station,measure,date,value']
    today = date.today()
    num_days = 60
    
    for i in range(num_days, 0, -1):
        current_date = today - timedelta(days=i)
        date_str = current_date.isoformat()
        
        for station in stations:
            for measure in measures:
                # Introduce shift for JFK Turnaround Time
                if station == 'JFK' and measure == 'Turnaround Time':
                    if i > num_days / 2:
                        value = 45 + (random.random() - 0.5) * 10
                    else:
                        value = 60 + (random.random() - 0.5) * 12
                elif measure == 'Baggage Handling Errors':
                    value = 5 + (random.random() - 0.5) * 4
                else:
                    value = 15 + (random.random() - 0.5) * 8
                
                value = max(0, round(value, 2))
                lines.append(f'{station},"{measure}",{date_str},{value}')
    
    return '\n'.join(lines)


if __name__ == '__main__':
    # Test with demo data
    demo = generate_demo_data()
    result = process_data(demo)
    print(json.dumps(result, indent=2))

