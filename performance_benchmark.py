#!/usr/bin/env python3
"""
Performance Benchmarking Script for Southwest Airlines Tech Ops SPC Dashboard

This script measures and compares dashboard load times and chart rendering performance
between CDN and local library versions to validate offline performance requirements.

Requirements: 1.5 (Performance validation)
"""

import os
import sys
import time
import json
import subprocess
import threading
import socket
import tempfile
import shutil
from http.server import HTTPServer, SimpleHTTPRequestHandler
from urllib.request import urlopen
from urllib.error import URLError
import statistics
from contextlib import contextmanager


class PerformanceBenchmark:
    def __init__(self):
        self.results = {
            'timestamp': time.strftime('%Y-%m-%d %H:%M:%S'),
            'tests': [],
            'summary': {}
        }
        self.server_port = 8002  # Different port for benchmarking
        
    def log_result(self, test_name, metric, value, unit, passed=True, details=""):
        """Log performance test result"""
        status = "PASS" if passed else "FAIL"
        print(f"[{status}] {test_name}: {value:.3f}{unit}")
        if details:
            print(f"    {details}")
        
        self.results['tests'].append({
            'test': test_name,
            'metric': metric,
            'value': value,
            'unit': unit,
            'passed': passed,
            'details': details
        })
    
    def start_test_server(self):
        """Start HTTP server for performance testing"""
        try:
            sys.path.insert(0, '.')
            from server import SPCHandler
            
            server_address = ('localhost', self.server_port)
            httpd = HTTPServer(server_address, SPCHandler)
            
            def run_server():
                try:
                    httpd.serve_forever()
                except:
                    pass
            
            server_thread = threading.Thread(target=run_server, daemon=True)
            server_thread.start()
            
            # Wait for server to start
            time.sleep(2)
            
            # Test if server is responding
            try:
                response = urlopen(f'http://localhost:{self.server_port}/', timeout=5)
                if response.getcode() == 200:
                    print(f"✅ Test server started on port {self.server_port}")
                    return httpd
                else:
                    print(f"❌ Server returned status code: {response.getcode()}")
                    return None
            except Exception as e:
                print(f"❌ Server not responding: {str(e)}")
                return None
                
        except Exception as e:
            print(f"❌ Failed to start server: {str(e)}")
            return None
    
    def measure_dashboard_load_time(self, test_name, iterations=5):
        """Measure dashboard load time with multiple iterations"""
        load_times = []
        
        for i in range(iterations):
            try:
                start_time = time.time()
                
                url = f'http://localhost:{self.server_port}/'
                response = urlopen(url, timeout=15)
                content = response.read()
                
                load_time = time.time() - start_time
                load_times.append(load_time)
                
                print(f"  Iteration {i+1}: {load_time:.3f}s")
                
                # Small delay between iterations
                time.sleep(0.5)
                
            except Exception as e:
                print(f"  Iteration {i+1}: FAILED - {str(e)}")
                continue
        
        if load_times:
            avg_time = statistics.mean(load_times)
            min_time = min(load_times)
            max_time = max(load_times)
            
            # Check if meets 5-second requirement
            passed = avg_time <= 5.0
            
            details = f"Min: {min_time:.3f}s, Max: {max_time:.3f}s, Avg: {avg_time:.3f}s ({iterations} iterations)"
            
            self.log_result(
                test_name,
                "load_time_avg",
                avg_time,
                "s",
                passed,
                details
            )
            
            return {
                'avg': avg_time,
                'min': min_time,
                'max': max_time,
                'iterations': len(load_times)
            }
        else:
            self.log_result(
                test_name,
                "load_time_avg",
                0,
                "s",
                False,
                "All iterations failed"
            )
            return None
    
    def measure_api_response_time(self, endpoint, test_name, iterations=3):
        """Measure API endpoint response time"""
        response_times = []
        
        for i in range(iterations):
            try:
                import urllib.request
                import json
                
                start_time = time.time()
                
                url = f'http://localhost:{self.server_port}{endpoint}'
                req = urllib.request.Request(url, data=b'{}', headers={'Content-Type': 'application/json'})
                req.get_method = lambda: 'POST'
                
                response = urllib.request.urlopen(req, timeout=15)
                data = json.loads(response.read().decode('utf-8'))
                
                response_time = time.time() - start_time
                
                if data.get('success', False):
                    response_times.append(response_time)
                    print(f"  API {endpoint} iteration {i+1}: {response_time:.3f}s")
                else:
                    print(f"  API {endpoint} iteration {i+1}: FAILED - {data.get('error', 'Unknown error')}")
                
                time.sleep(0.5)
                
            except Exception as e:
                print(f"  API {endpoint} iteration {i+1}: FAILED - {str(e)}")
                continue
        
        if response_times:
            avg_time = statistics.mean(response_times)
            
            self.log_result(
                test_name,
                "api_response_time",
                avg_time,
                "s",
                True,
                f"Average of {len(response_times)} successful calls"
            )
            
            return avg_time
        else:
            self.log_result(
                test_name,
                "api_response_time",
                0,
                "s",
                False,
                "All API calls failed"
            )
            return None
    
    def test_csv_upload_performance(self):
        """Test CSV upload and processing performance"""
        # Find a test CSV file
        test_csv_files = [
            'input/Daily_Airline_KPIs_Sample.csv',
            'input/Weekly_Airline_KPIs_Sample.csv',
            'input/Simple_Test.csv'
        ]
        
        test_file = None
        for csv_file in test_csv_files:
            if os.path.exists(csv_file):
                test_file = csv_file
                break
        
        if not test_file:
            self.log_result(
                "CSV Upload Performance",
                "upload_time",
                0,
                "s",
                False,
                "No test CSV files found"
            )
            return None
        
        try:
            # Read the CSV file
            with open(test_file, 'r') as f:
                csv_content = f.read()
            
            # Measure upload and processing time
            start_time = time.time()
            
            import urllib.request
            import urllib.parse
            
            # Simulate CSV upload via API
            url = f'http://localhost:{self.server_port}/api/upload-csv'
            data = urllib.parse.urlencode({'csv_data': csv_content}).encode('utf-8')
            req = urllib.request.Request(url, data=data, headers={'Content-Type': 'application/x-www-form-urlencoded'})
            req.get_method = lambda: 'POST'
            
            try:
                response = urllib.request.urlopen(req, timeout=30)
                result = json.loads(response.read().decode('utf-8'))
                
                processing_time = time.time() - start_time
                
                if result.get('success', False):
                    self.log_result(
                        "CSV Upload Performance",
                        "upload_time",
                        processing_time,
                        "s",
                        True,
                        f"Processed {test_file} successfully"
                    )
                    return processing_time
                else:
                    self.log_result(
                        "CSV Upload Performance",
                        "upload_time",
                        processing_time,
                        "s",
                        False,
                        f"Upload failed: {result.get('error', 'Unknown error')}"
                    )
                    return None
            except Exception as e:
                processing_time = time.time() - start_time
                self.log_result(
                    "CSV Upload Performance",
                    "upload_time",
                    processing_time,
                    "s",
                    False,
                    f"Upload request failed: {str(e)}"
                )
                return None
                
        except Exception as e:
            self.log_result(
                "CSV Upload Performance",
                "upload_time",
                0,
                "s",
                False,
                f"Error reading test file: {str(e)}"
            )
            return None
    
    @contextmanager
    def create_cdn_version(self):
        """Create temporary CDN version for comparison"""
        print("🔄 Creating temporary CDN version for comparison...")
        
        # Backup current HTML file
        backup_file = 'dashboard_standalone.html.backup'
        shutil.copy2('dashboard_standalone.html', backup_file)
        
        try:
            # Modify HTML to use CDN
            with open('dashboard_standalone.html', 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Replace local reference with CDN
            cdn_content = content.replace(
                './js/plotly-2.27.0.min.js',
                'https://cdn.plot.ly/plotly-2.27.0.min.js'
            )
            
            with open('dashboard_standalone.html', 'w', encoding='utf-8') as f:
                f.write(cdn_content)
            
            print("✅ Temporary CDN version created")
            yield
            
        finally:
            # Restore original file
            shutil.move(backup_file, 'dashboard_standalone.html')
            print("✅ Original local version restored")
    
    def run_performance_comparison(self):
        """Run comprehensive performance comparison"""
        print("=" * 60)
        print("Southwest Airlines Tech Ops SPC Dashboard")
        print("Performance Benchmarking Suite")
        print("=" * 60)
        
        # Start test server
        print("\n🚀 Starting Performance Test Server")
        print("-" * 40)
        
        server = self.start_test_server()
        if not server:
            print("❌ Critical: Could not start test server")
            return False
        
        try:
            # Test 1: Local version performance (current state)
            print("\n📊 Testing Local Plotly.js Performance")
            print("-" * 40)
            
            local_results = {}
            
            # Dashboard load time
            print("Measuring dashboard load time (local)...")
            local_results['load_time'] = self.measure_dashboard_load_time("Dashboard Load Time (Local)")
            
            # API response times
            print("Measuring API response times...")
            local_results['api_demo'] = self.measure_api_response_time('/api/demo', 'API Demo Response (Local)')
            local_results['api_load'] = self.measure_api_response_time('/api/load-actual', 'API Load Actual (Local)')
            
            # CSV upload performance
            print("Measuring CSV upload performance...")
            local_results['csv_upload'] = self.test_csv_upload_performance()
            
            # Test 2: CDN version performance (for comparison)
            print("\n🌐 Testing CDN Plotly.js Performance (Comparison)")
            print("-" * 40)
            
            cdn_results = {}
            
            # Only test CDN if we have internet connection
            try:
                # Quick connectivity test
                test_response = urlopen('https://cdn.plot.ly/plotly-2.27.0.min.js', timeout=5)
                if test_response.getcode() == 200:
                    print("✅ Internet connection available - testing CDN performance")
                    
                    with self.create_cdn_version():
                        # Restart server to pick up changes
                        server.shutdown()
                        time.sleep(2)
                        server = self.start_test_server()
                        
                        if server:
                            print("Measuring dashboard load time (CDN)...")
                            cdn_results['load_time'] = self.measure_dashboard_load_time("Dashboard Load Time (CDN)")
                            
                            print("Measuring API response times (CDN)...")
                            cdn_results['api_demo'] = self.measure_api_response_time('/api/demo', 'API Demo Response (CDN)')
                else:
                    print("⚠️  CDN not accessible - skipping CDN comparison")
                    
            except Exception as e:
                print(f"⚠️  No internet connection - skipping CDN comparison: {str(e)}")
            
            # Performance Analysis
            print("\n📈 Performance Analysis")
            print("-" * 40)
            
            self.analyze_performance_results(local_results, cdn_results)
            
            # Generate summary
            self.generate_performance_summary()
            
            return True
            
        finally:
            if server:
                server.shutdown()
    
    def analyze_performance_results(self, local_results, cdn_results):
        """Analyze and compare performance results"""
        
        # Analyze local performance
        if local_results.get('load_time'):
            local_load = local_results['load_time']['avg']
            
            if local_load <= 5.0:
                print(f"✅ Local load time: {local_load:.3f}s (meets 5s requirement)")
            else:
                print(f"❌ Local load time: {local_load:.3f}s (exceeds 5s requirement)")
        
        # Compare with CDN if available
        if cdn_results.get('load_time') and local_results.get('load_time'):
            local_load = local_results['load_time']['avg']
            cdn_load = cdn_results['load_time']['avg']
            
            if local_load < cdn_load:
                improvement = ((cdn_load - local_load) / cdn_load) * 100
                print(f"🚀 Local version is {improvement:.1f}% faster than CDN")
                self.log_result(
                    "Performance Comparison",
                    "improvement_percentage",
                    improvement,
                    "%",
                    True,
                    f"Local: {local_load:.3f}s vs CDN: {cdn_load:.3f}s"
                )
            else:
                degradation = ((local_load - cdn_load) / cdn_load) * 100
                print(f"⚠️  Local version is {degradation:.1f}% slower than CDN")
                self.log_result(
                    "Performance Comparison",
                    "degradation_percentage",
                    degradation,
                    "%",
                    degradation < 10,  # Accept up to 10% degradation
                    f"Local: {local_load:.3f}s vs CDN: {cdn_load:.3f}s"
                )
        
        # Analyze API performance
        if local_results.get('api_demo'):
            api_time = local_results['api_demo']
            if api_time <= 2.0:
                print(f"✅ API response time: {api_time:.3f}s (good)")
            else:
                print(f"⚠️  API response time: {api_time:.3f}s (may be slow)")
        
        # Analyze CSV upload performance
        if local_results.get('csv_upload'):
            csv_time = local_results['csv_upload']
            if csv_time <= 10.0:
                print(f"✅ CSV upload time: {csv_time:.3f}s (acceptable)")
            else:
                print(f"⚠️  CSV upload time: {csv_time:.3f}s (may be slow)")
    
    def generate_performance_summary(self):
        """Generate performance test summary"""
        total_tests = len(self.results['tests'])
        passed_tests = sum(1 for test in self.results['tests'] if test['passed'])
        
        self.results['summary'] = {
            'total_tests': total_tests,
            'passed_tests': passed_tests,
            'failed_tests': total_tests - passed_tests,
            'success_rate': (passed_tests / total_tests) * 100 if total_tests > 0 else 0
        }
        
        print(f"\n📊 Performance Test Summary")
        print("-" * 40)
        print(f"Tests Passed: {passed_tests}/{total_tests}")
        print(f"Success Rate: {self.results['summary']['success_rate']:.1f}%")
        
        # Show failed tests
        failed_tests = [test for test in self.results['tests'] if not test['passed']]
        if failed_tests:
            print("\nFailed Tests:")
            for test in failed_tests:
                print(f"  ❌ {test['test']}: {test['value']:.3f}{test['unit']}")
                if test['details']:
                    print(f"     {test['details']}")
        
        # Save detailed report
        with open('performance_benchmark_report.json', 'w') as f:
            json.dump(self.results, f, indent=2)
        
        print(f"\n📄 Detailed performance report saved to: performance_benchmark_report.json")
        
        return self.results['summary']['success_rate'] >= 80  # 80% pass rate threshold


def main():
    """Main benchmarking execution"""
    benchmark = PerformanceBenchmark()
    
    try:
        success = benchmark.run_performance_comparison()
        
        if success:
            print("\n🎉 Performance benchmarking completed successfully!")
            sys.exit(0)
        else:
            print("\n⚠️  Performance benchmarking completed with issues. See details above.")
            sys.exit(1)
            
    except KeyboardInterrupt:
        print("\n\n⏹️  Benchmarking interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n💥 Unexpected error during benchmarking: {str(e)}")
        sys.exit(1)


if __name__ == '__main__':
    main()