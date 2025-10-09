# Technical Specification
## SPC Station Health Charts

**Version:** 1.6  
**Date:** October 9, 2025  
**Status:** Implemented with Debug Tools  
**Enhancement:** CSV Troubleshooting & Enhanced Error Reporting

---

## 1. Technical Overview

### 1.1 Technology Stack

| Component | Technology | Version | Rationale |
|-----------|-----------|---------|-----------|
| **Backend Language** | Python | 3.7+ | Pre-installed enterprise-wide; no admin rights needed |
| **Web Server** | http.server | stdlib | Zero dependencies; sufficient for localhost |
| **Frontend** | HTML5 + Vanilla JS | - | Universal browser support; no build step |
| **Charting** | HTML5 Canvas API | - | No external libraries; full PNG export control |
| **Data Format** | CSV | - | Universal; easy to generate |
| **API Protocol** | HTTP/JSON | - | Standard web protocols |

### 1.2 System Architecture

**Architecture Pattern:** Client-Server (Local Desktop)

```
┌─────────────────────────────────────────────────────┐
│                User's Desktop                        │
│                                                      │
│  ┌────────────┐         ┌──────────────────┐       │
│  │  Browser   │◄───────►│  Python Server   │       │
│  │  (Client)  │  HTTP   │  (localhost:8000)│       │
│  └────────────┘         └──────────────────┘       │
│       │                          │                  │
│       │                          │                  │
│       v                          v                  │
│  ┌────────────┐         ┌──────────────────┐       │
│  │  Canvas    │         │  SPC Processor   │       │
│  │  Rendering │         │  (Statistics)    │       │
│  └────────────┘         └──────────────────┘       │
│                                  │                  │
│                                  v                  │
│                          ┌──────────────────┐       │
│                          │  CSV Files       │       │
│                          │  (input/)        │       │
│                          └──────────────────┘       │
└─────────────────────────────────────────────────────┘
```

---

## 2. Backend Implementation

### 2.1 server.py - HTTP Request Handler

**File:** `server.py`  
**Lines of Code:** ~200  
**Dependencies:** Python stdlib only

#### Class: SPCHandler

```python
class SPCHandler(SimpleHTTPRequestHandler):
    """
    Custom HTTP request handler for SPC Dashboard.
    Routes:
      - GET /               → Serve dashboard_standalone.html
      - POST /api/process   → Process uploaded CSV
      - POST /api/load-actual → Load sample data from input/
      - OPTIONS *           → CORS preflight
    """
```

**Key Methods:**

| Method | Purpose | Input | Output |
|--------|---------|-------|--------|
| `end_headers()` | Add CORS headers | None | HTTP headers |
| `do_OPTIONS()` | Handle CORS preflight | HTTP request | 200 OK |
| `do_GET()` | Serve HTML file | GET / | HTML content |
| `do_POST()` | Process API requests | JSON body | JSON response |

**API Endpoints:**

#### Endpoint 1: GET /
```python
def do_GET(self):
    if self.path == '/' or self.path == '/index.html':
        with open('dashboard_standalone.html', 'r', encoding='utf-8') as f:
            content = f.read()
        self.send_response(200)
        self.send_header('Content-Type', 'text/html; charset=utf-8')
        self.end_headers()
        self.wfile.write(content.encode('utf-8'))
```

#### Endpoint 2: POST /api/process
```python
# Reads request body (JSON with csvData and filename)
# Calls auto_convert_csv_format() to standardize format
# Calls spc_processor.process_data()
# Returns JSON response with chartData
```

#### Endpoint 3: POST /api/load-actual
```python
# Determines input folder path (relative to script)
# Calls load_actual_data.convert_to_spc_format()
# Calls spc_processor.process_data()
# Returns JSON response with chartData
```

**Error Handling:**
```python
try:
    # Process request
    result = process_data(csv_text)
    self.send_response(200)
except Exception as e:
    self.send_response(500)
    error_response = {'error': str(e), 'success': False}
    self.wfile.write(json.dumps(error_response).encode('utf-8'))
```

---

