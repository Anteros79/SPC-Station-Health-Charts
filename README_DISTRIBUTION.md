# 📊 SPC Station Health Charts

Statistical Process Control (SPC) Dashboard for Airline Maintenance Metrics

## ✅ Requirements

- **Python 3.7+** (that's it!)
- No admin rights needed
- No web server installation required
- Works on Windows, Mac, and Linux

## 🚀 Quick Start

### Windows
1. **Extract** the zip file to your desktop or any folder
2. **Double-click** `START_DASHBOARD.bat`
3. Your browser will open automatically to the dashboard
4. Click **"Load Test Data"** to see sample charts

### Mac/Linux
1. **Extract** the zip file
2. Open Terminal and navigate to the folder
3. Run: `./start_dashboard.sh`
4. Open your browser to: `http://localhost:8000`

## 📁 What's Included

```
SPC-Station-Health-Charts/
├── dashboard_standalone.html    # Main dashboard interface
├── server.py                    # Local Python server
├── spc_processor.py            # Statistical calculations
├── load_actual_data.py         # Data processing
├── START_DASHBOARD.bat         # Windows launcher
├── start_dashboard.sh          # Mac/Linux launcher
├── input/                      # Sample CSV files
│   ├── maintenance_cancels.csv
│   ├── maintenance_delays.csv
│   ├── scheduled_maintenance_findings.csv
│   └── unscheduled_maintenance.csv
└── output/                     # Your exported PNG charts go here
```

## 📊 Using Your Own Data

### Option 1: Replace Sample Files
Replace the CSV files in the `input/` folder with your own data.

**Required CSV Format:**
```csv
timestamp,station,metric_value
2023-01-02,Austin,2.5
2023-01-02,Dallas,3.1
2023-01-09,Austin,2.8
```

### Option 2: Upload Individual Files
Click **"Upload CSV"** in the dashboard to analyze a single file.

**Supported Formats:**
- `timestamp,station,metric_value` (filename becomes measure name)
- `station,measure,date,value` (standard format)

## 📈 Features

### Statistical Methods
- **Wheeler's XmR Charts** - Individuals (X), Moving Range (mR), and Distribution charts
- **Natural Process Limits** - 2.66 sigma control limits
- **Automatic Phase Detection** - Detects process shifts using:
  - Rule #1: Points beyond control limits
  - Rule #4: 7 consecutive points on one side of centerline
- **Distribution Analysis** - Histogram with normal curve overlay to assess data normality
- **Chart Grouping** - All three charts (X, mR, Distribution) for each measure appear together

### Export
- **Save as PNG** - Click the download button on any chart
- Charts save to the `output/` folder automatically

### Data Coverage
- Sample data spans **January 2023 to present**
- Covers **3 stations**: Austin (AUS), Dallas (DAL), Houston (HOU)
- Tracks **4 measures**:
  - Maintenance Cancels
  - Maintenance Delays
  - Scheduled Maintenance Findings
  - Unscheduled Maintenance

## 🔧 Troubleshooting

### "Connection Refused" Error
**Solution:** Make sure `server.py` is running. Double-click `START_DASHBOARD.bat` again.

### Charts Not Loading
**Solution:** Check that your CSV files are in the correct format (see above).

### Port Already in Use
**Solution:** Close other applications using port 8000, or edit `server.py` and change:
```python
PORT = 8000  # Change to 8001, 8002, etc.
```

### Server Won't Stop
**Windows:** Close the Command Prompt window
**Mac/Linux:** Press `Ctrl+C` in the Terminal

## 📝 Notes

- Keep the Command Prompt/Terminal window **open** while using the dashboard
- The server runs **locally only** - no internet connection required
- Your data **never leaves your computer**
- All calculations happen in your browser

## 🆘 Support

If you encounter issues:
1. Check that Python is installed: `python --version`
2. Make sure no other program is using port 8000
3. Try restarting your computer
4. Contact your technical lead

## 📚 More Information

For technical details about the SPC methodology used, see:
- Wheeler, Donald J. "Understanding Variation: The Key to Managing Chaos" (2000)
- Wheeler's Rules for detecting special causes of variation

---

**Built with:** Python, HTML5 Canvas, Statistical Process Control
**License:** Internal use only
**Version:** 1.5.1 (October 2025)

