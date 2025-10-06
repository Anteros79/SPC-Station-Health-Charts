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
                
                # Auto-detect CSV format
                csv_text = auto_convert_csv_format(csv_text, filename)
                
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
            
            if station and timestamp and metric_value:
                # Map station names if needed
                from load_actual_data import STATION_MAP
                station = STATION_MAP.get(station, station)
                
                output_lines.append(f'{station},{measure_name},{timestamp},{metric_value}')
        
        return '\n'.join(output_lines)
    
    # Format B or already correct - return as-is
    return csv_text


def run_server(port=8000):
    server_address = ('', port)
    httpd = HTTPServer(server_address, SPCHandler)
    
    print(f"""
╔════════════════════════════════════════════════════════════╗
║  Airline Tech Ops SPC Dashboard Server                    ║
╚════════════════════════════════════════════════════════════╝

✓ Server running on: http://localhost:{port}

📋 Instructions:
   1. Open your web browser
   2. Navigate to: http://localhost:{port}
   3. Click 'Load Demo' or upload your CSV file
   4. Press Ctrl+C to stop the server

⚠️  Keep this window open while using the dashboard!
""")
    
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\n\n✓ Server stopped. You can close this window.")
        httpd.shutdown()


if __name__ == '__main__':
    run_server()

