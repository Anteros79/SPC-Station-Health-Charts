# Release Notes - Version 1.6
## Southwest Airlines Technical Operations SPC Dashboard

### 🎉 Release Date: October 9, 2025

---

## 🌟 What's New

### Desktop Two-Column Layout
Charts now display side-by-side on desktop screens, showing **twice as many charts** without scrolling. Perfect for widescreen monitors and data analysis workflows.

### Compact Professional Header
Streamlined header design fits on a single line, providing more vertical space for your charts while maintaining a clean, professional appearance.

### Complete Southwest Airlines Station List
Pre-loaded dropdown menu with **all 82 Southwest Airlines stations** - from major hubs like PHX and MDW to international destinations like CUN and SJU.

### Fixed Phase Slider Functionality
Phase sliders now work correctly for each individual measure, with proper state persistence and accurate phase boundary display.

---

## ✨ Key Features

### 📊 Enhanced Layout
- **2-Column Grid:** Side-by-side charts on desktop (≥1200px)
- **Responsive Design:** Automatically adjusts to single column on mobile
- **Better Space Usage:** See more data at once

### 🎯 Improved User Experience
- **Compact Header:** More room for charts
- **82 Stations Pre-loaded:** Quick access to any Southwest location
- **Phase Control per Measure:** Independent slider control for each metric
- **Persistent Settings:** Your phase selections stay as you navigate

### 🔧 Bug Fixes
- ✅ Phase boundaries now align correctly with filtered data
- ✅ Phase sliders work independently for each measure
- ✅ Roman numeral phase labels display in correct positions
- ✅ State preservation when switching between stations

---

## 📋 Quick Start

### Windows Users
1. Double-click `START_DASHBOARD.bat`
2. Browser opens automatically
3. Click "📊 Load Test Data" to start

### Mac/Linux Users
1. Run `./start_dashboard.sh` in Terminal
2. Open browser to `http://localhost:8000`
3. Click "📊 Load Test Data" to start

---

## 📊 Sample Data Included

**Stations:** Austin (AUS), Dallas (DAL), Houston (HOU)
**Measures:** 
- Maintenance Cancels
- Maintenance Delays  
- Scheduled Maintenance Findings
- Unscheduled Maintenance

**Date Range:** January 2023 - October 2025

---

## 🎓 New User Tips

### Using the Phase Slider
1. Each measure group has its own phase slider (when 2+ phases exist)
2. Drag slider to show recent phases only
3. Settings persist as you navigate between stations
4. Use to focus on current performance vs historical

### Selecting Stations
- **View All:** Keep "All Stations" selected to see everything
- **Filter:** Choose specific station code (e.g., "PHX - Phoenix")
- **Add Custom:** Type code and click "Add" for unlisted stations

### Exporting Charts
- Click "💾 Save PNG" button on any chart
- High-resolution image downloads to your computer
- Perfect for presentations and reports

---

## 🔬 Statistical Methodology

### Wheeler's XmR Charts
- **X Chart:** Monitors process average (location)
- **mR Chart:** Monitors process variation (spread)  
- **Distribution:** Histogram with normality assessment

### Natural Process Limits (NPL)
- **Sigma:** 2.66 (natural process limits)
- **Detection Rules:** Wheeler's Rule #1 (beyond limits) & Rule #4 (runs of 7)
- **Automatic Phasing:** New phases created when signals detected

### Phase Management
- Minimum 20 points to establish baseline
- Limits calculated from baseline data only
- Subsequent data monitored for signals
- Automatic recalculation when process shifts

---

## 🔒 Data Privacy & Security

- ✅ **100% Local Processing** - No cloud services
- ✅ **No Internet Required** - Works completely offline
- ✅ **Zero Data Collection** - No telemetry or analytics
- ✅ **Your Computer Only** - Data never leaves your machine

Perfect for sensitive operational data and regulated environments.

---

## 📦 What's Included

```
SPC-Station-Health-Charts-v1.6/
├── dashboard_standalone.html      # Main dashboard
├── server.py                      # Local Python server
├── spc_processor.py              # SPC calculations
├── load_actual_data.py           # CSV processing
├── START_DASHBOARD.bat           # Windows launcher
├── start_dashboard.sh            # Mac/Linux launcher
├── SW Tech Ops logo.png          # Southwest branding
├── CHANGELOG_v1.6.md             # Detailed changes
├── README.md                     # Full documentation
├── README_DISTRIBUTION.md        # Quick start guide
└── input/                        # Sample CSV files
    ├── maintenance_cancels.csv
    ├── maintenance_delays.csv
    ├── scheduled_maintenance_findings.csv
    └── unscheduled_maintenance.csv
```

---

## 🔧 System Requirements

- **Python 3.7+** (standard library only)
- **Modern Web Browser** (Chrome, Edge, Firefox, Safari)
- **No Admin Rights Required**
- **No API Keys or Accounts Needed**
- **No Internet Connection Required**

---

## 📈 Upgrade from v1.5.1

### What's Different
- New 2-column layout on desktop
- Smaller, more compact header
- 82 Southwest stations pre-populated
- Phase slider functionality completely fixed
- Updated logo reference

### Compatibility
- ✅ Same data formats supported
- ✅ Same CSV upload process
- ✅ All existing features preserved
- ✅ No breaking changes

### Action Required
**None!** Just extract and run. All changes are backward compatible.

---

## 🆘 Troubleshooting

### Server Won't Start
- Verify Python installed: `python --version`
- Check port 8000 is available
- Try different port by editing `server.py`

### Charts Not Loading
- Ensure server is still running (don't close terminal)
- Refresh browser (F5)
- Check browser console for errors (F12)

### CSV Upload Issues
- Verify format: `timestamp,station,metric_value`
- Check dates are YYYY-MM-DD format
- Ensure values are valid numbers

### Phase Slider Not Appearing
- Slider only shows when measure has 2+ phases
- Single-phase measures don't need filtering

---

## 📚 Documentation

- **CHANGELOG_v1.6.md** - Detailed technical changes
- **README.md** - Complete user guide
- **README_DISTRIBUTION.md** - Quick start for new users

---

## 🎯 Coming Soon

Future enhancements under consideration:
- Export all charts as PDF report
- Custom date range filtering
- Comparison mode for multiple stations
- Additional statistical tests

*(Feature requests? Contact your Technical Operations lead)*

---

## 📞 Support

For questions, issues, or feature requests:
- Contact your station's Technical Operations team
- Email your local analytics support
- Internal ticket system for IT issues

---

## 📄 License & Usage

**Internal Use Only** - Southwest Airlines Technical Operations

This tool is for internal operational analysis only. Not for external distribution.

---

## 🙏 Acknowledgments

Built for Southwest Airlines Technical Operations teams using:
- **Wheeler's Methodology** - Donald J. Wheeler's XmR Chart principles
- **Python Standard Library** - Zero external dependencies
- **HTML5 Canvas** - High-performance chart rendering
- **Statistical Process Control** - Time-tested quality management

---

## 🔖 Version Information

- **Current Version:** 1.6
- **Release Date:** October 9, 2025
- **Previous Version:** 1.5.1 (October 8, 2025)
- **Initial Release:** 1.0 (October 2025)

---

**Thank you for using SPC Station Health Charts!**

*Empowering Technical Operations teams with data-driven insights.*

---

**Maintained by:** Southwest Airlines Technical Operations Analytics Team  
**Last Updated:** October 9, 2025  
**For:** Station maintenance teams, operations managers, and quality analysts

