"""
Load the actual CSV files from input folder and convert to SPC format
"""

import csv
import os
from pathlib import Path

# Map filenames to measure names
MEASURE_NAMES = {
    'maintenance_cancels.csv': 'Maintenance Cancels',
    'maintenance_delays.csv': 'Maintenance Delays',
    'scheduled_maintenance_findings.csv': 'Scheduled Maintenance Findings',
    'unscheduled_maintenance.csv': 'Unscheduled Maintenance'
}

# Map full station names to codes
STATION_MAP = {
    'Austin': 'AUS',
    'Dallas': 'DAL',  # Dallas Love Field
    'Dallas Love Field': 'DAL',
    'Dallas Lovefield': 'DAL',
    'Houston': 'HOU',  # Houston Hobby
    'Houston Hobby': 'HOU'
}

def infer_measure_from_filename(filename):
    """
    Infer measure name from filename.
    Examples:
      maintenance_cancels.csv -> Maintenance Cancels
      scheduled_maintenance_findings.csv -> Scheduled Maintenance Findings
    """
    # Check if it's in our known measures first
    if filename in MEASURE_NAMES:
        return MEASURE_NAMES[filename]
    
    # Otherwise, convert filename to title case
    # Remove .csv extension
    name = filename.replace('.csv', '').replace('.CSV', '')
    # Replace underscores with spaces and title case
    name = name.replace('_', ' ').title()
    return name

def convert_to_spc_format(input_folder):
    """
    Read all CSV files from input folder and convert to unified SPC format
    Returns CSV text in format: station,measure,date,value
    """
    output_lines = ['station,measure,date,value']
    
    input_path = Path(input_folder)
    
    for filename in MEASURE_NAMES.keys():
        filepath = input_path / filename
        
        if not filepath.exists():
            print(f"Warning: {filename} not found")
            continue
        
        measure_name = MEASURE_NAMES[filename]
        
        with open(filepath, 'r') as f:
            reader = csv.DictReader(f)
            
            for row in reader:
                try:
                    # Get values from your format
                    timestamp = row['timestamp'].strip()
                    station_full = row['station'].strip()
                    metric_value = row['metric_value'].strip()
                    
                    # Convert station name to code
                    station_code = STATION_MAP.get(station_full, station_full)
                    
                    # Create output line
                    output_line = f'{station_code},{measure_name},{timestamp},{metric_value}'
                    output_lines.append(output_line)
                    
                except (KeyError, ValueError) as e:
                    print(f"Skipping invalid row in {filename}: {e}")
                    continue
    
    return '\n'.join(output_lines)


if __name__ == '__main__':
    # Test the conversion
    import os
    # Use local input folder (relative to script location)
    script_dir = os.path.dirname(os.path.abspath(__file__))
    input_folder = os.path.join(script_dir, 'input')
    
    csv_text = convert_to_spc_format(input_folder)
    
    print("First 20 lines of converted data:")
    print('\n'.join(csv_text.split('\n')[:20]))
    print(f"\nTotal lines: {len(csv_text.split(chr(10)))}")

