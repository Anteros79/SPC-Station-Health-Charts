# Architecture Documentation
## SPC Station Health Charts

**Version:** 1.6  
**Last Updated:** October 9, 2025  
**Architecture Style:** Client-Server (Local)  
**Enhancement:** Debug Tools & CSV Troubleshooting

---

## 1. System Overview

### High-Level Architecture

```mermaid
graph TB
    subgraph "User's Desktop"
        User[👤 User]
        Browser[🌐 Web Browser]
        Server[🐍 Python HTTP Server<br/>localhost:8000]
        
        subgraph "Static Files"
            HTML[📄 dashboard_standalone.html<br/>UI + Canvas Rendering]
            Launcher[⚙️ START_DASHBOARD.bat]
        end
        
        subgraph "Python Backend"
            ServerPy[server.py<br/>HTTP Request Handler]
            SPC[spc_processor.py<br/>Statistical Calculations]
            Loader[load_actual_data.py<br/>CSV Processing]
        end
        
        subgraph "Data Storage"
            Input[📁 input/<br/>Sample CSV Files]
            Output[📁 output/<br/>Exported PNG Charts]
        end
    end
    
    User -->|Double-click| Launcher
    Launcher -->|Starts| Server
    Launcher -->|Opens| Browser
    Browser -->|HTTP GET /| ServerPy
    ServerPy -->|Serves| HTML
    Browser -->|POST /api/load-actual| ServerPy
    Browser -->|POST /api/process| ServerPy
    ServerPy -->|Calls| Loader
    ServerPy -->|Calls| SPC
    Loader -->|Reads| Input
    SPC -->|Returns JSON| ServerPy
    ServerPy -->|JSON Response| Browser
    Browser -->|Renders Canvas| User
    Browser -->|Downloads PNG| Output
```

---

## 2. Component Architecture

### 2.1 Frontend (dashboard_standalone.html)

**Technology:** Pure HTML5 + JavaScript (No frameworks)

```mermaid
graph LR
    subgraph "Browser Layer"
        UI[User Interface<br/>HTML + CSS]
        Canvas[Canvas Renderer<br/>Chart Drawing]
        API[API Client<br/>Fetch Requests]
        State[State Management<br/>Global Variables]
    end
    
    UI -->|User Actions| API
    API -->|Fetch Data| State
    State -->|Trigger Render| Canvas
    Canvas -->|Visual Output| UI
```

**Key Responsibilities:**
- User interface rendering
- Chart visualization via HTML5 Canvas
- API communication with Python backend
- PNG export via Canvas `toDataURL()`
- Client-side state management

**Design Patterns:**
- **Event-Driven:** Button clicks trigger async API calls
- **Data-Driven Rendering:** Charts redraw on state change
- **Functional Decomposition:** Separate functions for each chart type

---

### 2.2 Backend (Python HTTP Server)

```mermaid
graph TB
    subgraph "Python Backend"
        Handler[SPCHandler<br/>HTTP Request Router]
        
        subgraph "Endpoints"
            GET[GET /<br/>Serve Dashboard HTML]
            LoadActual[POST /api/load-actual<br/>Load Sample Data]
            Process[POST /api/process<br/>Process CSV Upload]
        end
        
        subgraph "Processing Layer"
            Converter[auto_convert_csv_format<br/>Format Detection]
            SPCProc[spc_processor.py<br/>Statistical Engine]
            Loader[load_actual_data.py<br/>Multi-File Loader]
        end
        
        Handler --> GET
        Handler --> LoadActual
        Handler --> Process
        
        GET --> HTML[Return HTML File]
        LoadActual --> Loader
        Process --> Converter
        Converter --> SPCProc
        Loader --> SPCProc
        SPCProc --> JSON[Return JSON Data]
    end
```

**server.py - HTTP Request Handler**
- Extends `SimpleHTTPRequestHandler`
- Routes requests to appropriate handlers
- Adds CORS headers for local development
- Serves static HTML file
- Processes API requests

**spc_processor.py - Statistical Engine**
- Parses CSV data
- Calculates control limits (2.66 sigma)
- Detects phases using Wheeler's Rules
- Generates both X and mR charts
- Returns structured JSON

**load_actual_data.py - Data Loader**
- Scans `input/` directory for CSV files
- Converts format to standardized structure
- Maps station names (e.g., "Dallas" → "DAL")
- Infers measure names from filenames
- Combines multiple files into single dataset