### 2.2 spc_processor.py - Statistical Engine

**File:** `spc_processor.py`  
**Lines of Code:** ~400  
**Purpose:** Core SPC calculations and phase detection

#### Function: parse_csv(csv_text)
**Input:** Raw CSV string  
**Output:** List of dictionaries `[{station, measure, date, value}, ...]`

```python
def parse_csv(csv_text: str) -> List[Dict[str, Any]]:
    """
    Parse CSV text into structured data points.
    Expected format: station,measure,date,value
    
    Returns:
        List of dicts with keys: station, measure, date, value
    """
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
        except (KeyError, ValueError):
            continue  # Skip invalid rows
    
    return data_points
```

---

#### Function: calculate_initial_limits(values)
**Input:** List of numeric values  
**Output:** Tuple `(center_line, moving_range_average)`

**Algorithm:**
1. Calculate center line (CL) = mean of values
2. Calculate moving ranges: `mR[i] = |value[i] - value[i-1]|`
3. Calculate average moving range: `mR̄ = mean(mR)`
4. Return (CL, mR̄)

```python
def calculate_initial_limits(values: List[float]) -> Tuple[float, float]:
    """
    Calculate center line and moving range average.
    
    Wheeler's method:
    - CL = mean(X)
    - mR̄ = mean(|X[i] - X[i-1]|)
    """
    if len(values) < 2:
        return (values[0] if values else 0, 0)
    
    cl = sum(values) / len(values)
    
    moving_ranges = [abs(values[i] - values[i-1]) 
                     for i in range(1, len(values))]
    mR_bar = sum(moving_ranges) / len(moving_ranges)
    
    return (cl, mR_bar)
```

**Control Limit Calculation:**
```python
# Natural Process Limits (2.66 sigma)
ucl = cl + 2.66 * mR_bar
lcl = max(0, cl - 2.66 * mR_bar)  # Non-negative
```

---

#### Function: find_phase_end(values, cl, ucl, lcl)
**Input:** List of values, control limits  
**Output:** Index where phase ends (signal detected)

**Algorithm:** Wheeler's Rules

```python
def find_phase_end(values: List[float], cl: float, ucl: float, lcl: float) -> int:
    """
    Find where phase ends using Wheeler's Rules.
    
    Wheeler's Rules for detecting special causes:
      Rule #1: Point beyond control limits (outside UCL/LCL)
      Rule #4: 7 consecutive points on one side of centerline
    
    Returns:
        Index where current phase should end (signal detected)
    """
    RUN_LENGTH = 7
    consecutive_above = 0
    consecutive_below = 0
    
    for i, value in enumerate(values):
        # RULE #1: Point outside control limits
        if value > ucl or value < lcl:
            # Signal! Phase ends at the point BEFORE this outlier
            return max(0, i - 1)
        
        # RULE #4: Track 7-point runs
        if value > cl:
            consecutive_above += 1
            consecutive_below = 0
        elif value < cl:
            consecutive_below += 1
            consecutive_above = 0
        # Point exactly on centerline doesn't reset counter
        
        # Signal detected: 7 consecutive on one side
        if consecutive_above >= RUN_LENGTH or consecutive_below >= RUN_LENGTH:
            # Phase ends at the point BEFORE the run started
            return max(0, i - RUN_LENGTH)
    
    # No signal found - entire dataset is one phase
    return len(values) - 1
```

---

#### Function: detect_phases(data_points)
**Input:** List of data points (sorted by date)  
**Output:** Dictionary with augmented points and phase metadata

**Algorithm:**
1. Start with baseline (minimum 20 points)
2. Calculate limits from baseline ONLY
3. Monitor remaining data for Wheeler's Rules signals
4. When signal detected:
   - End current phase
   - Start new phase
   - Recalculate limits from actual phase data
5. Augment each point with its phase's control limits

