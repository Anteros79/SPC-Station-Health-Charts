# SPC Dashboard Developer Guide

## 🏗️ Architecture Overview

The SPC Dashboard is a client-server application built with Python's built-in HTTP server and vanilla JavaScript. It implements Statistical Process Control (SPC) methodology using Wheeler's XmR charts and rules.

### Core Components

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Frontend      │    │   Backend       │    │   Data Layer    │
│                 │    │                 │    │                 │
│ dashboard_      │◄──►│ server.py       │◄──►│ CSV Files       │
│ standalone.html │    │                 │    │                 │
│                 │    │ spc_processor.py│    │ input/          │
│ Plotly.js       │    │                 │    │ output/         │
│ Canvas API      │    │ load_actual_    │    │                 │
│                 │    │ data.py         │    │                 │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

## 📁 File Structure

```
airline-tech-ops-spc-dashboard/
├── dashboard_standalone.html    # Main UI (HTML + CSS + JavaScript)
├── server.py                    # HTTP server + API endpoints
├── spc_processor.py            # SPC calculations + phase detection
├── load_actual_data.py         # CSV data processing utilities
├── input/                      # Sample CSV data files
├── output/                     # Exported PNG charts
├── README.md                   # User documentation
├── SPC_Rules_and_Odds.html     # Technical SPC documentation
├── Explainer_File.html         # User guide
└── DEVELOPER_GUIDE.md          # This file
```

## 🔧 Backend Architecture

### server.py

**Purpose:** HTTP server and API endpoints

**Key Functions:**
- `process_csv_data()` - Main API endpoint for CSV processing
- `validate_csv_format()` - CSV format validation
- `auto_convert_csv_format()` - Automatic format conversion
- `serve_static_files()` - Static file serving

**API Endpoints:**
- `POST /api/process` - Process uploaded CSV data
- `GET /api/ping` - Health check
- `GET /*` - Serve static files

**Error Handling:**
```python
try:
    # Process CSV data
    result = process_csv_data(csv_content, filename)
    return json.dumps(result)
except Exception as e:
    return json.dumps({"error": str(e)})
```

### spc_processor.py

**Purpose:** Statistical calculations and phase detection

**Key Classes:**
- `SPCProcessor` - Main processing class

**Key Methods:**
- `process_data()` - Main data processing pipeline
- `detect_phases()` - Phase detection using Wheeler's rules
- `find_phase_end()` - Signal detection logic
- `calculate_initial_limits()` - Control limit calculations
- `generate_histogram()` - Distribution chart data

**Wheeler's Rules Implementation:**
```python
# Rule #1: Point outside control limits
if value > ucl or value < lcl:
    return max(0, i - 1)

# Rule #2: 2 of 3 beyond 2σ on same side
count_upper = sum(1 for v in recent_values if v >= two_sigma_upper)
if count_upper >= 2:
    return max(0, i - 2)

# Rule #4: 7 consecutive on one side
if consecutive_above >= 7 or consecutive_below >= 7:
    return max(0, i - 7)
```

## 🎨 Frontend Architecture

### dashboard_standalone.html

**Structure:**
- **HTML:** Chart containers and UI elements
- **CSS:** Southwest Airlines branding and responsive design
- **JavaScript:** Chart rendering and user interactions

**Key JavaScript Functions:**

#### Chart Rendering
```javascript
function renderCharts() {
    // Determine mode (weekly vs daily)
    const hasDailyData = Object.values(allData).some(station => 
        Object.values(station).some(measure => 
            measure.measure.includes('(Daily Bar)')
        )
    );
    
    if (hasDailyData) {
        // Daily Mode: Plotly.js charts
        renderDailyMode();
    } else {
        // Weekly Mode: Canvas-based SPC charts
        renderWeeklyMode();
    }
}
```

#### Weekly Mode (Canvas)
```javascript
function drawXChart(canvasId, data, station, measure) {
    const canvas = document.getElementById(canvasId);
    const ctx = canvas.getContext('2d');
    
    // Draw chart elements
    drawGrid(ctx, width, height);
    drawControlLimits(ctx, ucl, lcl, cl);
    drawDataPoints(ctx, points);
    drawPhaseBoundaries(ctx, phases);
}
```