---

## 3. Data Flow Architecture

### 3.1 Complete Data Flow (Load Test Data)

```mermaid
sequenceDiagram
    actor User
    participant Browser
    participant Server
    participant Loader
    participant SPC
    participant Files
    
    User->>Browser: Click "Load Test Data"
    Browser->>Server: POST /api/load-actual
    Server->>Loader: convert_to_spc_format(input_folder)
    Loader->>Files: Read all CSV files
    Files-->>Loader: Raw CSV data
    Loader->>Loader: Convert to standard format
    Loader-->>Server: Combined CSV text
    Server->>SPC: process_data(csv_text)
    SPC->>SPC: Parse CSV
    SPC->>SPC: Group by station/measure
    
    loop For each measure
        SPC->>SPC: detect_phases (X chart)
        SPC->>SPC: generate_moving_range_data
        SPC->>SPC: detect_phases (mR chart)
    end
    
    SPC-->>Server: JSON {chartData, stations}
    Server-->>Browser: HTTP 200 + JSON
    Browser->>Browser: Update state
    Browser->>Browser: renderCharts()
    
    loop For each chart
        Browser->>Browser: Draw Canvas (X chart)
        Browser->>Browser: Draw Canvas (mR chart)
    end
    
    Browser->>User: Display charts
```

---

### 3.2 CSV Upload Flow

```mermaid
sequenceDiagram
    actor User
    participant Browser
    participant Server
    participant Converter
    participant SPC
    
    User->>Browser: Upload CSV file
    Browser->>Browser: Read file.text()
    Browser->>Server: POST /api/process<br/>{csvData, filename}
    Server->>Converter: auto_convert_csv_format()
    
    alt Format A: timestamp,station,metric_value
        Converter->>Converter: Infer measure from filename
        Converter->>Converter: Convert to Format B
    else Format B: station,measure,date,value
        Converter->>Converter: Pass through unchanged
    end
    
    Converter-->>Server: Standardized CSV
    Server->>SPC: process_data(csv_text)
    SPC-->>Server: JSON result
    Server-->>Browser: HTTP 200 + JSON
    Browser->>Browser: Render charts
    Browser->>User: Display results
```

---

### 3.3 Phase Detection Algorithm Flow

```mermaid
flowchart TD
    Start[Start: Raw Data Points] --> Sort[Sort by Date]
    Sort --> Init[Initialize:<br/>phase_number=1<br/>current_start=0]
    Init --> CheckRemaining{More data<br/>to process?}
    
    CheckRemaining -->|No| End[Return phases + augmented points]
    CheckRemaining -->|Yes| Baseline[Take next 20 points<br/>as baseline]
    
    Baseline --> CalcBaseline[Calculate limits<br/>from baseline ONLY:<br/>CL, UCL, LCL]
    CalcBaseline --> Monitor[Monitor remaining data<br/>for Wheeler's Rules]
    
    Monitor --> Rule1{Point outside<br/>UCL/LCL?}
    Rule1 -->|Yes| Signal[Signal Detected!]
    Rule1 -->|No| Rule4{7 consecutive<br/>on one side of CL?}
    Rule4 -->|Yes| Signal
    Rule4 -->|No| ContinuePhase[Extend phase]
    
    ContinuePhase --> MoreData{More data<br/>in phase?}
    MoreData -->|Yes| Monitor
    MoreData -->|No| EndPhase
    
    Signal --> EndPhase[End current phase]
    EndPhase --> Recalc[Recalculate limits<br/>from actual phase data]
    Recalc --> SavePhase[Save phase metadata]
    SavePhase --> Augment[Augment points with<br/>UCL, CL, LCL values]
    Augment --> Increment[current_start = phase_end + 1<br/>phase_number++]
    Increment --> CheckRemaining
```

---

## 4. Technology Stack

### 4.1 Technology Decisions

| Layer | Technology | Rationale |
|-------|-----------|-----------|
| **Frontend UI** | HTML5 + CSS | Universal browser support; no build step |
| **Frontend Logic** | Vanilla JavaScript | Zero dependencies; works offline |
| **Charting** | HTML5 Canvas API | No external libraries; full control; PNG export built-in |
| **Backend** | Python 3.7+ | Already installed enterprise-wide; no admin rights needed |
| **Web Server** | `http.server` (stdlib) | No installation required; sufficient for localhost |
| **Data Format** | CSV | Universal; easy to generate from any system |
| **Data Transfer** | JSON over HTTP | Standard web protocol; easy parsing |
| **State Management** | Global JavaScript variables | Simple; no framework overhead |