```python
def detect_phases(data_points: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Detect phases and recalculate control limits when process shifts occur.
    
    Proper SPC phase detection:
      1. Start with baseline data (minimum 20 points)
      2. Calculate limits from ONLY that baseline
      3. Extend phase forward, watching for signals
      4. When signal detected, start new phase at signal point
    
    Returns:
        {
            'points': [...],  # Augmented with ucl, cl, lcl
            'phases': [...]   # Phase metadata
        }
    """
    MIN_BASELINE = 20
    
    sorted_data = sorted(data_points, key=lambda x: x['date'])
    values = [p['value'] for p in sorted_data]
    phases = []
    augmented_points = [dict(p) for p in sorted_data]
    
    current_start = 0
    phase_number = 1
    
    while current_start < len(values):
        # Establish baseline
        baseline_end = min(current_start + MIN_BASELINE, len(values))
        baseline_values = values[current_start:baseline_end]
        
        if not baseline_values:
            break
        
        # Calculate limits from baseline ONLY
        cl, mR_bar = calculate_initial_limits(baseline_values)
        ucl = cl + 2.66 * mR_bar
        lcl = max(0, cl - 2.66 * mR_bar)
        
        # Monitor remaining data for signal
        remaining_values = values[baseline_end:]
        signal_offset = find_phase_end(remaining_values, cl, ucl, lcl)
        phase_end = baseline_end + signal_offset
        
        # Recalculate limits from actual phase data
        phase_values = values[current_start:phase_end + 1]
        cl, mR_bar = calculate_initial_limits(phase_values)
        ucl = cl + 2.66 * mR_bar
        lcl = max(0, cl - 2.66 * mR_bar)
        
        # Save phase metadata
        phases.append({
            'startIndex': current_start,
            'endIndex': phase_end,
            'cl': round(cl, 2),
            'ucl': round(ucl, 2),
            'lcl': round(lcl, 2),
            'phaseNumber': phase_number
        })
        
        # Augment points with limits
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
```

---

#### Function: generate_moving_range_data(individuals_data)
**Input:** List of Individuals (X) data points  
**Output:** List of Moving Range (mR) data points

```python
def generate_moving_range_data(individuals_data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Generate Moving Range data from Individuals data.
    
    Moving Range = |X[i] - X[i-1]|
    Used to monitor process variation.
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
```

---

#### Function: process_data(csv_text)
**Input:** CSV string  
**Output:** JSON structure with chart data

```python
def process_data(csv_text: str) -> Dict[str, Any]:
    """
    Process CSV data and return structured chart data.
    
    Generates both X chart (Individuals) and mR chart (Moving Range)
    following Wheeler's XmR methodology.
    
    Returns:
        {
            'success': True,
            'chartData': {
                'STATION': {
                    'MEASURE': {'points': [...], 'phases': [...]},
                    'MEASURE (Moving Range)': {'points': [...], 'phases': [...]}
                }
            },
            'stations': ['STATION1', 'STATION2', ...]
        }
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
    chart_data = {}
    for station, measures in grouped.items():
        chart_data[station] = {}
        for measure, points in measures.items():
            # X Chart (Individuals)
            chart_data[station][measure] = detect_phases(points)
            
            # mR Chart (Moving Range)
            mr_points = generate_moving_range_data(points)
            if mr_points:
                mr_measure = measure + ' (Moving Range)'
                chart_data[station][mr_measure] = detect_phases(mr_points)
    
    return {
        'success': True,
        'chartData': chart_data,
        'stations': list(grouped.keys())
    }
```

---

### 2.3 load_actual_data.py - Multi-File CSV Loader

**File:** `load_actual_data.py`  
**Lines of Code:** ~150  
**Purpose:** Load and convert multiple CSV files from input/ folder

#### Constants:

```python
STATION_MAP = {
    'Austin': 'AUS',
    'Dallas': 'DAL',
    'Dallas Love Field': 'DAL',
    'Houston': 'HOU',
    'Houston Hobby': 'HOU'
}

MEASURE_NAMES = {
    'maintenance_cancels.csv': 'Maintenance Cancels',
    'maintenance_delays.csv': 'Maintenance Delays',
    'scheduled_maintenance_findings.csv': 'Scheduled Maintenance Findings',
    'unscheduled_maintenance.csv': 'Unscheduled Maintenance'
}
```