#### Daily Mode (Plotly.js)
```javascript
function renderDailyPlotlyChart(containerId, data, station, measure) {
    // Extract data
    const dates = points.map(p => new Date(p.date));
    const values = points.map(p => parseFloat(p.value));
    
    // Calculate statistics
    const mean = values.reduce((sum, v) => sum + v, 0) / values.length;
    const stdDev = Math.sqrt(values.reduce((sum, v) => sum + Math.pow(v - mean, 2), 0) / (values.length - 1));
    const ucl = mean + 3 * stdDev;
    const lcl = mean - 3 * stdDev;
    
    // Create traces
    const barTrace = {
        x: dates,
        y: values,
        type: 'bar',
        marker: { color: colors }
    };
    
    // Render with Plotly
    Plotly.newPlot(containerId, [barTrace, meanTrace, uclTrace, lclTrace], layout, config);
}
```

## 📊 Data Flow

### 1. CSV Upload
```
User uploads CSV → server.py → validate_csv_format() → auto_convert_csv_format() → spc_processor.py
```

### 2. Data Processing
```
CSV data → SPCProcessor.process_data() → detect_phases() → calculate_limits() → JSON response
```

### 3. Chart Rendering
```
JSON data → renderCharts() → mode detection → Canvas/Plotly rendering → User interaction
```

## 🎯 Key Features Implementation

### Phase Zoom Control

**Backend (spc_processor.py):**
```python
def filter_to_last_n_phases(data, num_phases):
    """Filter data to show only the last N phases"""
    if not data.get('phases'):
        return data
    
    # Get last N phases
    last_phases = data['phases'][-num_phases:]
    
    # Filter points to only include those in the selected phases
    filtered_points = []
    for phase in last_phases:
        filtered_points.extend(phase['points'])
    
    return {
        'points': filtered_points,
        'phases': last_phases,
        'measure': data['measure']
    }
```

**Frontend (dashboard_standalone.html):**
```javascript
function updatePhaseSlider(containerId, numPhases) {
    // Update display
    const valueDisplay = document.getElementById(`phase-value-${containerId}`);
    valueDisplay.textContent = `${numPhases} phase${numPhases !== 1 ? 's' : ''}`;
    
    // Re-render charts with filtered data
    const station = containerId.split('-')[0];
    const measure = containerId.split('-')[1];
    const data = chartData[station][measure];
    
    // Filter data to last N phases
    const filteredData = filterToLastNPhases(data, numPhases);
    
    // Re-render charts
    renderChartGroup(containerId, filteredData, station, measure);
}
```

### Daily Chart Slider Control

**Frontend Implementation:**
```javascript
function updateDailySlider(containerId, numDays) {
    // Update display
    const valueDisplay = document.getElementById(`daily-value-${containerId}`);
    valueDisplay.textContent = `${numDays} day${numDays !== 1 ? 's' : ''}`;
    
    // Get chart data
    const chartDiv = document.getElementById(containerId);
    const allDates = chartDiv.data[0].x;
    
    // Calculate new range (last N days)
    const endDate = allDates[allDates.length - 1];
    const startDate = allDates[Math.max(0, allDates.length - numDays)];
    
    // Update Plotly chart range
    Plotly.relayout(containerId, {
        'xaxis.range': [startDate, endDate]
    });
    
    // Update synchronized table
    updateDailyDataTable(containerId, visiblePoints);
}
```

### Weekend Day Highlighting

**Implementation:**
```javascript
const xAxisLabels = dates.map(d => {
    const dayOfWeek = d.getDay();
    const isWeekend = dayOfWeek === 0 || dayOfWeek === 6;
    const dayAbbr = d.toLocaleDateString('en-US', { weekday: 'short' });
    const dateStr = d.toLocaleDateString('en-US', { month: '2-digit', day: '2-digit' });
    
    // Color weekends in Southwest red
    const color = isWeekend ? '#C4122F' : '#304CB2';
    return `<span style="color:${color}">${dayAbbr}</span><br>${dateStr}`;
});
```

## 🎨 Styling and Branding

### Southwest Airlines Color Palette

```css
:root {
    --swa-blue: #304CB2;      /* Primary brand color */
    --swa-yellow: #FFBF27;    /* Accent color */
    --swa-red: #C4122F;       /* Weekend highlighting */
    --swa-gray: #6B7280;      /* Muted text */
    --swa-light-gray: #F9FAFB; /* Background */
}
```

