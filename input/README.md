# Input Directory - Sample Data Files

This directory contains sample CSV files demonstrating the proper format for importing data into the SPC Dashboard.

## 📁 Sample Files

### **Weekly_Airline_KPIs_Sample.csv**
- **Purpose:** Demonstrates weekly SPC chart data
- **Stations:** DAL, HOU, PHX (3 major Southwest hubs)
- **Measures:** Aircraft On-Time Performance, Maintenance Delays per 100 Departures
- **Time Range:** January 2023 to October 2025 (weekly data)
- **Format:** station,measure,date,value

### **Daily_Airline_KPIs_Sample.csv**
- **Purpose:** Demonstrates daily bar chart data
- **Stations:** DAL, HOU, PHX
- **Measures:** MEL Rate (Daily Bar), Aircraft Turn Time (Daily Bar), Gate Departure Delays (Daily Bar)
- **Time Range:** September 15 - October 14, 2025 (30 days)
- **Format:** station,measure,date,value
- **Special:** Contains "(Daily Bar)" in measure names for interactive charts

### **Comprehensive_Airline_KPIs_Sample.csv**
- **Purpose:** Mixed weekly and daily data in one file
- **Stations:** DAL, HOU, PHX
- **Weekly Measures:** 6 different KPIs (On-Time, Maintenance Delays, etc.)
- **Daily Measures:** 3 daily bar chart measures
- **Format:** station,measure,date,value

### **CSV_Format_Examples.csv**
- **Purpose:** Documentation and examples of supported formats
- **Content:** Format examples, date format options, requirements

## 📋 CSV Format Requirements

### **Supported Formats:**

#### **Format 1: Single Measure per File**
```
timestamp,station,metric_value
2023-01-02,DAL,2.1
2023-01-02,HOU,2.3
```
- **Filename becomes the measure name**
- **Use for:** Single KPI files

#### **Format 2: Multiple Measures in One File**
```
station,measure,date,value
DAL,Aircraft On-Time Performance,2023-01-02,87.2
DAL,Maintenance Delays per 100 Departures,2023-01-02,2.1
```
- **Use for:** Multiple KPIs from same data source

### **Date Formats Supported:**
- `YYYY-MM-DD`: 2023-01-02
- `M/D/YYYY`: 1/2/2023
- `YYYY/M/D`: 2023/1/2
- `M-D-YYYY`: 1-2-2023

### **Daily Charts:**
- **Add "(Daily Bar)" to measure name** for interactive Plotly charts
- **Example:** `MEL Rate (Daily Bar)`, `Aircraft Turn Time (Daily Bar)`

### **Requirements:**
- ✅ First row must be headers
- ✅ No empty rows
- ✅ Numeric values only in value column
- ✅ 3-letter station codes (DAL, HOU, PHX, etc.)
- ✅ Descriptive measure names

## 🎯 Chart Types

### **Weekly Mode (SPC Charts):**
- **X Chart:** Individual values over time
- **mR Chart:** Moving range between consecutive points
- **Distribution Chart:** Histogram of all values
- **Features:** Phase detection, Wheeler's rules, phase zoom slider

### **Daily Mode (Interactive Bar Charts):**
- **Plotly.js Charts:** Interactive bar charts with zoom/pan
- **Features:** 7-30 day slider, weekend highlighting, dynamic control limits
- **Data Table:** Synchronized table below chart

## 🚀 Getting Started

1. **Upload a sample file** to test the dashboard
2. **Try "Generate Airline KPIs"** button for realistic test data
3. **Use "Load Test Data"** for basic demo data
4. **Check the User Guide** (Explainer_File.html) for detailed instructions

## 📊 Sample Data Characteristics

### **Weekly Data:**
- **Realistic variation:** Based on airline industry benchmarks
- **Seasonal patterns:** Performance varies throughout the year
- **Station differences:** Each station has unique performance characteristics
- **Phase detection:** Contains natural performance shifts for SPC analysis

### **Daily Data:**
- **Weekend effects:** Slightly different performance on weekends
- **Realistic ranges:** Based on actual airline operational data
- **Interactive features:** Perfect for testing slider and zoom functionality

## 🔧 Troubleshooting

### **Common Issues:**
- **Date format errors:** Use supported date formats only
- **Missing headers:** Ensure first row contains column names
- **Non-numeric values:** Check that value column contains only numbers
- **Empty rows:** Remove any blank rows from your CSV

### **File Size Limits:**
- **Recommended:** Under 10MB for best performance
- **Maximum:** 50MB (browser dependent)
- **Large files:** Consider splitting by station or time period

## 📞 Support

- **User Guide:** Explainer_File.html
- **SPC Rules:** SPC_Rules_and_Odds.html
- **Developer Guide:** DEVELOPER_GUIDE.md
- **Release Notes:** RELEASE_NOTES_v2.0.md