### 4.2 Dependency Graph

```mermaid
graph TD
    subgraph "Zero External Dependencies"
        Python[Python 3.7+ Standard Library]
        Browser[Modern Web Browser]
    end
    
    subgraph "Python Modules (stdlib)"
        HTTP[http.server]
        JSON[json]
        CSV[csv]
        OS[os]
        DateTime[datetime]
    end
    
    subgraph "Browser APIs (native)"
        Canvas[Canvas API]
        Fetch[Fetch API]
        FileReader[FileReader API]
        DOM[DOM API]
    end
    
    Python --> HTTP
    Python --> JSON
    Python --> CSV
    Python --> OS
    Python --> DateTime
    
    Browser --> Canvas
    Browser --> Fetch
    Browser --> FileReader
    Browser --> DOM
```

**Critical Design Decision:**
- ❌ **Rejected:** React, Recharts, npm, Node.js (external dependencies, CDN issues)
- ✅ **Chosen:** Vanilla JavaScript + Canvas (zero dependencies, works anywhere)

---

## 5. API Specification

### 5.1 Endpoint: GET /

**Purpose:** Serve main dashboard HTML

**Request:**
```http
GET / HTTP/1.1
Host: localhost:8000
```

**Response:**
```http
HTTP/1.1 200 OK
Content-Type: text/html; charset=utf-8

<!DOCTYPE html>
<html>...</html>
```

---

### 5.2 Endpoint: POST /api/load-actual

**Purpose:** Load sample data from `input/` folder

**Request:**
```http
POST /api/load-actual HTTP/1.1
Host: localhost:8000
Content-Type: application/json

{}
```

**Response:**
```json
{
  "success": true,
  "chartData": {
    "DAL": {
      "Maintenance Cancels": {
        "points": [
          {
            "station": "DAL",
            "measure": "Maintenance Cancels",
            "date": "2023-01-02",
            "value": 3.2,
            "ucl": 5.1,
            "cl": 3.0,
            "lcl": 0.9
          }
        ],
        "phases": [
          {
            "startIndex": 0,
            "endIndex": 45,
            "cl": 3.0,
            "ucl": 5.1,
            "lcl": 0.9,
            "phaseNumber": 1
          }
        ]
      }
    }
  },
  "stations": ["AUS", "DAL", "HOU"]
}
```

---

### 5.3 Endpoint: POST /api/process

**Purpose:** Process uploaded CSV file

**Request:**
```http
POST /api/process HTTP/1.1
Host: localhost:8000
Content-Type: application/json

{
  "csvData": "timestamp,station,metric_value\n2023-01-02,Austin,2.5\n...",
  "filename": "maintenance_cancels.csv"
}
```

**Response:** (Same structure as `/api/load-actual`)

---

## 6. Security Architecture

### 6.1 Security Model

**Threat Model:** Low risk (local desktop tool)

```mermaid
graph TD
    subgraph "Security Boundaries"
        User[Trusted User]
        LocalHost[localhost:8000<br/>Loopback Only]
        FileSystem[Local File System<br/>User-owned]
    end
    
    User -->|Full Trust| LocalHost
    LocalHost -->|Read Only| FileSystem
    
    NoAuth[❌ No Authentication Needed]
    NoSSL[❌ No HTTPS Needed]
    NoValidation[⚠️ Minimal Input Validation]
    
    style NoAuth fill:#f9f,stroke:#333
    style NoSSL fill:#f9f,stroke:#333
    style NoValidation fill:#ff9,stroke:#333
```

**Security Decisions:**
- **No authentication:** Single-user desktop tool; localhost only
- **No HTTPS:** Traffic never leaves local machine
- **Minimal input validation:** Trust user-provided CSVs (graceful error handling)
- **No CORS restrictions:** Local origin only

**Risks Accepted:**
- Malicious CSV could cause Python exception (caught and returned as error)
- Port 8000 accessible to other localhost processes (low risk)

---

## 7. Deployment Architecture

### 7.1 Deployment Model

