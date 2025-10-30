"""
Simple Python HTTP Server for SPC Dashboard
No installation required - uses Python's built-in http.server
"""

from http.server import HTTPServer, SimpleHTTPRequestHandler
import json
import urllib.parse
import math
from spc_processor import process_data, generate_demo_data
from load_actual_data import convert_to_spc_format, infer_measure_from_filename
import re


class SPCHandler(SimpleHTTPRequestHandler):
    def end_headers(self):
        # Enable CORS for local access
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        super().end_headers()
    
    def do_OPTIONS(self):
        self.send_response(200)
        self.end_headers()
    
    def do_GET(self):
        # Serve the dashboard at root
        if self.path == '/' or self.path == '/index.html':
            try:
                with open('dashboard_standalone.html', 'r', encoding='utf-8') as f:
                    content = f.read()
                
                self.send_response(200)
                self.send_header('Content-Type', 'text/html; charset=utf-8')
                self.end_headers()
                self.wfile.write(content.encode('utf-8'))
            except Exception as e:
                self.send_response(500)
                self.send_header('Content-Type', 'text/plain')
                self.end_headers()
                self.wfile.write(f'Error loading dashboard: {str(e)}'.encode('utf-8'))
        else:
            # Let the parent class handle other files
            super().do_GET()
    
    def do_POST(self):
        if self.path == '/api/process':
            # Handle data processing with auto-format detection
            try:
                # Log basic request info (size-limited headers)
                try:
                    raw_headers = str(self.headers)
                    print(f"Incoming /api/process request. Headers (trimmed):\n{raw_headers[:800]}")
                except Exception:
                    pass

                # Defensive Content-Length parsing
                length_header = self.headers.get('Content-Length')
                if not length_header:
                    raise ValueError('Missing Content-Length header')
                try:
                    content_length = int(length_header)
                except Exception:
                    raise ValueError(f'Invalid Content-Length: {length_header}')
                if content_length <= 0:
                    raise ValueError('Empty request body (Content-Length <= 0)')

                # Read request body safely
                post_data = self.rfile.read(content_length)
                if not post_data:
                    raise ValueError('No request body received')

                # Decode JSON strictly
                request_data = json.loads(post_data.decode('utf-8'))
                csv_text = request_data.get('csvData', '')
                filename = request_data.get('filename', '')
                
                # Validate CSV isn't empty
                if not csv_text or not csv_text.strip():
                    raise ValueError("Uploaded file is empty")
                
                # Auto-detect and convert CSV format first
                csv_text = auto_convert_csv_format(csv_text, filename)
                
                # Then validate the converted format
                is_valid, error_msg = validate_csv_format(csv_text)
                if not is_valid:
                    raise ValueError(error_msg)
                
                # Process the data
                result = process_data(csv_text)
                
                # Check if processing succeeded
                if not result.get('success', False):
                    raise ValueError(result.get('error', 'Unknown processing error'))
                
                self.send_response(200)
                self.send_header('Content-Type', 'application/json')
                self.end_headers()
                self.wfile.write(json.dumps(result).encode('utf-8'))
            
            except json.JSONDecodeError as e:
                error_msg = f"Invalid JSON data: {str(e)}"
                self.send_response(400)
                self.send_header('Content-Type', 'application/json')
                self.end_headers()
                error_response = {'error': error_msg, 'success': False}
                self.wfile.write(json.dumps(error_response).encode('utf-8'))
            
            except UnicodeDecodeError as e:
                error_msg = f"File encoding error. Please save as UTF-8: {str(e)}"
                self.send_response(400)
                self.send_header('Content-Type', 'application/json')
                self.end_headers()
                error_response = {'error': error_msg, 'success': False}
                self.wfile.write(json.dumps(error_response).encode('utf-8'))
            
            except ValueError as e:
                error_msg = str(e)
                print(f"ValueError caught: {error_msg}")
                self.send_response(400)
                self.send_header('Content-Type', 'application/json')
                self.end_headers()
                error_response = {'error': error_msg, 'success': False}
                self.wfile.write(json.dumps(error_response).encode('utf-8'))
            
            except OSError as e:
                # [Errno 22] Invalid argument falls here
                error_msg = f"File processing error: {str(e)}<br><br>This is typically caused by invalid date formats. Please ensure:<br>• Dates use supported formats: M/D/YYYY, YYYY-MM-DD, YYYY/M/D, or M-D-YYYY<br>• All date values are valid (no dates like 13/45/2023)<br>• File is saved as UTF-8 encoding"
                print(f"OSError caught: {str(e)}")
                self.send_response(400)
                self.send_header('Content-Type', 'application/json')
                self.end_headers()
                error_response = {'error': error_msg, 'success': False}
                self.wfile.write(json.dumps(error_response).encode('utf-8'))
            
            except Exception as e:
                import traceback
                error_msg = f"Unexpected error: {str(e)}"
                print(f"\n{'='*60}")
                print(f"EXCEPTION CAUGHT: {type(e).__name__}")
                print(f"Error message: {str(e)}")
                print(f"Traceback:")
                traceback.print_exc()
                print(f"{'='*60}\n")
                self.send_response(500)
                self.send_header('Content-Type', 'application/json')
                self.end_headers()
                error_response = {'error': error_msg, 'success': False}
                self.wfile.write(json.dumps(error_response).encode('utf-8'))
        
        elif self.path == '/api/ping':
            # Simple echo endpoint to test POST pipeline
            try:
                length_header = self.headers.get('Content-Length')
                content_length = int(length_header) if length_header else 0
                body = self.rfile.read(content_length) if content_length > 0 else b''
                payload = None
                if body:
                    try:
                        payload = json.loads(body.decode('utf-8'))
                    except Exception:
                        payload = {'raw': body.decode('utf-8', errors='replace')}
                self.send_response(200)
                self.send_header('Content-Type', 'application/json')
                self.end_headers()
                self.wfile.write(json.dumps({'ok': True, 'received': payload}).encode('utf-8'))
            except Exception as e:
                self.send_response(500)
                self.send_header('Content-Type', 'application/json')
                self.end_headers()
                self.wfile.write(json.dumps({'ok': False, 'error': str(e)}).encode('utf-8'))
        
        elif self.path == '/api/demo':
            # Generate demo data
            try:
                demo_csv = generate_demo_data()
                result = process_data(demo_csv)
                
                self.send_response(200)
                self.send_header('Content-Type', 'application/json')
                self.end_headers()
                self.wfile.write(json.dumps(result).encode('utf-8'))
            
            except Exception as e:
                self.send_response(500)
                self.send_header('Content-Type', 'application/json')
                self.end_headers()
                error_response = {'error': str(e), 'success': False}
                self.wfile.write(json.dumps(error_response).encode('utf-8'))
        
        elif self.path == '/api/load-actual':
            # Load actual data from input folder
            try:
                import os
                # Use local input folder (relative to script location)
                script_dir = os.path.dirname(os.path.abspath(__file__))
                input_folder = os.path.join(script_dir, 'input')
                csv_text = convert_to_spc_format(input_folder)
                result = process_data(csv_text)
                
                self.send_response(200)
                self.send_header('Content-Type', 'application/json')
                self.end_headers()
                self.wfile.write(json.dumps(result).encode('utf-8'))
            
            except Exception as e:
                self.send_response(500)
                self.send_header('Content-Type', 'application/json')
                self.end_headers()
                error_response = {'error': str(e), 'success': False}
                self.wfile.write(json.dumps(error_response).encode('utf-8'))
        
        elif self.path == '/api/generate-airline-kpis':
            # Generate realistic airline KPI data
            try:
                result = generate_airline_kpi_data()
                self.send_response(200)
                self.send_header('Content-Type', 'application/json')
                self.end_headers()
                self.wfile.write(json.dumps(result).encode('utf-8'))
            
            except Exception as e:
                self.send_response(500)
                self.send_header('Content-Type', 'application/json')
                self.end_headers()
                error_response = {'error': str(e), 'success': False}
                self.wfile.write(json.dumps(error_response).encode('utf-8'))
        
        else:
            self.send_response(404)
            self.end_headers()
    
    def log_message(self, format, *args):
        # Custom logging to make it cleaner
        print(f"[{self.log_date_time_string()}] {format % args}")