#### Function: infer_measure_from_filename(filename)
```python
def infer_measure_from_filename(filename):
    """
    Infer measure name from filename.
    
    Examples:
      maintenance_cancels.csv → Maintenance Cancels
      turnaround_time.csv → Turnaround Time
    """
    if filename in MEASURE_NAMES:
        return MEASURE_NAMES[filename]
    
    # Convert filename to title case
    name = filename.replace('.csv', '').replace('_', ' ').title()
    return name
```

#### Function: convert_to_spc_format(input_folder)
**Input:** Path to folder containing CSV files  
**Output:** Combined CSV string in standard format

**Algorithm:**
1. Scan folder for .csv files
2. For each file:
   - Read CSV (format: timestamp,station,metric_value)
   - Infer measure name from filename
   - Map station names using STATION_MAP
   - Convert to standard format (station,measure,date,value)
3. Combine all files into single CSV string
4. Return combined CSV

```python
def convert_to_spc_format(input_folder: str) -> str:
    """
    Convert multiple CSV files to unified SPC format.
    
    Input CSV format: timestamp,station,metric_value
    Output format: station,measure,date,value
    """
    output_lines = ['station,measure,date,value']
    
    csv_files = [f for f in os.listdir(input_folder) if f.endswith('.csv')]
    
    for filename in csv_files:
        filepath = os.path.join(input_folder, filename)
        measure = infer_measure_from_filename(filename)
        
        with open(filepath, 'r') as f:
            reader = csv.DictReader(f)
            for row in reader:
                station = STATION_MAP.get(row['station'], row['station'])
                timestamp = row['timestamp']
                value = row['metric_value']
                
                output_lines.append(f'{station},{measure},{timestamp},{value}')
    
    return '\n'.join(output_lines)
```

---

## 3. Frontend Implementation

### 3.1 dashboard_standalone.html - Single-Page Application

**File:** `dashboard_standalone.html`  
**Lines of Code:** ~900  
**Structure:** Self-contained HTML with embedded CSS and JavaScript

#### HTML Structure:

```html
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>SPC Station Health Charts</title>
    <style>
        /* Embedded CSS - ~150 lines */
    </style>
</head>
<body>
    <div id="header">...</div>
    <div id="controls">...</div>
    <div id="content">
        <!-- Charts render here -->
    </div>
    
    <script>
        // Embedded JavaScript - ~700 lines
    </script>
</body>
</html>
```

---

### 3.2 JavaScript Architecture

#### Global State:

```javascript
let chartData = null;     // Current dataset
let selectedStation = 'all';  // Station filter
```

#### Key Functions:

| Function | Purpose | Lines |
|----------|---------|-------|
| `loadActualData()` | Load test data from /api/load-actual | ~20 |
| `handleFileUpload(event)` | Process CSV file upload | ~30 |
| `updateStationSelect(stations)` | Populate station dropdown | ~15 |
| `renderCharts()` | Render all charts for selected station | ~30 |
| `drawChart(canvasId, data, title)` | Draw single chart on canvas | ~200 |
| `downloadChart(canvasId, chartName)` | Export chart as PNG | ~10 |
| `showError(message)` | Display error message | ~10 |

---

#### Function: drawChart(canvasId, data, title)

**Core Rendering Logic:**

