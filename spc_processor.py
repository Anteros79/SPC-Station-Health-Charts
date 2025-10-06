"""
Statistical Process Control (SPC) Data Processor
Converts CSV data to SPC charts with phase detection
"""

import csv
import json
from datetime import datetime
from typing import List, Dict, Any, Tuple
from io import StringIO


def parse_csv(csv_text: str) -> List[Dict[str, Any]]:
    """Parse CSV text into data points"""
    reader = csv.DictReader(StringIO(csv_text))
    data_points = []
    
    for row in reader:
        try:
            data_points.append({
                'station': row['station'].strip(),
                'measure': row['measure'].strip(),
                'date': row['date'].strip(),
                'value': float(row['value'])
            })
        except (ValueError, KeyError) as e:
            print(f"Warning: Skipping invalid row: {e}")
            continue
    
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


def find_phase_end(values: List[float], cl: float, ucl: float, lcl: float) -> int:
    """Find where phase ends using Wheeler's Rules
    
    Wheeler's Rules for detecting special causes:
    Rule #1: Point beyond control limits (outside UCL/LCL)
    Rule #4: 8 consecutive points on one side of centerline
    
    Returns index where current phase should end (signal detected)
    """
    RUN_LENGTH = 8
    
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
        
        # RULE #4: Track 8-point runs
        if value > cl:
            consecutive_above += 1
            consecutive_below = 0
        elif value < cl:
            consecutive_below += 1
            consecutive_above = 0
        else:
            # Point exactly on centerline - doesn't reset counter
            pass
        
        # Signal detected: 8 consecutive on one side
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
    
    # Sort by date
    sorted_data = sorted(data_points, key=lambda x: x['date'])
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
        
        # Augment points with this phase's limits
        for i in range(current_start, min(phase_end + 1, len(augmented_points))):
            augmented_points[i]['cl'] = round(cl, 2)
            augmented_points[i]['ucl'] = round(ucl, 2)
            augmented_points[i]['lcl'] = round(lcl, 2)
        
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
            # X Chart (Individuals)
            chart_data[station][measure] = detect_phases(points)
            
            # mR Chart (Moving Range)
            mr_points = generate_moving_range_data(points)
            if mr_points:  # Only if we have at least 2 points
                mr_measure = measure + ' (Moving Range)'
                chart_data[station][mr_measure] = detect_phases(mr_points)
    
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

