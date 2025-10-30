# Southwest Airlines Tech Ops SPC Dashboard v2.0
## Distribution Package

**Version:** 2.0  
**Release Date:** October 14, 2025  
**Package:** Complete Distribution with Sample Data

---

## 🚀 Quick Start

1. **Extract** this ZIP file to your desired location
2. **Open Terminal/Command Prompt** in the extracted folder
3. **Run:** `python server.py`
4. **Open Browser:** Navigate to `http://localhost:8000`
5. **Click:** "✈️ Generate Airline KPIs" or upload your CSV file

---

## 📦 Package Contents

### **Core Application Files**
- `dashboard_standalone.html` - Main dashboard interface
- `server.py` - Python backend server
- `spc_processor.py` - SPC calculation engine
- `load_actual_data.py` - Data loading utilities

### **Documentation**
- `README.md` - Main project documentation
- `DISTRIBUTION_README.md` - This file (distribution guide)
- `DEVELOPER_GUIDE.md` - Comprehensive developer documentation
- `RELEASE_NOTES_v2.0.md` - Version 2.0 release notes
- `Explainer_File.html` - User guide with Southwest branding
- `SPC_Rules_and_Odds.html` - Statistical methodology guide

### **Sample Data Files**
- `input/Weekly_Airline_KPIs_Sample.csv` - Weekly SPC chart data
- `input/Daily_Airline_KPIs_Sample.csv` - Daily interactive chart data
- `input/Comprehensive_Airline_KPIs_Sample.csv` - Mixed weekly/daily data
- `input/CSV_Format_Examples.csv` - Format documentation and examples
- `input/README.md` - Input directory guide

### **Assets**
- `images/` - Southwest Airlines branding images and logos
- `test.html` - Simple test page for troubleshooting

---

## 🎯 Key Features

### **Weekly Mode (SPC Charts)**
- **X Chart:** Individual values with control limits
- **mR Chart:** Moving range between consecutive points  
- **Distribution Chart:** Histogram with phase filtering
- **Phase Detection:** Automatic phase boundary detection
- **Wheeler's Rules:** Rule #1, #2, and #4 implementation
- **Phase Zoom:** Slider to control number of phases displayed

### **Daily Mode (Interactive Charts)**
- **Plotly.js Bar Charts:** Interactive with zoom/pan capabilities
- **7-30 Day Slider:** Explicit control over date range
- **Weekend Highlighting:** Red coloring for weekend days
- **Dynamic Control Limits:** UCL/LCL calculated from visible data
- **Synchronized Data Table:** Table updates with chart interactions
- **Responsive Design:** Adapts to different screen sizes

### **Data Import**
- **Format 1:** `timestamp,station,metric_value` (filename = measure)
- **Format 2:** `station,measure,date,value` (multiple measures)
- **Date Formats:** YYYY-MM-DD, M/D/YYYY, YYYY/M/D, M-D-YYYY
- **Daily Charts:** Add "(Daily Bar)" to measure name
- **Error Handling:** Comprehensive validation and error messages