```javascript
function drawChart(canvasId, data, title) {
    const canvas = document.getElementById(canvasId);
    if (!canvas) return;
    
    const ctx = canvas.getContext('2d');
    const { points, phases } = data;
    
    // 1. Clear canvas
    ctx.clearRect(0, 0, canvas.width, canvas.height);
    
    // 2. Calculate scales
    const padding = {top: 60, right: 40, bottom: 60, left: 70};
    const chartWidth = canvas.width - padding.left - padding.right;
    const chartHeight = canvas.height - padding.top - padding.bottom;
    
    const xScale = chartWidth / (points.length - 1);
    const yMin = Math.min(...points.map(p => p.lcl || p.value)) * 0.95;
    const yMax = Math.max(...points.map(p => p.ucl || p.value)) * 1.05;
    const yRange = yMax - yMin;
    const yScale = chartHeight / yRange;
    
    // 3. Draw axes
    ctx.strokeStyle = '#000';
    ctx.lineWidth = 2;
    ctx.beginPath();
    ctx.moveTo(padding.left, padding.top);
    ctx.lineTo(padding.left, padding.top + chartHeight);
    ctx.lineTo(padding.left + chartWidth, padding.top + chartHeight);
    ctx.stroke();
    
    // 4. Draw control limits (UCL, CL, LCL)
    if (points[0].ucl) {
        drawHorizontalLine(ctx, points[0].ucl, '#e74c3c', 'UCL', 2);
    }
    if (points[0].cl) {
        drawHorizontalLine(ctx, points[0].cl, '#3498db', 'CL', 2);
    }
    if (points[0].lcl) {
        drawHorizontalLine(ctx, points[0].lcl, '#e74c3c', 'LCL', 2);
    }
    
    // 5. Draw phase boundaries
    phases.forEach((phase, idx) => {
        if (idx > 0) {
            const x = padding.left + phase.startIndex * xScale;
            ctx.strokeStyle = '#95a5a6';
            ctx.setLineDash([5, 5]);
            ctx.beginPath();
            ctx.moveTo(x, padding.top);
            ctx.lineTo(x, padding.top + chartHeight);
            ctx.stroke();
            ctx.setLineDash([]);
        }
    });
    
    // 6. Draw data line
    ctx.strokeStyle = '#2c3e50';
    ctx.lineWidth = 2;
    ctx.beginPath();
    points.forEach((point, i) => {
        const x = padding.left + i * xScale;
        const y = padding.top + chartHeight - (point.value - yMin) * yScale;
        if (i === 0) ctx.moveTo(x, y);
        else ctx.lineTo(x, y);
    });
    ctx.stroke();
    
    // 7. Draw data points
    points.forEach((point, i) => {
        const x = padding.left + i * xScale;
        const y = padding.top + chartHeight - (point.value - yMin) * yScale;
        
        // Check if out of control
        const outOfControl = point.value > point.ucl || point.value < point.lcl;
        ctx.fillStyle = outOfControl ? '#e74c3c' : '#3498db';
        
        ctx.beginPath();
        ctx.arc(x, y, 4, 0, Math.PI * 2);
        ctx.fill();
    });
    
    // 8. Draw title
    ctx.fillStyle = '#000';
    ctx.font = 'bold 18px Arial';
    ctx.textAlign = 'center';
    ctx.fillText(title, canvas.width / 2, 30);
    
    // 9. Draw axis labels
    drawXAxisLabels(ctx, points, padding, chartWidth, chartHeight);
    drawYAxisLabels(ctx, yMin, yMax, padding, chartHeight);
}
```

**Helper Functions:**

```javascript
function drawHorizontalLine(ctx, value, color, label, lineWidth) {
    // Draw horizontal line at y = value
    const y = padding.top + chartHeight - (value - yMin) * yScale;
    ctx.strokeStyle = color;
    ctx.lineWidth = lineWidth;
    ctx.setLineDash([10, 5]);
    ctx.beginPath();
    ctx.moveTo(padding.left, y);
    ctx.lineTo(padding.left + chartWidth, y);
    ctx.stroke();
    ctx.setLineDash([]);
    
    // Draw label
    ctx.fillStyle = color;
    ctx.font = '12px Arial';
    ctx.textAlign = 'right';
    ctx.fillText(label + ': ' + value.toFixed(2), padding.left - 10, y + 4);
}

function drawXAxisLabels(ctx, points, padding, chartWidth, chartHeight) {
    ctx.fillStyle = '#000';
    ctx.font = '10px Arial';
    ctx.textAlign = 'center';
    
    const step = Math.ceil(points.length / 10);  // Show ~10 labels
    points.forEach((point, i) => {
        if (i % step === 0) {
            const x = padding.left + i * xScale;
            const y = padding.top + chartHeight + 20;
            ctx.fillText(point.date, x, y);
        }
    });
}

function drawYAxisLabels(ctx, yMin, yMax, padding, chartHeight) {
    ctx.fillStyle = '#000';
    ctx.font = '10px Arial';
    ctx.textAlign = 'right';
    
    const numLabels = 5;
    const step = (yMax - yMin) / (numLabels - 1);
    
    for (let i = 0; i < numLabels; i++) {
        const value = yMin + i * step;
        const y = padding.top + chartHeight - i * (chartHeight / (numLabels - 1));
        ctx.fillText(value.toFixed(1), padding.left - 10, y + 4);
    }
}
```

