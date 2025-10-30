# Southwest Airlines Tech Ops SPC Dashboard

**Version 2.1 - True Offline Capability**

Statistical Process Control (SPC) Dashboard for Airline Maintenance Metrics using Wheeler's XmR methodology.

## 🎯 Overview

Professional desktop tool for monitoring maintenance performance across multiple airline stations. Implements Wheeler's Rules for detecting process shifts and calculating Natural Process Limits with complete offline capability.

**Key Features:**
- ✅ **True Offline Operation** - Zero internet requirements, works in air-gapped environments
- ✅ **Local Plotly.js Library** - Professional charting with no CDN dependencies
- ✅ **Zero external dependencies** - Python standard library only
- ✅ **No web server installation required** - Uses Python's built-in http.server
- ✅ **Wheeler's XmR Charts** - Both Individuals (X) and Moving Range (mR)
- ✅ **Interactive Daily Bar Charts** - Plotly.js charts with zoom/pan and slider control
- ✅ **Automatic phase detection** - Rule #1 (points beyond limits), Rule #2 (2 of 3 beyond 2σ), and Rule #4 (7-point runs)
- ✅ **Phase zoom control** - Slider to focus on recent phases (default: all phases from Jan 2023)
- ✅ **PNG export** - Save charts for reports and presentations
- ✅ **Comprehensive Testing** - Automated offline functionality validation
- ✅ **CSV troubleshooting tools** - Built-in format checker and debug logging
- ✅ **Southwest Airlines branding** - Unified SWA blue/red/yellow theme across docs and UI
- ✅ **Executive-ready layout** - Widescreen 16:9 format for presentations

## 📋 Requirements

- **Python 3.7+** (standard library only - no pip packages needed)
- **Modern web browser** (Chrome, Edge, Firefox, Safari)
- **No admin rights required**
- **No API keys required**
- **No internet connection required** (runs completely offline with local Plotly.js v2.27.0)
- **Storage:** Additional 3.4MB for bundled JavaScript libraries

## 🚀 Quick Start

### Windows
```bash
# Extract the project folder
# Double-click START_DASHBOARD.bat
```

### Mac/Linux
```bash
# Extract the project folder
# Open Terminal in project folder
chmod +x start_dashboard.sh
./start_dashboard.sh
```

The dashboard will automatically open in your browser at `http://localhost:8000`

## 🔧 Troubleshooting CSV Uploads

If you're having trouble uploading CSV files, use the built-in troubleshooting tools:

### **CSV Format Checker**
- Navigate to `http://localhost:8000/csv_format_checker.html`
- Paste your CSV content to diagnose format issues
- Get specific fix suggestions for common problems

### **Debug Logging**
- Check the server console (Command Prompt window) for detailed error messages
- Shows exactly what's wrong with your CSV format
- Identifies decimal format issues (commas vs. periods)

## 📁 Project Structure

```
SPC-Station-Health-Charts/
├── dashboard_standalone.html      # Main dashboard UI
├── server.py                      # Python HTTP server + debug logging
├── spc_processor.py              # Statistical calculations + debug logging
├── load_actual_data.py           # CSV data processing
├── csv_format_checker.html       # CSV diagnostic tool
├── logotest.html                 # Logo comparison gallery
├── START_DASHBOARD.bat           # Windows launcher
├── start_dashboard.sh            # Mac/Linux launcher
├── input/                        # Sample CSV files
│   ├── maintenance_cancels.csv
│   ├── maintenance_delays.csv
│   ├── scheduled_maintenance_findings.csv
│   └── unscheduled_maintenance.csv
└── output/                       # Exported PNG charts
```

## 📊 Using the Dashboard

### Load Sample Data
1. Click **"Load Test Data"** to view sample maintenance metrics
2. Data includes 3 stations (AUS, DAL, HOU) from Jan 2023 to present
3. **Weekly Mode:** View 4 maintenance measures with X chart, mR chart, and Distribution chart grouped together
4. **Daily Mode:** View daily bar charts with interactive zoom/pan and 7-30 day slider control