def auto_convert_csv_format(csv_text, filename=''):
    """
    Auto-detect CSV format and convert if needed.
    Supports both formats:
    - Format A: timestamp,station,metric_value (uses filename as measure)
    - Format B: station,measure,date,value (standard format)
    """
    lines = csv_text.strip().split('\n')
    if not lines:
        return csv_text
    
    header = lines[0].lower()
    
    # Check if it's Format A (timestamp,station,metric_value)
    if 'timestamp' in header and 'metric_value' in header and 'measure' not in header:
        # Format A detected - convert to Format B
        measure_name = infer_measure_from_filename(filename) if filename else 'Metric'
        
        # Read CSV and convert
        from io import StringIO
        import csv
        
        reader = csv.DictReader(StringIO(csv_text))
        output_lines = ['station,measure,date,value']
        
        for row in reader:
            station = row.get('station', '').strip()
            timestamp = row.get('timestamp', '').strip()
            metric_value = row.get('metric_value', '').strip()
            
            print(f"Debug - Row: station='{station}', timestamp='{timestamp}', metric_value='{metric_value}'")
            
            if station and timestamp and metric_value:
                # Map station names if needed
                from load_actual_data import STATION_MAP
                station = STATION_MAP.get(station, station)
                
                output_lines.append(f'{station},{measure_name},{timestamp},{metric_value}')
        
        return '\n'.join(output_lines)
    
    # Format B or already correct - return as-is
    return csv_text