---

#### Function: downloadChart(canvasId, chartName)

**PNG Export:**

```javascript
function downloadChart(canvasId, chartName) {
    const canvas = document.getElementById(canvasId);
    if (!canvas) return;
    
    // Convert canvas to PNG data URL
    const dataURL = canvas.toDataURL('image/png');
    
    // Create temporary download link
    const link = document.createElement('a');
    link.download = `${chartName.replace(/[^a-zA-Z0-9]/g, '_')}.png`;
    link.href = dataURL;
    link.click();
}
```

---

## 4. Data Structures

### 4.1 JSON API Response

```json
{
  "success": true,
  "chartData": {
    "DAL": {
      "Maintenance Cancels": {
        "points": [
          {
            "station": "DAL",
            "measure": "Maintenance Cancels",
            "date": "2023-01-02",
            "value": 3.2,
            "ucl": 5.1,
            "cl": 3.0,
            "lcl": 0.9
          }
        ],
        "phases": [
          {
            "startIndex": 0,
            "endIndex": 45,
            "cl": 3.0,
            "ucl": 5.1,
            "lcl": 0.9,
            "phaseNumber": 1
          }
        ]
      }
    }
  },
  "stations": ["AUS", "DAL", "HOU"]
}
```

---

## 5. Performance Optimizations

### 5.1 Backend Optimizations

**1. List Comprehensions (Python):**
```python
# Fast
moving_ranges = [abs(values[i] - values[i-1]) for i in range(1, len(values))]

# Slow
moving_ranges = []
for i in range(1, len(values)):
    moving_ranges.append(abs(values[i] - values[i-1]))
```

**2. Single-Pass CSV Parsing:**
- Parse CSV once, group by station/measure in single loop
- Avoid multiple passes over data

**3. Minimal Data Transfer:**
- Return only necessary data in JSON
- Round decimals to 2 places (reduce size)

---

### 5.2 Frontend Optimizations

**1. Canvas Rendering (vs DOM manipulation):**
- Canvas: Direct pixel manipulation, GPU accelerated
- DOM: Slow, causes reflows, memory intensive

**2. Debounced Resize Events:**
```javascript
let resizeTimer;
window.addEventListener('resize', () => {
    clearTimeout(resizeTimer);
    resizeTimer = setTimeout(() => {
        renderCharts();  // Redraw after resize stops
    }, 250);
});
```

**3. Lazy Loading:**
- Only render charts for selected station
- Don't render hidden charts

---

## 6. Security Considerations

### 6.1 Threat Model

**Risk Level:** Low (localhost-only desktop tool)