### Upload Your Own Data

**Supported CSV Formats:**

**Format 1** (filename becomes measure name):
```csv
timestamp,station,metric_value
2023-01-02,Austin,2.5
2023-01-02,Dallas,3.1
2023-01-09,Austin,2.8
```

**Format 2** (standard format):
```csv
station,measure,date,value
AUS,Maintenance Cancels,2023-01-02,2.5
DAL,Maintenance Cancels,2023-01-02,3.1
AUS,Maintenance Cancels,2023-01-09,2.8
```

The dashboard automatically detects which format you're using.

### Export Charts
- Click the **"Save PNG"** button on any chart
- Charts save to your Downloads folder
- High resolution, suitable for presentations
- Footer stamp removed for executive-ready images

## 📈 Statistical Methodology

### Wheeler's XmR Charts (Weekly Mode)
- **X Chart (Individuals):** Monitors process location (average)
- **mR Chart (Moving Range):** Monitors process variation (consistency)
- **Distribution Chart:** Histogram with normal curve overlay; linked to phase slider, auto-bins filtered X values

### Daily Bar Charts (Daily Mode)
- **Interactive Plotly.js charts** with smooth zoom and pan capabilities
- **7-30 day slider control** for explicit date range selection
- **Weekend day highlighting** with Southwest Airlines red coloring
- **Dynamic control limits** calculated from visible data only
- **Synchronized data table** that updates with chart zoom/pan
- **Southwest Airlines branding** with proper color scheme

### Natural Process Limits (NPL)
- **Sigma:** 2.66 (natural process limits)
- **UCL:** Center Line + 2.66 × mR̄
- **LCL:** Center Line - 2.66 × mR̄ (minimum 0)

### Phase Detection
**Wheeler's Rules implemented:**
- **Rule #1:** Point beyond control limits (outside UCL/LCL)
- **Rule #2:** 2 of 3 consecutive points beyond 2σ on the same side of centerline
- **Rule #4:** 7 consecutive points on one side of centerline

When a signal is detected:
1. Current phase ends
2. New phase begins
3. Control limits recalculate based on new phase data

### Baseline Methodology
1. Start with minimum 20 points to establish baseline
2. Calculate limits from baseline data ONLY
3. Monitor subsequent data for signals
4. Recalculate limits when phase changes

## 🔧 Troubleshooting

### Port Already in Use
If port 8000 is already taken, edit `server.py`:
```python
PORT = 8001  # Change to any available port
```

### Server Won't Start
- Check Python is installed: `python --version` or `python3 --version`
- Make sure no other Python server is running
- Try closing and reopening the terminal/command prompt

### Charts Not Loading
- Make sure `server.py` is still running (don't close the terminal window)
- Try refreshing the browser
- Check browser console for errors (F12 key)

### CSV Upload Error
- Verify CSV format matches one of the supported formats above
- Check that date format is YYYY-MM-DD
- Ensure numeric values are valid numbers (not text)

## 🔒 Data Privacy & Security

- **100% Local:** All data processing happens on your computer
- **No cloud services:** No data sent to external servers
- **No API keys:** No accounts or authentication required
- **No internet required:** Works completely offline
- **No data collection:** No telemetry or analytics

Perfect for regulated environments and sensitive data.

## 📚 References

- Wheeler, Donald J. "Understanding Variation: The Key to Managing Chaos" (2000)
- Wheeler's Rules for detecting special causes of variation
- Statistical Process Control (SPC) best practices

## 🤝 Contributing

This is an internal tool. For questions or issues, contact your technical operations team.

## 📄 License

Internal use only - Airline Technical Operations

---

**Version:** 2.0  
**Last Updated:** October 13, 2025  
**Maintained by:** Southwest Airlines Technical Operations Analytics Team
