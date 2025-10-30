# Design Document

## Overview

The offline dashboard fix addresses the single point of internet dependency in the Southwest Airlines Tech Ops SPC Dashboard by replacing the CDN-hosted Plotly.js library with a local copy. This design ensures true offline operation while maintaining all existing functionality and performance characteristics.

## Architecture

### Current Architecture Issue
```
Browser → dashboard_standalone.html → https://cdn.plot.ly/plotly-2.27.0.min.js (FAILS OFFLINE)
```

### Proposed Architecture
```
Browser → dashboard_standalone.html → ./js/plotly-2.27.0.min.js (LOCAL FILE)
```

### File Structure Changes
```
project-root/
├── dashboard_standalone.html (modified)
├── js/                       (new directory)
│   └── plotly-2.27.0.min.js (downloaded library)
├── server.py                 (unchanged)
├── spc_processor.py          (unchanged)
└── ... (other existing files)
```

## Components and Interfaces

### Component 1: Local JavaScript Library Storage
- **Purpose**: Store Plotly.js library locally to eliminate CDN dependency
- **Location**: `./js/plotly-2.27.0.min.js`
- **Size**: Approximately 3.2MB (compressed)
- **Version**: 2.27.0 (matching current CDN version)

### Component 2: HTML Reference Update
- **File**: `dashboard_standalone.html`
- **Change**: Update script src from CDN URL to local path
- **Before**: `<script src="https://cdn.plot.ly/plotly-2.27.0.min.js"></script>`
- **After**: `<script src="./js/plotly-2.27.0.min.js"></script>`

### Component 3: HTTP Server Static File Serving
- **Component**: Python HTTP server (server.py)
- **Requirement**: Ensure proper MIME type serving for .js files
- **Current State**: Already handles static files correctly via SimpleHTTPRequestHandler
- **Action**: No changes required - existing server handles .js files properly

## Data Models

No data model changes are required. All existing data structures, API endpoints, and CSV processing remain unchanged.

## Error Handling

### Offline Detection Strategy
1. **Graceful Degradation**: If local Plotly.js fails to load, display clear error message
2. **Fallback Messaging**: Inform user of missing dependency and provide resolution steps
3. **Startup Validation**: Optional startup check to verify all local dependencies exist

### Error Scenarios
1. **Missing Local File**: Display error if plotly-2.27.0.min.js is not found
2. **Corrupted File**: Handle cases where local file is corrupted or incomplete
3. **Browser Compatibility**: Maintain existing browser compatibility requirements

## Testing Strategy

### Offline Testing Protocol
1. **Network Isolation Test**: Disconnect internet and verify full functionality
2. **File Integrity Test**: Verify local Plotly.js file loads and functions correctly
3. **Feature Parity Test**: Ensure all chart types and interactions work identically
4. **Performance Test**: Verify load times are equal or better than CDN version

### Test Scenarios
1. **Cold Start Offline**: Start dashboard with no internet connection
2. **Network Loss During Use**: Disconnect internet while dashboard is running
3. **File Permission Test**: Verify dashboard works with various file permissions
4. **Browser Cache Test**: Test behavior with and without browser caching

### Validation Criteria
- All existing chart types render correctly
- Interactive features (zoom, pan, export) function properly
- Load time is ≤ 5 seconds on typical hardware
- No console errors related to missing resources
- CSV upload and processing work identically

## Implementation Approach

### Phase 1: Library Acquisition
1. Download Plotly.js 2.27.0 from official source
2. Verify file integrity using checksums
3. Create `js/` directory in project root
4. Place library file with correct permissions

### Phase 2: HTML Modification
1. Update script tag in `dashboard_standalone.html`
2. Test local loading in development environment
3. Verify no other CDN dependencies exist

### Phase 3: Validation
1. Test offline functionality thoroughly
2. Verify backward compatibility
3. Update documentation if needed

## Security Considerations

### File Integrity
- Verify Plotly.js download integrity using official checksums
- Ensure no malicious code injection during download process
- Maintain same security posture as CDN version

### Local File Access
- Leverage existing Python server security model
- No additional file system permissions required
- Maintain existing CORS and access control policies

## Performance Impact

### Expected Improvements
- **Faster Load Times**: Local file eliminates network latency
- **Reliability**: No dependency on external CDN availability
- **Consistent Performance**: No variation due to CDN performance

### Resource Usage
- **Disk Space**: +3.2MB for local Plotly.js file
- **Memory**: No change (same library loaded)
- **Network**: Eliminates external network requests

## Deployment Strategy

### Distribution Method
1. Include `js/plotly-2.27.0.min.js` in existing ZIP distribution
2. Update existing batch/shell scripts if needed
3. Maintain same extraction and startup procedures

### Rollback Plan
- Simple revert: Change HTML script tag back to CDN URL
- No data migration or complex rollback procedures required
- Existing installations can be updated by file replacement

## Maintenance Considerations

### Library Updates
- Monitor Plotly.js releases for security updates
- Establish process for updating local copy when needed
- Document version tracking in project documentation

### File Management
- Include local library in version control
- Ensure proper file permissions in distribution packages
- Monitor file size impact on overall package size