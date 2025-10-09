# Changelog - Version 1.5.1

## Release Date: October 8, 2025

## Summary
Minor visual enhancement: Changed centerline color from blue to green for improved chart readability.

## Visual Improvements

### Centerline Color Change
**What Changed:**
- Centerline (CL) color changed from blue (`#304CB2`) to green (`#10B981`)
- Legend updated to reflect the new green centerline color

**Why It Matters:**
- Improved visual distinction between value line and centerline
- Easier to identify the center line at a glance
- Reduces visual confusion when analyzing charts
- Green is commonly associated with "target" or "goal" in process control

**Color Scheme:**
- **Value Line:** Blue (`#304CB2`) - Unchanged
- **Center Line (CL):** Green (`#10B981`) - **NEW**
- **UCL/LCL:** Red (`#F87171`) - Unchanged

## Technical Details

### Files Modified
1. **dashboard_standalone.html**
   - Line 832: Changed centerline stroke color to `#10B981` (green)
   - Line 523: Updated CL legend indicator to match new green color

### Code Changes

**Chart Drawing (Line 832):**
```javascript
// Before
ctx.strokeStyle = '#304CB2';  // Blue

// After
ctx.strokeStyle = '#10B981';  // Green
```

**Legend (Line 523):**
```html
<!-- Before -->
<div class="legend-line" style="background: #304CB2;"></div>

<!-- After -->
<div class="legend-line" style="background: #10B981;"></div>
```

## Compatibility

### No Breaking Changes
- ✅ All existing functionality remains unchanged
- ✅ No data format changes
- ✅ No API changes
- ✅ Backward compatible with all CSV files

### User Impact
- Users will immediately see the new green centerline
- No action required from users
- No retraining needed - just a visual enhancement

## Migration Notes

### For Users
- Simply refresh your browser to see the change
- No data migration required
- All existing workflows continue unchanged

### For Developers
- Only visual styling changed
- No logic or calculation changes
- No new dependencies

## Version History

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
**License:** Internal use only - Airline Technical Operations

