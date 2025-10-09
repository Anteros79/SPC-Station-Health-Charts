# Changelog - Version 1.6

## Release Date: October 9, 2025

## Summary
Major UI improvements including two-column chart layout for desktop, compact header design, comprehensive airport station list, and critical phase slider functionality fixes.

## New Features

### 1. Two-Column Chart Layout
**What Changed:**
- Charts now display in a 2-column grid on desktop screens (≥1200px width)
- Single column layout on smaller screens for mobile compatibility
- Improved space utilization on widescreen monitors

**Benefits:**
- More charts visible without scrolling
- Better use of screen real estate
- Faster data comparison across measures

**Technical Implementation:**
```css
.measure-charts {
    display: grid;
    grid-template-columns: repeat(2, 1fr);
    gap: 1.5rem;
}

@media (max-width: 1200px) {
    .measure-charts {
        grid-template-columns: 1fr;
    }
}
```

### 2. Compact Header Design
**What Changed:**
- Reduced logo size from 112.5px to 80px height
- Reduced title font size from 2.25rem to 1.75rem
- Tightened padding and gaps throughout header
- Simplified button text: "Upload CSV (Auto-Detect Format)" → "Upload CSV"
- More compact button and input padding

**Benefits:**
- Header fits on single line on most screens
- More vertical space for charts
- Cleaner, more professional appearance

### 3. Comprehensive Southwest Airlines Station List
**What Added:**
- Pre-populated dropdown with 82 Southwest Airlines airport codes
- Includes all major hubs and destinations
- Organized alphabetically for easy finding
- Format: "CODE - City Name" (e.g., "PHX - Phoenix")

**Stations Included:**
- Major hubs: ATL, BWI, DAL, DEN, HOU, LAS, MDW, PHX, etc.
- Texas cities: AUS, DAL, HOU, SAT, ELP, etc.
- West Coast: BUR, LAX, OAK, ONT, PDX, SAN, SEA, SFO, SJC, etc.
- East Coast: BOS, BUF, BWI, LGA, PHL, PVD, etc.
- International: CUN, MEX, MBJ, PVR, SJD, SJU

## Critical Bug Fixes

### Phase Slider Functionality
**Issues Fixed:**

1. **Phase Index Misalignment**
   - Problem: Phase `startIndex` and `endIndex` weren't adjusted when filtering data
   - Impact: Charts displayed incorrect phase boundaries when using slider
   - Solution: Adjusted phase indices to be relative to filtered points array

2. **Missing State Persistence**
   - Problem: Phase selection reset to maximum on every render
   - Impact: Slider position lost when switching between stations
   - Solution: Added `phaseSelections` global object to track state per measure group

3. **Station-Level vs Measure-Level Control**
   - Problem: Phase slider only worked at station level, not per measure
   - Impact: All measures forced to same phase selection
   - Solution: Unique `groupKey` per station-measure combination

**Technical Implementation:**

```javascript
// Added global state tracking
let phaseSelections = {}; // Track phase selections per measure group

// Fixed filterToLastNPhases() to adjust indices
const adjustedPhases = phasesToShow.map(phase => ({
    ...phase,
    startIndex: phase.startIndex - startIndex,  // Relative to filtered array
    endIndex: phase.endIndex - startIndex      // Relative to filtered array
}));

// Save state when slider changes
const groupKey = `${station}-${baseMeasure}`;
phaseSelections[groupKey] = numPhases;

// Use saved state on render
const defaultPhases = phaseSelections[groupKey] || maxPhases;
```

**Impact:**
- ✅ Phase slider now works independently for each measure
- ✅ Phase boundaries display correctly
- ✅ Slider state persists when navigating
- ✅ Roman numeral phase labels align properly

## Technical Details

### Files Modified

