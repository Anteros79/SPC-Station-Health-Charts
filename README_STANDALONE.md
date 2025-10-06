# Airline Tech Ops SPC Dashboard - Standalone Version

**No installation required!** Just Python and a web browser.

This is a self-contained Statistical Process Control (SPC) dashboard for monitoring airline technical operations. It runs entirely on your local machine with no internet connection required (after initial load).

---

## 🚀 Quick Start (Windows)

### Simplest Method:
1. **Double-click** `START_DASHBOARD.bat`
2. Wait for browser to open
3. Click "Load Demo" or upload your CSV file

That's it! 🎉

---

## 🚀 Quick Start (macOS/Linux)

### Simplest Method:
1. Open Terminal
2. Navigate to this folder: `cd /path/to/this/folder`
3. Run: `bash start_dashboard.sh`
4. Wait for browser to open
5. Click "Load Demo" or upload your CSV file

---

## 📋 Manual Setup (If batch file doesn't work)

### Step 1: Start the Python Server
Open Command Prompt (Windows) or Terminal (macOS/Linux) and run:

**Windows:**
```cmd
python server.py
```

**macOS/Linux:**
```bash
python3 server.py
```

You should see:
```
╔════════════════════════════════════════════════════════════╗
║  Airline Tech Ops SPC Dashboard Server                    ║
╚════════════════════════════════════════════════════════════╝

✓ Server running on: http://localhost:8000
```

**⚠️ IMPORTANT:** Keep this window open while using the dashboard!

### Step 2: Open the Dashboard
- Double-click `dashboard.html` to open it in your web browser
- Or drag and drop it into your browser window

### Step 3: Use the Dashboard
- Click **"Load Demo"** to see sample data
- Or click **"Upload CSV"** to use your own data

---

## 📊 CSV File Format

Your CSV file must have these columns:

```csv
station,measure,date,value
JFK,Turnaround Time,2024-01-01,45.5
JFK,Turnaround Time,2024-01-02,47.2
LAX,Baggage Handling Errors,2024-01-01,3.1
```

**Required Columns:**
- `station` - Airport code (e.g., JFK, LAX, ORD)
- `measure` - Metric name (e.g., "Turnaround Time", "Baggage Handling Errors")
- `date` - Date in YYYY-MM-DD format
- `value` - Numeric value

---

## 🎯 Features

✅ **Statistical Process Control (SPC) Charts**
- Automatically detects process phases
- Calculates control limits (UCL, CL, LCL)
- Identifies process shifts using 8-point run rule

✅ **Multi-Station Monitoring**
- View all stations at once or individually
- Add custom stations on the fly

✅ **Multiple Measures**
- Track different metrics per station
- Each measure gets its own control chart

✅ **No Installation Required**
- Uses Python's built-in libraries only
- All UI libraries loaded from CDN

---

## 🛠️ Requirements

- **Python 3.7+** (no additional packages needed!)
- **Web Browser** (Chrome, Firefox, Edge, Safari)
- **No internet connection** required after first page load
- **No admin rights** needed

---

## 📁 Files Included

```
📦 Dashboard Package
├── 📄 dashboard.html          ← The dashboard (open this in browser)
├── 🐍 server.py               ← Python backend server
├── 🐍 spc_processor.py        ← SPC calculations
├── 🚀 START_DASHBOARD.bat     ← Windows launcher
├── 🚀 start_dashboard.sh      ← macOS/Linux launcher
├── 📖 README_STANDALONE.md    ← This file
└── 📊 PERFORMANCE_FIXES.md    ← Technical documentation
```

---

## ❓ Troubleshooting

### Problem: "Python is not installed"
**Solution:** Install Python from [python.org](https://www.python.org/downloads/)
- Windows: Check "Add Python to PATH" during installation
- Verify: Run `python --version` in Command Prompt

### Problem: "Server Not Running" error in browser
**Solution:** 
1. Make sure you started `server.py` first
2. Check that no other program is using port 8000
3. Try closing and reopening the dashboard

### Problem: Port 8000 already in use
**Solution:** Edit `server.py` and change the port:
```python
run_server(port=8001)  # Change to any available port
```
Then edit `dashboard.html` and change:
```javascript
const API_URL = 'http://localhost:8001';  // Match the port
```

### Problem: Batch file won't run
**Solution:** 
1. Right-click `START_DASHBOARD.bat`
2. Select "Run as administrator" (if you have rights)
3. Or manually run `python server.py` and open `dashboard.html`

### Problem: CSV upload fails
**Solution:**
- Check CSV format matches the template above
- Ensure dates are in YYYY-MM-DD format
- Make sure values are numeric (not text)
- Remove any extra blank lines

---

## 🔧 How It Works

1. **dashboard.html** - Contains the entire user interface
   - Built with React (loaded from CDN)
   - Charts powered by Recharts library
   - Sends CSV data to Python backend

2. **server.py** - Simple Python HTTP server
   - Handles file uploads
   - Routes requests to SPC processor
   - Returns results as JSON

3. **spc_processor.py** - Statistical calculations
   - Parses CSV data
   - Calculates control limits
   - Detects phase shifts
   - Returns formatted data for charts

**No data leaves your computer!** Everything runs locally.

---

## 📈 Understanding the Charts

- **Blue Line** - Actual values
- **Green Line** - Center Line (CL) - process average
- **Orange Dashed Lines** - Control Limits (UCL/LCL)
- **White Vertical Lines** - Phase boundaries
- **Phase Labels** - Roman numerals (I, II, III, etc.)

**Phase Detection:**
The system automatically detects when your process shifts by identifying 8 consecutive points above or below the center line.

---

## 🎓 Tips for Best Results

1. **Data Quality**: Ensure your data is clean and complete
2. **Sufficient Points**: At least 20-30 data points per measure work best
3. **Consistent Intervals**: Daily or weekly data points are ideal
4. **Multiple Measures**: Track 3-5 key metrics per station

---

## 📞 Support

For issues or questions:
1. Check the Troubleshooting section above
2. Review `PERFORMANCE_FIXES.md` for technical details
3. Verify Python version: `python --version` (need 3.7+)

---

## 🔒 Security & Privacy

✅ **All data stays on your computer**
✅ **No internet connection needed** (after initial load)
✅ **No data collection or tracking**
✅ **No external APIs or services**

---

## 📄 License & Credits

This dashboard uses:
- React 18 (MIT License)
- Recharts 2.12 (MIT License)
- TailwindCSS (MIT License)

All libraries loaded from public CDNs.

---

## 🚀 Quick Reference Card

```
┌─────────────────────────────────────────────────────┐
│  QUICK START GUIDE                                  │
├─────────────────────────────────────────────────────┤
│  1. Double-click START_DASHBOARD.bat (Windows)      │
│     or run: bash start_dashboard.sh (Mac/Linux)     │
│                                                      │
│  2. Wait for browser to open                        │
│                                                      │
│  3. Click "Load Demo" to see sample data            │
│                                                      │
│  4. Or "Upload CSV" to use your own data            │
│                                                      │
│  5. Switch stations using dropdown                  │
│                                                      │
│  ⚠️  Keep terminal/command window open!             │
└─────────────────────────────────────────────────────┘
```

---

**Need Help?** All files are self-contained and portable. Copy the entire folder to any computer with Python installed.

**Performance:** Handles datasets with 10,000+ data points smoothly. Optimized for minimal CPU usage.

---

*Last Updated: 2024*