### Responsive Design

```css
.chart-container {
    width: 100%;
    max-width: 1200px;
    margin: 0 auto;
    background: white;
    border-radius: 8px;
    box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
}

@media (max-width: 768px) {
    .chart-container {
        margin: 0 1rem;
    }
}
```

## 🔍 Debugging and Development

### Console Logging

**Backend Debugging:**
```python
import logging
logging.basicConfig(level=logging.DEBUG)

def process_csv_data(csv_content, filename):
    logging.debug(f"Processing file: {filename}")
    logging.debug(f"CSV content length: {len(csv_content)}")
    # ... processing logic
```

**Frontend Debugging:**
```javascript
function renderDailyPlotlyChart(containerId, data, station, measure) {
    console.log('Chart data:', { dates, values, pointsCount: points.length });
    console.log('Rendering chart with traces:', [barTrace, meanTrace, uclTrace, lclTrace]);
    
    Plotly.newPlot(chartDiv, traces, layout, config)
        .then(() => {
            console.log('Chart rendered successfully');
        })
        .catch(error => {
            console.error('Error rendering chart:', error);
        });
}
```

### CSV Format Debugging

**Built-in CSV Format Checker:**
- Navigate to `http://localhost:8000/csv_format_checker.html`
- Paste CSV content to diagnose format issues
- Get specific fix suggestions

### Error Handling

**Backend Error Handling:**
```python
try:
    result = process_csv_data(csv_content, filename)
    return json.dumps(result)
except ValueError as e:
    return json.dumps({"error": f"Data validation error: {str(e)}"})
except Exception as e:
    logging.error(f"Unexpected error: {str(e)}", exc_info=True)
    return json.dumps({"error": f"Processing failed: {str(e)}"})
```

**Frontend Error Handling:**
```javascript
try {
    renderDailyPlotlyChart(canvasId, data, station, baseMeasure);
} catch (error) {
    console.error('Error rendering Plotly chart:', error);
    const container = document.getElementById(canvasId);
    if (container) {
        container.innerHTML = `
            <div style="padding: 2rem; text-align: center; color: #C4122F;">
                <p style="font-weight: 600;">Chart Rendering Error</p>
                <p style="font-size: 0.875rem; color: #6B7280;">
                    Unable to display chart. Please try refreshing the page.
                </p>
            </div>
        `;
    }
}
```

## 🧪 Testing

### Unit Testing

**Backend Tests:**
```python
import unittest
from spc_processor import SPCProcessor

class TestSPCProcessor(unittest.TestCase):
    def test_phase_detection(self):
        processor = SPCProcessor()
        test_data = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
        result = processor.detect_phases(test_data)
        self.assertIsNotNone(result)
        self.assertIn('phases', result)
```

**Frontend Tests:**
```javascript
// Test chart rendering
function testChartRendering() {
    const testData = {
        points: [
            {date: '2023-01-01', value: 1.5},
            {date: '2023-01-02', value: 2.0}
        ]
    };
    
    try {
        renderDailyPlotlyChart('test-container', testData, 'TEST', 'Test Measure');
        console.log('Chart rendering test passed');
    } catch (error) {
        console.error('Chart rendering test failed:', error);
    }
}
```

### Integration Testing

**CSV Upload Testing:**
1. Test with valid CSV files
2. Test with invalid formats
3. Test with empty files
4. Test with large files

**Chart Interaction Testing:**
1. Test phase slider functionality
2. Test daily slider functionality
3. Test zoom/pan interactions
4. Test PNG export functionality

## 🚀 Deployment

### Local Development

```bash
# Start development server
python server.py

# Access dashboard
open http://localhost:8000
```

### Production Deployment

**Requirements:**
- Python 3.7+
- Modern web browser
- No external dependencies

**Deployment Steps:**
1. Copy all files to target directory
2. Ensure Python is installed
3. Run `python server.py`
4. Configure firewall for port 8000 (or change port in server.py)

### Docker Deployment (Optional)

```dockerfile
FROM python:3.9-slim

WORKDIR /app
COPY . .

EXPOSE 8000
CMD ["python", "server.py"]
```

## 📚 API Reference

### POST /api/process

