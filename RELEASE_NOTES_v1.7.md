# Release Notes — SPC Station Health Charts v1.7

**Release Date:** October 9, 2025  
**Package:** SPC-Station-Health-Charts-v1.7-SWA-Branding.zip

## 🎨 What's New in v1.7

### Southwest Airlines Branding
- **Documentation refresh**: All HTML docs now use official SWA color palette (Bold Blue #304CB2, Sunrise Yellow #FFBF27)
- **Unified typography**: Segoe UI/Inter system font stack across all documents
- **SPC Rules Explainer**: Converted from dark theme to clean SWA light theme for consistency

### Distribution Chart Enhancement
- **Phase slider integration**: Distribution histogram now updates dynamically with X/mR charts
- **Auto-binning**: Histogram automatically recalculates optimal bin count (Freedman-Diaconis rule) from filtered data
- **Synchronized filtering**: All three charts (X, mR, Distribution) respond to the same phase selection

### Export Improvements
- **Clean PNG exports**: Removed "Generated: timestamp | Wheeler's XmR Charts | NPL: 2.66σ" footer
- **Executive-ready**: Charts now export without metadata stamps for immediate use in presentations

## 📦 What's Included

### Core Application
- `dashboard_standalone.html` - Main dashboard with histogram linking
- `server.py` - Python HTTP server
- `spc_processor.py` - Statistical calculations engine
- `load_actual_data.py` - CSV data loader

### Documentation (Updated to v1.7)
- `TECHNICAL_SPEC.html` - Technical specification with SWA branding
- `PRD_Product_Requirements.html` - Product requirements with SWA branding
- `ARCHITECTURE.html` - Architecture documentation with SWA branding
- `SPC_Rules_and_Odds.html` - Statistical explainer with SWA light theme
- `README.md` - Technical README
- `README_DISTRIBUTION.md` - User-facing README
- `CHANGELOG_v1.7.md` - Version changelog
- `RELEASE_NOTES_v1.7.md` - This file

### Utilities
- `START_DASHBOARD.bat` - Windows launcher
- `start_dashboard.sh` - Mac/Linux launcher
- `csv_format_checker.html` - CSV diagnostic tool
- `logotest.html` - Logo comparison gallery

### Sample Data
- `input/*.csv` - Sample maintenance metrics (4 measures, 3 stations)

## 🔧 Installation

### Windows
1. Extract `SPC-Station-Health-Charts-v1.7-SWA-Branding.zip`
2. Double-click `START_DASHBOARD.bat`
3. Browser opens automatically to `http://localhost:8000`

### Mac/Linux
1. Extract the ZIP file
2. Open Terminal in the project folder
3. Run: `chmod +x start_dashboard.sh && ./start_dashboard.sh`

## ⬆️ Upgrade from v1.6

**No breaking changes.** Simply replace your v1.6 folder with v1.7.

### If you experience caching issues:
1. Stop the server (close terminal/command prompt)
2. Clear browser cache or hard refresh (`Ctrl+Shift+R` or `Cmd+Shift+R`)
3. Restart server

## 📊 Key Features (v1.7)

- ✅ Wheeler's XmR Charts (X, mR, Distribution)
- ✅ Automatic phase detection (Rule #1 & #4)
- ✅ Phase slider with synchronized histogram updates
- ✅ Clean PNG exports (no metadata footer)
- ✅ Southwest Airlines branding across all docs
- ✅ CSV troubleshooting tools
- ✅ Zero external dependencies
- ✅ 100% offline capable

## 🐛 Bug Fixes

- Distribution chart now correctly filters to match X/mR phase selection
- Histogram bin counts adjust automatically based on filtered data range

## 📝 Technical Details

### Distribution Chart Changes
```javascript
// Old behavior (v1.6)
- Distribution used server-provided histogram (all data)
- Did not respond to phase slider

// New behavior (v1.7)
- Distribution recomputes from filtered X chart values
- Auto-bins using Freedman-Diaconis rule (6-30 bins)
- Updates in real-time with slider adjustments
```

### Export Footer Removal
```javascript
// Removed from downloadChartWithHeader()
- Footer bar with timestamp, chart type, and NPL notation
- Now exports only chart content + header + legend
```

## 🎯 Known Issues

None reported for v1.7.

## 🔮 Future Enhancements (v1.8+)

- Additional Wheeler's Rules (2-of-3, 4-of-5, trends)
- Annotation/commenting on charts
- Comparison mode (station vs station)
- Automated email reports

## 📞 Support

For questions or issues, contact your Southwest Airlines Technical Operations team.

---

**Southwest Airlines Technical Operations Analytics Team**  
**Internal Use Only**