```mermaid
graph TD
    GitHub[📦 GitHub Repository<br/>Anteros79/SPC-Station-Health-Charts]
    
    Zip[📦 Distribution ZIP<br/>SPC-Station-Health-Charts.zip]
    
    GitHub -->|Download Release| Zip
    
    Desktop1[👤 User 1 Desktop]
    Desktop2[👤 User 2 Desktop]
    Desktop3[👤 User 3 Desktop]
    
    Zip -->|Extract| Desktop1
    Zip -->|Extract| Desktop2
    Zip -->|Extract| Desktop3
    
    Desktop1 -->|Run| Server1[🐍 Python Server<br/>Port 8000]
    Desktop2 -->|Run| Server2[🐍 Python Server<br/>Port 8000]
    Desktop3 -->|Run| Server3[🐍 Python Server<br/>Port 8000]
    
    style GitHub fill:#4CAF50
    style Server1 fill:#2196F3
    style Server2 fill:#2196F3
    style Server3 fill:#2196F3
```

**Deployment Steps:**
1. Download ZIP from GitHub
2. Extract to any folder
3. Double-click `START_DASHBOARD.bat` (Windows) or `./start_dashboard.sh` (Mac/Linux)
4. Browser opens automatically to `http://localhost:8000`

**No central server:** Each user runs their own independent instance

---

### 7.2 File Structure

```
SPC-Station-Health-Charts/
│
├── dashboard_standalone.html      # Main UI (self-contained)
├── server.py                      # HTTP server + routing + debug logging
├── spc_processor.py              # Statistical calculations + debug logging
├── load_actual_data.py           # CSV data loader
├── csv_format_checker.html       # CSV diagnostic tool
├── logotest.html                 # Logo comparison gallery
│
├── START_DASHBOARD.bat           # Windows launcher
├── start_dashboard.sh            # Mac/Linux launcher
│
├── README.md                     # Technical README
├── README_DISTRIBUTION.md        # User-facing README
├── .gitignore                    # Git ignore rules
│
├── input/                        # Sample CSV data
│   ├── maintenance_cancels.csv
│   ├── maintenance_delays.csv
│   ├── scheduled_maintenance_findings.csv
│   └── unscheduled_maintenance.csv
│
└── output/                       # Exported PNG charts (created on first use)
```

---

## 8. Performance Architecture

### 8.1 Performance Characteristics

| Operation | Target | Actual | Notes |
|-----------|--------|--------|-------|
| Server startup | < 2s | ~1s | Python startup + socket bind |
| Page load | < 3s | ~1s | Single HTML file, no bundling |
| Data processing (10K rows) | < 2s | ~0.5s | Pure Python, no database |
| Chart rendering (8 charts) | < 2s | ~1s | Canvas API, no DOM manipulation |
| PNG export | Instant | ~100ms | Canvas `toDataURL()` |

### 8.2 Scalability Limits

**Design Constraints:**
- **Data size:** Tested up to 10,000 rows (140 weeks × 3 stations × 4 measures × 2 charts)
- **Chart count:** Tested up to 24 charts per view (3 stations × 4 measures × 2 charts)
- **Concurrent users:** Single user per instance (localhost only)
- **Memory:** ~50MB Python process + ~100MB browser tab

**Horizontal Scaling:** Each user runs their own instance (inherently scalable)

---

## 9. Monitoring & Observability

### 9.1 Logging

**Server-side (Python):**
```python
# server.py logs all HTTP requests automatically
[05/Oct/2025 20:22:16] "GET / HTTP/1.1" 200 -
[05/Oct/2025 20:22:18] "POST /api/load-actual HTTP/1.1" 200 -
```

**Client-side (Browser Console):**
```javascript
console.log('Loading test data...');
console.error('Failed to load data:', error);
```

**No centralized logging:** Desktop tool, each user has their own logs

---

### 9.2 Error Handling Strategy

