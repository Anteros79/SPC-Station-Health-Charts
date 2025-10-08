# Changelog - Version 1.5

## Release Date: October 8, 2025

## Summary
Version 1.5 introduces improved chart organization and refined XmR signal coordination, making it easier to analyze related charts together and understand process behavior.

## New Features

### 1. Improved Chart Grouping
**What Changed:**
- Charts are now organized by measure, with all three chart types (X, mR, Distribution) appearing together
- Previous behavior: All X charts, then all mR charts, then all Distribution charts
- New behavior: For each measure, you see X chart → mR chart → Distribution chart before moving to the next measure

**Why It Matters:**
- Easier to analyze all aspects of a single measure at once
- Reduces scrolling and improves workflow
- More intuitive organization for process analysis

**Example:**
```
Station: DAL
  ├── Extreme Delays (X chart)
  ├── Extreme Delays (Moving Range)
  ├── Extreme Delays (Distribution)
  ├── Unscheduled Maintenance (X chart)
  ├── Unscheduled Maintenance (Moving Range)
  └── Unscheduled Maintenance (Distribution)
```

### 2. Point-Specific Signal Detection
**What Changed:**
- Tooltips now show accurate signal status for each individual data point
- Previous behavior: Global signal status could appear on all points
- New behavior: Only points that are actually signaling show signal badges

**Signal Badges:**
- ⚠️ **Both X & mR Signaling** - Point signals in both charts (requires immediate attention)
- 📊 **X Chart Signal** - Point signals in X chart only (process location shift)
- 📈 **mR Chart Signal** - Point signals in mR chart only (process variation change)

**Why It Matters:**
- More accurate identification of which specific points are out of control
- Clearer understanding of when signals occur
- Better decision-making for process interventions

## Technical Improvements

### Chart Sorting Algorithm
**File:** `dashboard_standalone.html`
**Lines:** 436-462, 545-567

**Implementation:**
```javascript
// Group measures by their base name (without suffixes)
measures.sort((a, b) => {
    const getBaseMeasure = (name) => {
        return name
            .replace(' (Moving Range)', '')
            .replace(' (Distribution)', '');
    };
    
    const getChartType = (name) => {
        if (name.includes('(Distribution)')) return 2;
        if (name.includes('(Moving Range)')) return 1;
        return 0;
    };
    
    const baseA = getBaseMeasure(a);
    const baseB = getBaseMeasure(b);
    
    if (baseA !== baseB) {
        return baseA.localeCompare(baseB);
    }
    
    return getChartType(a) - getChartType(b);
});
```

### Point-Specific Signal Flags
**File:** `spc_processor.py`
**Function:** `detect_xmr_signal_type`
**Lines:** 316-369

**New Data Fields Added to Each Point:**
- `x_signal` (boolean) - True if this point signals in X chart
- `mr_signal` (boolean) - True if this point signals in mR chart
- `both_signaling` (boolean) - True if this point signals in both charts
- `x_only_signal` (boolean) - True if only X chart signals at this point
- `mr_only_signal` (boolean) - True if only mR chart signals at this point

## Bug Fixes

### Fixed: Incorrect "Both Signaling" Badge Display
**Issue:** Tooltip showed "Both X & mR Signaling" on every data point, even when not signaling
**Root Cause:** Tooltip was checking global signal status instead of point-specific status
**Fix:** Updated tooltip logic to use point-specific signal flags
**File:** `dashboard_standalone.html`, lines 603-611

## Documentation Updates

### Updated Files:
1. **README.md**
   - Updated to version 1.5
   - Added chart grouping description
   - Updated feature list to include Distribution charts

2. **README_DISTRIBUTION.md**
   - Updated to version 1.5
   - Enhanced feature descriptions
   - Added chart grouping explanation

3. **TECHNICAL_SPEC.html**
   - Updated version number to 1.5

4. **PRD_Product_Requirements.html**
   - Updated version number to 1.5

5. **ARCHITECTURE.html**
   - Updated version number to 1.5

## Wheeler's Methodology Clarification

### XmR Chart Signal Interpretation
This release reinforces correct Wheeler's methodology for XmR charts:

**Key Principles:**
1. **X Chart Defines Phases** - The Individuals (X) chart is primary for detecting process location shifts
2. **mR Chart Uses Same Phases** - Moving Range chart shares identical phase boundaries from X chart
3. **Independent Signaling** - Each chart can signal independently:
   - X signal only = Process average has shifted
   - mR signal only = Process variation has changed
   - Both signaling = Both location and variation are out of control

**Control Limit Behavior:**
- Limits reflect the *previous* stable phase
- New limits are calculated for the *next* phase, starting *after* the signal point
- This is standard SPC practice and correct behavior

## Compatibility

### System Requirements
- Python 3.7+ (no changes)
- Modern web browser (no changes)
- No breaking changes to existing functionality

### Data Format
- No changes to CSV format requirements
- Existing data files work without modification

## Migration Notes

### For Users
- No action required
- Simply extract and run the new version
- All existing CSV files and workflows remain compatible

### For Developers
- Chart sorting logic has changed (see Technical Improvements)
- New point-specific signal fields available in data structure
- Tooltip rendering logic updated

## Known Issues
None reported for this release.

## Future Enhancements
- Additional Wheeler's rules (Rules #2 and #3)
- Configurable baseline period
- Multi-file batch processing
- Enhanced export options (PDF, Excel)

## Credits
- **Development:** Technical Operations Analytics Team
- **Methodology:** Donald J. Wheeler's SPC principles
- **Testing:** Station maintenance teams (AUS, DAL, HOU)

---

**Previous Version:** 1.4 (CSV Troubleshooting & Debug Tools)  
**Current Version:** 1.5 (Chart Grouping & Signal Refinement)  
**Next Planned:** 1.6 (Additional Wheeler's Rules)