def validate_csv_format(csv_text):
    """
    Validate CSV format and provide helpful error messages
    Returns (is_valid, error_message)
    """
    lines = [line.strip() for line in csv_text.strip().split('\n') if line.strip()]
    
    if len(lines) < 2:
        return False, "CSV file must have at least a header row and one data row"
    
    header = lines[0].lower()
    required_formats = [
        (['timestamp', 'station', 'metric_value'], "Format A"),
        (['station', 'measure', 'date', 'value'], "Format B")
    ]
    
    # Check if header matches either format
    for required_cols, format_name in required_formats:
        if all(col in header for col in required_cols):
            return True, ""
    
    # Neither format matched
    return False, f"CSV header must contain either:\n  - 'timestamp,station,metric_value' OR\n  - 'station,measure,date,value'\nFound: {lines[0]}"


def run_server(port=8000):
    server_address = ('', port)
    httpd = HTTPServer(server_address, SPCHandler)
    
    print(f"""
============================================================
  Airline Tech Ops SPC Dashboard Server                    
============================================================

Server running on: http://localhost:{port}

Instructions:
   1. Open your web browser
   2. Navigate to: http://localhost:{port}
   3. Click 'Load Demo' or upload your CSV file
   4. Press Ctrl+C to stop the server

WARNING: Keep this window open while using the dashboard!
""")
    
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\n\n✓ Server stopped. You can close this window.")
        httpd.shutdown()


def generate_airline_kpi_data():
    """
    Generate realistic airline technical operations KPI data for testing.
    Creates both weekly SPC data and daily bar chart data.
    """
    import random
    import datetime
    from spc_processor import process_data
    
    # Airline stations (major Southwest hubs)
    stations = ['DAL', 'HOU', 'PHX', 'DEN', 'LAS', 'LAX', 'MDW', 'BWI']
    
    # Realistic airline tech ops KPIs
    weekly_measures = {
        'Aircraft On-Time Performance': {'base': 85, 'variation': 8, 'unit': '%'},
        'Maintenance Delays per 100 Departures': {'base': 2.5, 'variation': 1.2, 'unit': 'delays'},
        'Unscheduled Maintenance Events': {'base': 12, 'variation': 4, 'unit': 'events'},
        'Aircraft Availability Rate': {'base': 92, 'variation': 5, 'unit': '%'},
        'Ground Support Equipment Reliability': {'base': 96, 'variation': 3, 'unit': '%'},
        'Baggage Handling Performance': {'base': 99.2, 'variation': 0.5, 'unit': '%'}
    }
    
    daily_measures = {
        'MEL Rate (Daily)': {'base': 0.35, 'variation': 0.15, 'unit': 'rate'},
        'Aircraft Turn Time (Daily)': {'base': 45, 'variation': 12, 'unit': 'minutes'},
        'Gate Departure Delays (Daily)': {'base': 8, 'variation': 6, 'unit': 'minutes'}
    }
    
    # Generate data starting from January 1, 2023
    start_date = datetime.date(2023, 1, 1)
    end_date = datetime.date(2025, 10, 13)  # Current date
    
    csv_lines = []
    
    # Generate weekly data (every Monday)
    current_date = start_date
    while current_date <= end_date:
        if current_date.weekday() == 0:  # Monday
            for station in stations:
                for measure_name, params in weekly_measures.items():
                    # Add some realistic seasonal variation
                    seasonal_factor = 1 + 0.1 * math.sin(2 * math.pi * current_date.timetuple().tm_yday / 365)
                    
                    # Add some station-specific variation
                    station_factor = 1 + (hash(station) % 20 - 10) / 100  # -10% to +10%
                    
                    # Generate value with normal distribution
                    base_value = params['base'] * seasonal_factor * station_factor
                    value = max(0, random.normalvariate(base_value, params['variation']))
                    
                    # Round appropriately
                    if params['unit'] == '%':
                        value = round(value, 1)
                    elif params['unit'] == 'rate':
                        value = round(value, 3)
                    else:
                        value = round(value, 1)
                    
                    csv_lines.append(f"{station},{measure_name},{current_date},{value}")
        
        current_date += datetime.timedelta(days=1)
    
    # Generate daily data for the last 30 days
    daily_start = end_date - datetime.timedelta(days=30)
    current_date = daily_start
    while current_date <= end_date:
        for station in stations:
            for measure_name, params in daily_measures.items():
                # Weekend effect (slightly different performance)
                weekend_factor = 0.95 if current_date.weekday() >= 5 else 1.0
                
                # Generate value with normal distribution
                base_value = params['base'] * weekend_factor
                value = max(0, random.normalvariate(base_value, params['variation']))
                
                # Round appropriately
                if params['unit'] == 'rate':
                    value = round(value, 3)
                else:
                    value = round(value, 1)
                
                csv_lines.append(f"{station},{measure_name} (Daily Bar),{current_date},{value}")
        
        current_date += datetime.timedelta(days=1)
    
    # Convert to CSV format
    csv_content = "station,measure,date,value\n" + "\n".join(csv_lines)
    
    # Process the data
    result = process_data(csv_content)
    
    return result


if __name__ == '__main__':
    run_server()