```mermaid
graph TD
    Error[Error Occurs] --> Type{Error Type?}
    
    Type -->|Server Error| ServerHandler[Python Exception Handler]
    Type -->|Client Error| ClientHandler[JavaScript Catch Block]
    Type -->|Data Error| DataHandler[Validation Logic]
    
    ServerHandler --> ServerLog[Log to Console]
    ServerLog --> ServerResponse[HTTP 500 + JSON Error]
    ServerResponse --> UserMessage[Show Error to User]
    
    ClientHandler --> ClientLog[Console.error]
    ClientLog --> UserMessage
    
    DataHandler --> ValidateMessage[Show Validation Message]
    ValidateMessage --> UserMessage
    
    UserMessage --> UserAction{User Action}
    UserAction -->|Retry| Retry[Try Again]
    UserAction -->|Contact Support| Support[Technical Support]
```

---

## 10. Design Patterns & Principles

### 10.1 Applied Patterns

**Separation of Concerns:**
- Frontend: UI rendering only
- Backend: Data processing only
- No business logic in HTML

**Stateless Server:**
- Each API call is independent
- No session management
- No database

**Fail-Fast:**
- Validate input immediately
- Return clear error messages
- Don't process invalid data

**Convention over Configuration:**
- Standard port (8000)
- Standard folders (`input/`, `output/`)
- No config files needed

---

## 11. Future Architecture Considerations

### 11.1 Potential Enhancements (V2.0)

```mermaid
graph TD
    subgraph "Current Architecture"
        Current[Single-User<br/>Desktop Tool]
    end
    
    subgraph "Future: Multi-User (Optional)"
        Web[Web Server<br/>Flask/FastAPI]
        DB[(PostgreSQL<br/>Historical Data)]
        Auth[Authentication<br/>SSO]
    end
    
    subgraph "Future: Advanced Features"
        Realtime[Real-time Updates<br/>WebSocket]
        ML[ML Predictions<br/>Anomaly Detection]
        API[REST API<br/>Integration]
    end
    
    Current -.->|If needed| Web
    Web -.-> DB
    Web -.-> Auth
    Web -.-> Realtime
    Web -.-> ML
    Web -.-> API
```

**Architectural Evolution:**
1. **Phase 1 (Current):** Desktop tool, zero dependencies ✅
2. **Phase 2 (Future):** Optional web deployment for teams
3. **Phase 3 (Future):** Integration with airline ERP systems

---

## 12. Architecture Decision Records (ADRs)

### ADR-001: Use HTML5 Canvas Instead of Recharts

**Context:** Initial implementation used Recharts library loaded from CDN  
**Decision:** Replaced with native HTML5 Canvas API  
**Rationale:**
- Corporate firewall blocks CDN access
- Recharts requires React framework (additional dependency)
- Canvas API provides sufficient charting capability
- Full control over rendering and export

**Consequences:**
- (+) Zero external dependencies
- (+) Works in any restricted environment
- (+) PNG export built-in via `toDataURL()`
- (-) More code to maintain (manual chart drawing)
- (-) Less sophisticated interactions (no hover tooltips)

**Status:** Accepted ✅

---

### ADR-002: Python http.server Instead of Flask/FastAPI

**Context:** Need web server for local dashboard  
**Decision:** Use Python's built-in `http.server` module  
**Rationale:**
- Already included in Python standard library
- No `pip install` required (users lack admin rights)
- Sufficient for localhost single-user scenario
- Simple to understand and modify

**Consequences:**
- (+) Zero installation friction
- (+) Works immediately after extracting ZIP
- (-) Not suitable for production multi-user deployment
- (-) Basic routing capabilities

**Status:** Accepted ✅

---

### ADR-003: Calculate Limits from Baseline, Not Entire Dataset

**Context:** Initial implementation calculated limits from all data, causing erratic behavior  
**Decision:** Calculate limits from first 20 points (baseline), then monitor for shifts  
**Rationale:**
- Follows Wheeler's methodology exactly
- Prevents limits from being influenced by out-of-control points
- Enables proper detection of process changes

**Consequences:**
- (+) Statistically correct
- (+) Realistic phase boundaries
- (-) Requires minimum 20 data points per phase

**Status:** Accepted ✅

---

## 13. Appendix: Mermaid Diagram Sources

All diagrams in this document use Mermaid markdown syntax and can be rendered in:
- GitHub markdown
- VS Code (with Mermaid extension)
- Notion, Confluence, etc.

---

**Document Version History**

| Version | Date | Author | Changes |
|---------|------|--------|---------|
| 1.0 | 2025-10-06 | Development Team | Initial architecture documentation |
| 1.4 | 2025-10-07 | Development Team | Debug tools, CSV troubleshooting, enhanced error reporting |