1. **dashboard_standalone.html**
   - CSS: Added 2-column grid layout with responsive breakpoint
   - CSS: Reduced header sizing and spacing
   - HTML: Added 82 Southwest Airlines stations to dropdown
   - JavaScript: Added `phaseSelections` state tracking (line 483)
   - JavaScript: Fixed `filterToLastNPhases()` index adjustment (lines 623-628)
   - JavaScript: Updated `renderCharts()` to use saved state (lines 713-714, 834-835)
   - JavaScript: Updated `updatePhaseZoom()` to save state (lines 860-861)
   - JavaScript: Reset phase selections on data load (lines 498, 522, 554)

### Code Changes Summary

**Layout (CSS):**
- `.measure-charts`: Changed from `flex column` to `grid` with 2 columns
- `.header`: Reduced padding from 1.5rem to 1rem
- `.logo`: Reduced height from 112.5px to 80px
- `.app-title`: Reduced font size from 2.25rem to 1.75rem
- `button`: Reduced padding from 0.625rem 1.25rem to 0.5rem 1rem

**Phase Slider Logic:**
- Added global state: `phaseSelections = {}`
- Fixed phase index adjustment in `filterToLastNPhases()`
- Added state save in `updatePhaseZoom()`
- Added state load in `renderCharts()` (2 locations)
- Added state reset in all data load functions (3 locations)

## Compatibility

### No Breaking Changes
- ✅ All existing functionality preserved
- ✅ No data format changes
- ✅ No API changes
- ✅ Backward compatible with all CSV files
- ✅ All existing features work as before

### Browser Compatibility
- Chrome/Edge: Fully supported
- Firefox: Fully supported
- Safari: Fully supported
- Mobile browsers: Responsive single-column layout

## Migration Notes

### For Users
- Simply refresh browser to see updates
- No action required
- Phase slider now works as expected per measure
- More charts visible on desktop screens

### For Developers
- Review phase filtering logic if customizing
- CSS Grid used for layout (IE11 not supported)
- State management pattern introduced for phase selections

## Performance Improvements

- **Layout Efficiency:** CSS Grid is more performant than flexbox for 2D layouts
- **Reduced Renders:** Phase state tracking prevents unnecessary re-renders
- **Smaller Header:** More vertical space = less scrolling

## User Experience Improvements

1. **Better Screen Utilization**
   - 2x more charts visible at once on desktop
   - Reduced scrolling for data analysis

2. **Correct Phase Filtering**
   - Sliders work independently per measure
   - Phase boundaries align correctly
   - State persists across navigation

3. **Easier Station Selection**
   - 82 pre-populated stations
   - Alphabetically organized
   - Quick access to any Southwest location

4. **Cleaner Interface**
   - Compact header maximizes chart space
   - Professional appearance
   - Single-line header on most screens

## Known Limitations

- Phase slider only appears when measure has 2+ phases
- Two-column layout requires ≥1200px screen width
- Phase selections reset when loading new data (by design)

## Testing Notes

### Tested Scenarios
- ✅ Phase slider with 1-8 phases per measure
- ✅ Multiple measures with different phase counts
- ✅ Station filtering with phase state preservation
- ✅ Data reload clearing phase selections
- ✅ Responsive layout on various screen sizes
- ✅ All 82 stations selectable from dropdown

### Test Data
- Sample files in `input/` folder
- AUS, DAL, HOU stations
- 4 maintenance measures
- Date range: Jan 2023 - Oct 2025

## Version History

- **v1.6** (Oct 2025) - Two-column layout, phase slider fixes, compact header
- **v1.5.1** (Oct 2025) - Green centerline for improved readability
- **v1.5** (Oct 2025) - Chart grouping & signal refinement
- **v1.4** (Oct 2025) - CSV troubleshooting & debug tools
- **v1.3** (Oct 2025) - Graphics update & branding
- **v1.2** (Oct 2025) - Final branded version
- **v1.1** (Oct 2025) - Interactive features
- **v1.0** (Oct 2025) - Initial release

---

**Built with:** Python, HTML5 Canvas, Statistical Process Control  
**Methodology:** Donald J. Wheeler's XmR Charts  
**License:** Internal use only - Southwest Airlines Technical Operations