**Request:**
```json
{
    "csv_content": "timestamp,station,metric_value\n2023-01-01,AUS,1.5",
    "filename": "test_data.csv"
}
```

**Response:**
```json
{
    "success": true,
    "data": {
        "AUS": {
            "Test Measure": {
                "points": [...],
                "phases": [...],
                "measure": "Test Measure"
            }
        }
    }
}
```

**Error Response:**
```json
{
    "error": "Invalid CSV format: missing required columns"
}
```

### GET /api/ping

**Response:**
```json
{
    "status": "ok",
    "timestamp": "2023-10-13T21:30:00Z"
}
```

## 🔧 Configuration

### Server Configuration

**server.py:**
```python
PORT = 8000  # Change port if needed
HOST = 'localhost'  # Change to '0.0.0.0' for external access
```

### Chart Configuration

**Weekly Charts:**
```javascript
const CHART_CONFIG = {
    width: 1200,
    height: 400,
    aspectRatio: 16/9,
    colors: {
        inControl: '#304CB2',
        outOfControl: '#C4122F',
        centerLine: '#6B7280'
    }
};
```

**Daily Charts:**
```javascript
const PLOTLY_CONFIG = {
    responsive: true,
    displayModeBar: true,
    toImageButtonOptions: {
        format: 'png',
        height: 600,
        width: 1200,
        scale: 2
    }
};
```

## 🐛 Common Issues and Solutions

### Issue: Charts Not Rendering

**Symptoms:** Blank chart areas, JavaScript errors in console

**Solutions:**
1. Check browser console for errors
2. Verify server is running
3. Check CSV data format
4. Clear browser cache

### Issue: CSV Upload Fails

**Symptoms:** "Upload Failed" error message

**Solutions:**
1. Use CSV format checker tool
2. Verify date format (YYYY-MM-DD)
3. Check for empty rows
4. Ensure numeric values are valid

### Issue: Phase Slider Not Working

**Symptoms:** Slider moves but charts don't update

**Solutions:**
1. Check browser console for JavaScript errors
2. Verify chartData is populated
3. Check container ID matching

### Issue: Daily Chart Bars Missing

**Symptoms:** Chart renders but no bars visible

**Solutions:**
1. Check Plotly.js CDN loading
2. Verify data extraction
3. Check bar trace configuration
4. Look for console errors

## 📈 Performance Optimization

### Backend Optimization

```python
# Use efficient data structures
from collections import defaultdict

# Cache frequently used calculations
@lru_cache(maxsize=128)
def calculate_limits(values):
    # ... calculation logic
```

### Frontend Optimization

```javascript
// Debounce expensive operations
let relayoutTimer;
chartDiv.on('plotly_relayout', function(eventData) {
    clearTimeout(relayoutTimer);
    relayoutTimer = setTimeout(() => {
        // Update table and stats
    }, 150);
});

// Use requestAnimationFrame for smooth animations
function animateChart() {
    requestAnimationFrame(() => {
        // Chart animation logic
    });
}
```

## 🔒 Security Considerations

### Data Privacy

- **100% Local Processing:** All data stays on user's machine
- **No Cloud Services:** No data sent to external servers
- **No Authentication:** No user accounts or API keys required
- **No Telemetry:** No data collection or analytics

### Input Validation

```python
def validate_csv_content(csv_content):
    """Validate CSV content for security"""
    if len(csv_content) > 10 * 1024 * 1024:  # 10MB limit
        raise ValueError("File too large")
    
    # Check for malicious content
    if '<script' in csv_content.lower():
        raise ValueError("Invalid content detected")
    
    return True
```

## 📝 Contributing

### Code Style

**Python:**
- Follow PEP 8
- Use type hints where appropriate
- Add docstrings for functions

**JavaScript:**
- Use consistent indentation (2 spaces)
- Use meaningful variable names
- Add comments for complex logic

### Pull Request Process

1. Fork the repository
2. Create feature branch
3. Make changes with tests
4. Update documentation
5. Submit pull request

### Testing Requirements

- All new features must have tests
- Existing tests must pass
- Manual testing on multiple browsers
- Performance impact assessment

---

**Version:** 2.0  
**Last Updated:** October 13, 2025  
**Maintained by:** Southwest Airlines Technical Operations Analytics Team
