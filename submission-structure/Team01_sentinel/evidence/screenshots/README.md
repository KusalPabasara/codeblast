# Screenshots Directory

This directory contains dashboard screenshots and visual evidence for the submission.

## Required Screenshots

Please capture the following screenshots:

### 1. Dashboard Overview
**Filename**: `dashboard-overview.png`  
**Content**: Main dashboard showing all metrics panels, alerts, and event table

### 2. Fraud Alerts Panel
**Filename**: `fraud-alerts.png`  
**Content**: High-priority fraud alerts section with detected events

### 3. Event Distribution
**Filename**: `event-distribution.png`  
**Content**: Event statistics showing breakdown by type

### 4. Real-Time Metrics
**Filename**: `metrics-panel.png`  
**Content**: Top metrics cards showing total events, fraud count, etc.

### 5. Event Details
**Filename**: `event-details.png`  
**Content**: Detailed view of a specific event with all metadata

### 6. System Architecture (Optional)
**Filename**: `architecture-diagram.png`  
**Content**: Visual representation of system components

## How to Capture

1. Start the dashboard:
   ```bash
   cd src
   python dashboard.py --events-file ../evidence/output/test/events.jsonl
   ```

2. Open browser at `http://localhost:5000`

3. Use screenshot tool (Windows: Win+Shift+S, Mac: Cmd+Shift+4)

4. Save screenshots to this directory

5. Verify filenames match the list above

## Tips for Best Screenshots

- Use full-screen browser for clean captures
- Ensure all panels are visible
- Wait for data to load completely
- Capture during active event detection for realism
- Include timestamps in view
- Show real data, not placeholder text

---

**Status**: Ready for screenshot capture during competition
