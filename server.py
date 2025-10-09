"""
Simple Python HTTP Server for SPC Dashboard
No installation required - uses Python's built-in http.server
"""

from http.server import HTTPServer, SimpleHTTPRequestHandler
import json
import urllib.parse
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
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            
            try:
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
                self.send_response(400)
                self.send_header('Content-Type', 'application/json')
                self.end_headers()
                error_response = {'error': error_msg, 'success': False}
                self.wfile.write(json.dumps(error_response).encode('utf-8'))
            
            except OSError as e:
                # [Errno 22] Invalid argument falls here
                error_msg = f"File processing error: {str(e)}. Check date formats (use YYYY-MM-DD or M/D/YYYY)"
                self.send_response(400)
                self.send_header('Content-Type', 'application/json')
                self.end_headers()
                error_response = {'error': error_msg, 'success': False}
                self.wfile.write(json.dumps(error_response).encode('utf-8'))
            
            except Exception as e:
                error_msg = f"Unexpected error: {str(e)}"
                self.send_response(500)
                self.send_header('Content-Type', 'application/json')
                self.end_headers()
                error_response = {'error': error_msg, 'success': False}
                self.wfile.write(json.dumps(error_response).encode('utf-8'))
        
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


if __name__ == '__main__':
    run_server()