### **Southwest Airlines Branding**
- **Color Scheme:** Southwest Blue (#304CB2), Southwest Red (#C4122F)
- **Typography:** Arial font family with proper hierarchy
- **Layout:** Professional, executive-ready appearance
- **Logos:** Southwest Tech Ops branding throughout

---

## 📊 Sample Data Overview

### **Weekly_Airline_KPIs_Sample.csv**
- **Stations:** DAL, HOU, PHX (3 major Southwest hubs)
- **Measures:** Aircraft On-Time Performance, Maintenance Delays per 100 Departures
- **Time Range:** January 2023 to October 2025 (weekly data)
- **Data Points:** 300+ realistic data points with seasonal variation
- **Purpose:** Demonstrates weekly SPC charts with phase detection

### **Daily_Airline_KPIs_Sample.csv**
- **Stations:** DAL, HOU, PHX
- **Measures:** MEL Rate (Daily Bar), Aircraft Turn Time (Daily Bar), Gate Departure Delays (Daily Bar)
- **Time Range:** September 15 - October 14, 2025 (30 days)
- **Data Points:** 270 data points with weekend effects
- **Purpose:** Demonstrates daily interactive Plotly bar charts

### **Comprehensive_Airline_KPIs_Sample.csv**
- **Mixed Data:** Both weekly and daily measures in one file
- **6 Weekly Measures:** On-Time Performance, Maintenance Delays, Unscheduled Events, Availability Rate, Equipment Reliability, Baggage Performance
- **3 Daily Measures:** MEL Rate, Turn Time, Gate Delays (all with "(Daily Bar)")
- **Purpose:** Shows how to combine different chart types in one file

---

## 🛠️ System Requirements

### **Minimum Requirements**
- **Python:** 3.7 or higher
- **RAM:** 4GB minimum, 8GB recommended
- **Storage:** 100MB free space
- **Browser:** Chrome 80+, Firefox 75+, Safari 13+, Edge 80+

### **Recommended Requirements**
- **Python:** 3.9 or higher
- **RAM:** 8GB or higher
- **Storage:** 500MB free space
- **Browser:** Latest version of Chrome or Firefox

### **Dependencies**
- **Built-in Python modules only:** No external packages required
- **http.server:** For web server functionality
- **json:** For API communication
- **urllib.parse:** For URL handling
- **math:** For statistical calculations

---

## 🔧 Installation & Setup

### **Step 1: Extract Files**
```bash
# Extract the ZIP file to your desired location
# Example: C:\DevProjects\airline-tech-ops-spc-dashboard
```

### **Step 2: Start Server**
```bash
# Navigate to the extracted folder
cd airline-tech-ops-spc-dashboard

# Start the Python server
python server.py
```

### **Step 3: Access Dashboard**
- **Open browser:** Navigate to `http://localhost:8000`
- **Alternative:** Try `http://127.0.0.1:8000` if localhost doesn't work

### **Step 4: Test with Sample Data**
1. **Click "✈️ Generate Airline KPIs"** for realistic test data
2. **Or upload** one of the sample CSV files
3. **Explore** both weekly and daily chart modes

---

## 📋 CSV Format Guide

### **Format 1: Single Measure per File**
```csv
timestamp,station,metric_value
2023-01-02,DAL,2.1
2023-01-02,HOU,2.3
2023-01-09,DAL,3.2
```
- **Filename becomes the measure name**
- **Use for:** Single KPI files

### **Format 2: Multiple Measures in One File**
```csv
station,measure,date,value
DAL,Aircraft On-Time Performance,2023-01-02,87.2
DAL,Maintenance Delays per 100 Departures,2023-01-02,2.1
HOU,Aircraft On-Time Performance,2023-01-02,86.8
```
- **Use for:** Multiple KPIs from same data source

### **Daily Charts**
```csv
station,measure,date,value
DAL,MEL Rate (Daily Bar),2025-09-15,0.342
DAL,Aircraft Turn Time (Daily Bar),2025-09-15,42.3
```
- **Add "(Daily Bar)" to measure name** for interactive charts

### **Supported Date Formats**
- `YYYY-MM-DD`: 2023-01-02
- `M/D/YYYY`: 1/2/2023
- `YYYY/M/D`: 2023/1/2
- `M-D-YYYY`: 1-2-2023

---

## 🎨 Chart Types & Features

### **Weekly Mode (SPC Charts)**
- **X Chart:** Individual values with control limits and phase detection
- **mR Chart:** Moving range between consecutive points
- **Distribution Chart:** Histogram filtered by selected phases
- **Phase Zoom Slider:** Control number of phases displayed (default: all)
- **Wheeler's Rules:** Automatic detection of special causes
- **Export:** PNG download with headers and legends

### **Daily Mode (Interactive Charts)**
- **Plotly.js Bar Charts:** Professional interactive charts
- **7-30 Day Slider:** Explicit control over date range
- **Weekend Highlighting:** Red coloring for Saturday/Sunday
- **Dynamic Control Limits:** UCL/LCL calculated from visible data only
- **Synchronized Data Table:** Updates with chart interactions
- **Zoom & Pan:** Mouse wheel zoom, click-and-drag pan
- **Export:** PNG download functionality

---

## 🔍 Troubleshooting

### **Common Issues**

#### **Server Won't Start**
- **Check Python version:** `python --version` (need 3.7+)
- **Check port 8000:** Another application might be using it
- **Try different port:** Modify `server.py` if needed

#### **Charts Not Displaying**
- **Check browser console:** Press F12, look for errors
- **Clear browser cache:** Ctrl+Shift+Delete
- **Try different browser:** Chrome, Firefox, Edge
- **Disable browser extensions:** Especially data analysis tools

#### **CSV Upload Errors**
- **Check format:** Use supported CSV formats only
- **Check date format:** Use supported date formats
- **Check headers:** First row must contain column names
- **Check values:** Value column must contain only numbers

#### **Performance Issues**
- **Large files:** Split files by station or time period
- **Browser memory:** Close other tabs, restart browser
- **System resources:** Close other applications

### **Getting Help**
1. **Check documentation:** README.md, Explainer_File.html
2. **Review sample files:** Use provided CSV examples
3. **Test with sample data:** Use "Generate Airline KPIs" button
4. **Check browser console:** Look for JavaScript errors

---

## 📚 Documentation Files

### **User Documentation**
- **README.md** - Main project overview and features
- **Explainer_File.html** - Step-by-step user guide
- **input/README.md** - CSV format and sample data guide

### **Technical Documentation**
- **DEVELOPER_GUIDE.md** - Comprehensive developer documentation
- **SPC_Rules_and_Odds.html** - Statistical methodology and rules
- **RELEASE_NOTES_v2.0.md** - Version 2.0 changes and improvements

### **Sample Data Documentation**
- **CSV_Format_Examples.csv** - Format examples and requirements
- **input/README.md** - Detailed sample data descriptions

---

## 🏢 Southwest Airlines Branding

### **Color Scheme**
- **Primary Blue:** #304CB2 (Southwest Blue)
- **Primary Red:** #C4122F (Southwest Red)
- **Secondary Colors:** #059669 (Green), #0ea5e9 (Light Blue)
- **Neutral Colors:** #6B7280 (Gray), #F9FAFB (Light Gray)

### **Typography**
- **Primary Font:** Arial, sans-serif
- **Font Sizes:** Responsive scaling from 0.75rem to 1.5rem
- **Font Weights:** 400 (normal), 600 (semibold), 700 (bold)

### **Layout**
- **Container:** Max-width 1200px, centered
- **Charts:** 16:9 aspect ratio for executive presentation
- **Spacing:** Consistent 1rem margins and padding
- **Borders:** 1px solid with rounded corners (0.5rem)

---

## 🔄 Version History

### **Version 2.0 (Current)**
- **New:** Daily interactive bar charts with Plotly.js
- **New:** 7-30 day slider for daily charts
- **New:** Weekend highlighting in daily charts
- **New:** Dynamic control limits for daily charts
- **New:** Comprehensive sample data files
- **New:** Southwest Airlines branding throughout
- **Improved:** Phase zoom control for weekly charts
- **Improved:** Error handling and validation
- **Improved:** Documentation and user guides

### **Version 1.0 (Previous)**
- **Basic SPC charts:** X, mR, and Distribution charts
- **Phase detection:** Automatic phase boundary detection
- **Wheeler's Rules:** Rule #1 and #4 implementation
- **CSV import:** Basic CSV file upload functionality

---

## 📞 Support & Contact

### **Documentation**
- **User Guide:** Explainer_File.html
- **Developer Guide:** DEVELOPER_GUIDE.md
- **Sample Data:** input/README.md
- **Format Guide:** CSV_Format_Examples.csv

### **Testing**
- **Sample Data:** Use provided CSV files
- **Generate Data:** Click "✈️ Generate Airline KPIs" button
- **Test Page:** test.html for troubleshooting

### **Troubleshooting**
- **Browser Console:** Press F12 for error messages
- **Server Logs:** Check terminal output for server errors
- **Sample Files:** Test with provided sample data first

---

## 📄 License & Usage

This software is provided for Southwest Airlines internal use. All rights reserved.

**Distribution Package Contents:**
- Complete SPC Dashboard application
- Comprehensive documentation
- Sample data files
- Southwest Airlines branding assets
- Developer guides and user manuals

**Ready for deployment and use in Southwest Airlines Tech Ops environment.**

---

*Southwest Airlines Tech Ops SPC Dashboard v2.0 - Complete Distribution Package*
*October 14, 2025*