**Threats Accepted:**
1. **CSV Injection:** Malicious CSV could contain formulas → Not applicable (no Excel output)
2. **Path Traversal:** User could upload CSV with path tricks → Mitigated by reading file content only
3. **XSS:** Malicious data in charts → Mitigated by Canvas rendering (not innerHTML)
4. **DOS:** Large CSV could crash browser → Accepted (user's own machine)

**Threats Mitigated:**
1. **CORS:** Only localhost origin allowed
2. **File System Access:** Python only reads from input/ folder
3. **SQL Injection:** N/A (no database)

---

## 7. Testing Strategy

### 7.1 Unit Tests (Not Implemented - V1.0)

**Would Test:**
- `calculate_initial_limits()` - Various input sizes
- `find_phase_end()` - Rule #1 and #4 scenarios
- `detect_phases()` - Single phase, multiple phases, edge cases
- `parse_csv()` - Valid and invalid CSV formats

**Testing Framework:** `unittest` (Python stdlib)

---

### 7.2 Manual Testing (Performed)

**Test Cases:**

| ID | Description | Expected | Actual | Status |
|----|-------------|----------|--------|--------|
| T01 | Load test data | 24 charts display | 24 charts | ✅ Pass |
| T02 | Upload Format A CSV | Charts display, filename = measure | Correct | ✅ Pass |
| T03 | Upload Format B CSV | Charts display, measure from column | Correct | ✅ Pass |
| T04 | Upload invalid CSV | Error message | "No valid data points" | ✅ Pass |
| T05 | Export PNG | File downloads | PNG in Downloads folder | ✅ Pass |
| T06 | Phase detection | Phases marked correctly | Matches Wheeler's Rules | ✅ Pass |
| T07 | Station filter | Only selected station charts | Correct filtering | ✅ Pass |
| T08 | Port conflict | Clear error message | Address in use error | ✅ Pass |

---

## 8. Deployment

### 8.1 Build Process

**No build step required!**
- No transpilation (no Babel/TypeScript)
- No bundling (no Webpack/Vite)
- No minification
- No dependency installation

### 8.2 Distribution

**Steps:**
1. Ensure all files committed to git
2. Push to GitHub
3. Create ZIP file of repository
4. Distribute ZIP to users

**Distribution Package Contents:**
```
SPC-Station-Health-Charts.zip
├── dashboard_standalone.html
├── server.py
├── spc_processor.py
├── load_actual_data.py
├── START_DASHBOARD.bat
├── start_dashboard.sh
├── README.md
├── README_DISTRIBUTION.md
├── input/
│   └── (4 CSV files)
└── .gitignore
```

---

## 9. Maintenance & Support

### 9.1 Common Issues

**Issue:** Port 8000 in use  
**Solution:** Edit `server.py`, change `PORT = 8000` to `PORT = 8001`

**Issue:** Python not found  
**Solution:** Install Python 3.7+ from python.org

**Issue:** Browser doesn't open  
**Solution:** Manually navigate to `http://localhost:8000`

**Issue:** Charts not loading  
**Solution:** Check browser console (F12) for JavaScript errors

---

### 9.2 Future Technical Debt

**Known Limitations:**
1. **No automated tests** - Reliant on manual testing
2. **Hardcoded port** - Should be configurable via command-line arg
3. **Canvas rendering** - Could use WebGL for better performance (100+ charts)
4. **Error handling** - Some edge cases not fully covered
5. **No logging framework** - Just print statements

**Refactoring Opportunities:**
1. Extract chart rendering to separate module
2. Add command-line arguments (port, input folder, etc.)
3. Implement proper logging (Python `logging` module)
4. Add configuration file (JSON/YAML)

---

## 10. Version History

| Version | Date | Changes | Lines Changed |
|---------|------|---------|---------------|
| 0.1 | 2025-09-28 | Initial React + Recharts version | N/A |
| 0.2 | 2025-10-01 | Fixed infinite render loop | ~20 |
| 0.3 | 2025-10-02 | Switched to standalone HTML + Canvas | ~900 (rewrite) |
| 0.4 | 2025-10-04 | Fixed phase detection (Wheeler's Rules) | ~150 |
| 0.5 | 2025-10-05 | Added XmR charts (both X and mR) | ~100 |
| **1.0** | **2025-10-06** | **Production release** | **~1600 total** |

---

## Approval

| Role | Name | Date | Signature |
|------|------|------|-----------|
| Tech Lead | Development Team | 2025-10-06 | ✅ Approved |
| Code Reviewer | Senior Developer | 2025-10-06 | ✅ Reviewed |

---

**Document Version History**

| Version | Date | Author | Changes |
|---------|------|--------|---------|
| 1.0 | 2025-10-06 | Development Team | Initial technical specification |
| 1.4 | 2025-10-07 | Development Team | Debug logging, CSV troubleshooting tools, enhanced error reporting |

