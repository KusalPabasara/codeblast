"""
Sentinel Dashboard - Executive Retail Intelligence Platform
Modern Material Design UI with Advanced Analytics
Auto-reloads events file when modified
"""
import json
import os
from pathlib import Path
from flask import Flask, jsonify, render_template_string, request
from flask_cors import CORS
from collections import defaultdict
from typing import Dict, List, Any
from datetime import datetime
import random

app = Flask(__name__)
CORS(app)

# Global storage for events and file tracking
EVENTS_DATA = []
EVENTS_FILE = None
LAST_MODIFIED_TIME = None


def load_events_from_file(filepath: str, force_reload: bool = False):
    """Load events from JSONL file with auto-reload on modification"""
    global EVENTS_DATA, LAST_MODIFIED_TIME
    
    try:
        # Check if file exists
        if not os.path.exists(filepath):
            print(f"⚠ Events file not found: {filepath}")
            return
        
        # Get current modification time
        current_mtime = os.path.getmtime(filepath)
        
        # Reload if forced or if file was modified
        if force_reload or LAST_MODIFIED_TIME is None or current_mtime > LAST_MODIFIED_TIME:
            EVENTS_DATA = []
            with open(filepath, 'r', encoding='utf-8') as f:
                for line in f:
                    line = line.strip()
                    if line:
                        EVENTS_DATA.append(json.loads(line))
            
            LAST_MODIFIED_TIME = current_mtime
            print(f"✓ Loaded {len(EVENTS_DATA)} events for dashboard (Updated: {datetime.fromtimestamp(current_mtime).strftime('%Y-%m-%d %H:%M:%S')})")
        
    except FileNotFoundError:
        print(f"⚠ Events file not found: {filepath}")
    except Exception as e:
        print(f"⚠ Error loading events: {e}")


@app.route('/')
def index():
    """Main dashboard page - Executive Daisy UI Interface"""
    if EVENTS_FILE:
        load_events_from_file(EVENTS_FILE)
    
    # Load the dashboard template
    template_path = Path(__file__).parent / 'templates' / 'dashboard.html'
    if template_path.exists():
        with open(template_path, 'r', encoding='utf-8') as f:
            return f.read()
    else:
        # Fallback to embedded template
        return render_template_string(DASHBOARD_HTML)


@app.route('/api/summary')
def api_summary():
    """API: Get overall summary statistics (auto-reloads data)"""
    # Auto-reload events if file was modified
    if EVENTS_FILE:
        load_events_from_file(EVENTS_FILE)
    
    event_counts = defaultdict(int)
    severity_counts = defaultdict(int)
    station_counts = defaultdict(int)
    
    for event in EVENTS_DATA:
        event_name = event['event_data'].get('event_name', 'Unknown')
        event_counts[event_name] += 1
        
        station_id = event['event_data'].get('station_id')
        if station_id:
            station_counts[station_id] += 1
        
        # Estimate severity from event_id
        event_id = event.get('event_id', '')
        if event_id in ['E001', 'E002', 'E003']:
            severity_counts['FRAUD'] += 1
        elif event_id in ['E004', 'E005', 'E006', 'E008']:
            severity_counts['OPERATIONAL'] += 1
        elif event_id == 'E007':
            severity_counts['INVENTORY'] += 1
        else:
            severity_counts['NORMAL'] += 1
    
    return jsonify({
        'total_events': len(EVENTS_DATA),
        'event_breakdown': dict(event_counts),
        'severity_breakdown': dict(severity_counts),
        'station_breakdown': dict(station_counts),
        'fraud_events': severity_counts['FRAUD'],
        'operational_events': severity_counts['OPERATIONAL'],
        'inventory_events': severity_counts['INVENTORY'],
        'normal_events': severity_counts['NORMAL']
    })


@app.route('/api/events')
def api_all_events():
    """API: Get all events with optional filtering (auto-reloads data)"""
    # Auto-reload events if file was modified
    if EVENTS_FILE:
        load_events_from_file(EVENTS_FILE)
    
    # Query parameters for filtering
    event_type = request.args.get('event_type')
    station_id = request.args.get('station_id')
    limit = request.args.get('limit', type=int)
    
    filtered_events = EVENTS_DATA
    
    # Apply filters
    if event_type:
        filtered_events = [
            e for e in filtered_events
            if e['event_data'].get('event_name') == event_type
        ]
    
    if station_id:
        filtered_events = [
            e for e in filtered_events
            if e['event_data'].get('station_id') == station_id
        ]
    
    # Apply limit
    if limit:
        filtered_events = filtered_events[:limit]
    
    return jsonify({
        'total': len(filtered_events),
        'events': filtered_events
    })


@app.route('/api/events/<event_type>')
def api_events_by_type(event_type: str):
    """API: Get events filtered by event type"""
    filtered_events = [
        e for e in EVENTS_DATA
        if e['event_data'].get('event_name') == event_type
    ]
    
    return jsonify({
        'event_type': event_type,
        'count': len(filtered_events),
        'events': filtered_events
    })


@app.route('/api/stations')
def api_stations():
    """API: Get all stations with their event counts"""
    station_events = defaultdict(list)
    
    for event in EVENTS_DATA:
        station_id = event['event_data'].get('station_id')
        if station_id:
            station_events[station_id].append(event)
    
    stations = []
    for station_id, events in station_events.items():
        # Count event types
        event_type_counts = defaultdict(int)
        for event in events:
            event_name = event['event_data'].get('event_name', 'Unknown')
            event_type_counts[event_name] += 1
        
        stations.append({
            'station_id': station_id,
            'total_events': len(events),
            'event_breakdown': dict(event_type_counts),
            'recent_events': events[-5:]  # Last 5 events
        })
    
    return jsonify({
        'total_stations': len(stations),
        'stations': stations
    })


@app.route('/api/stations/<station_id>')
def api_station_details(station_id: str):
    """API: Get detailed information for a specific station"""
    station_events = [
        e for e in EVENTS_DATA
        if e['event_data'].get('station_id') == station_id
    ]
    
    # Count event types
    event_type_counts = defaultdict(int)
    fraud_count = 0
    
    for event in station_events:
        event_name = event['event_data'].get('event_name', 'Unknown')
        event_type_counts[event_name] += 1
        
        if event.get('event_id') in ['E001', 'E002', 'E003']:
            fraud_count += 1
    
    return jsonify({
        'station_id': station_id,
        'total_events': len(station_events),
        'fraud_events': fraud_count,
        'event_breakdown': dict(event_type_counts),
        'events': station_events
    })


@app.route('/api/fraud')
def api_fraud_events():
    """API: Get all fraud-related events"""
    fraud_event_ids = ['E001', 'E002', 'E003']
    fraud_events = [
        e for e in EVENTS_DATA
        if e.get('event_id') in fraud_event_ids
    ]
    
    return jsonify({
        'total_fraud_events': len(fraud_events),
        'events': fraud_events
    })


@app.route('/api/operational')
def api_operational_events():
    """API: Get all operational issue events"""
    operational_event_ids = ['E004', 'E005', 'E006', 'E008']
    operational_events = [
        e for e in EVENTS_DATA
        if e.get('event_id') in operational_event_ids
    ]
    
    return jsonify({
        'total_operational_events': len(operational_events),
        'events': operational_events
    })


@app.route('/api/inventory')
def api_inventory_events():
    """API: Get all inventory-related events"""
    inventory_events = [
        e for e in EVENTS_DATA
        if e.get('event_id') == 'E007'
    ]
    
    return jsonify({
        'total_inventory_events': len(inventory_events),
        'events': inventory_events
    })


@app.route('/api/analytics')
def api_analytics():
    """API: Get advanced analytics data"""
    # Auto-reload events if file was modified
    if EVENTS_FILE:
        load_events_from_file(EVENTS_FILE)
    
    # Calculate analytics
    total_events = len(EVENTS_DATA)
    
    # Station statistics
    station_stats = defaultdict(lambda: {
        'total': 0,
        'fraud': 0,
        'operational': 0,
        'customers': set()
    })
    
    # Time-based statistics
    hourly_events = defaultdict(int)
    
    # Event type distribution
    event_types = defaultdict(int)
    
    for event in EVENTS_DATA:
        station_id = event['event_data'].get('station_id')
        event_id = event.get('event_id', '')
        event_name = event['event_data'].get('event_name', 'Unknown')
        
        if station_id:
            station_stats[station_id]['total'] += 1
            if event_id in ['E001', 'E002', 'E003']:
                station_stats[station_id]['fraud'] += 1
            else:
                station_stats[station_id]['operational'] += 1
            
            customer_id = event['event_data'].get('customer_id')
            if customer_id:
                station_stats[station_id]['customers'].add(customer_id)
        
        # Time distribution
        try:
            timestamp = datetime.fromisoformat(event['timestamp'])
            hour = timestamp.hour
            hourly_events[hour] += 1
        except:
            pass
        
        event_types[event_name] += 1
    
    # Convert sets to counts
    station_summary = {}
    for station, stats in station_stats.items():
        station_summary[station] = {
            'total': stats['total'],
            'fraud': stats['fraud'],
            'operational': stats['operational'],
            'unique_customers': len(stats['customers']),
            'fraud_rate': round((stats['fraud'] / stats['total'] * 100), 2) if stats['total'] > 0 else 0
        }
    
    return jsonify({
        'total_events': total_events,
        'station_stats': station_summary,
        'hourly_distribution': dict(hourly_events),
        'event_type_distribution': dict(event_types),
        'active_stations': list(station_stats.keys()),
        'avg_events_per_station': round(total_events / len(station_stats), 2) if station_stats else 0
    })


# Dashboard HTML Template
DASHBOARD_HTML = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>AgentX - Self-Checkout Fraud Detection</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            padding: 20px;
            color: #333;
        }
        .container {
            max-width: 1400px;
            margin: 0 auto;
        }
        .header {
            text-align: center;
            color: white;
            margin-bottom: 30px;
        }
        .header h1 {
            font-size: 3em;
            margin-bottom: 10px;
            text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
        }
        .header p {
            font-size: 1.2em;
            opacity: 0.9;
        }
        .stats-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 20px;
            margin-bottom: 30px;
        }
        .stat-card {
            background: white;
            padding: 25px;
            border-radius: 12px;
            box-shadow: 0 4px 6px rgba(0,0,0,0.1);
            transition: transform 0.2s;
        }
        .stat-card:hover {
            transform: translateY(-5px);
            box-shadow: 0 6px 12px rgba(0,0,0,0.15);
        }
        .stat-card h3 {
            color: #666;
            font-size: 0.9em;
            text-transform: uppercase;
            margin-bottom: 10px;
        }
        .stat-card .value {
            font-size: 2.5em;
            font-weight: bold;
            margin-bottom: 5px;
        }
        .stat-card.fraud .value { color: #e74c3c; }
        .stat-card.operational .value { color: #f39c12; }
        .stat-card.inventory .value { color: #9b59b6; }
        .stat-card.success .value { color: #27ae60; }
        .stat-card.total .value { color: #3498db; }
        
        .content-section {
            background: white;
            border-radius: 12px;
            padding: 30px;
            margin-bottom: 20px;
            box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        }
        .section-title {
            font-size: 1.8em;
            margin-bottom: 20px;
            color: #2c3e50;
            border-bottom: 3px solid #667eea;
            padding-bottom: 10px;
        }
        .event-table {
            width: 100%;
            border-collapse: collapse;
            margin-top: 20px;
        }
        .event-table th {
            background: #667eea;
            color: white;
            padding: 12px;
            text-align: left;
            font-weight: 600;
        }
        .event-table td {
            padding: 12px;
            border-bottom: 1px solid #eee;
        }
        .event-table tr:hover {
            background: #f8f9fa;
        }
        .badge {
            display: inline-block;
            padding: 4px 12px;
            border-radius: 20px;
            font-size: 0.85em;
            font-weight: 600;
        }
        .badge.fraud { background: #fee; color: #e74c3c; }
        .badge.operational { background: #fef3e0; color: #f39c12; }
        .badge.inventory { background: #f3e5f5; color: #9b59b6; }
        .badge.success { background: #e8f5e9; color: #27ae60; }
        
        .api-section {
            background: #2c3e50;
            color: white;
            padding: 30px;
            border-radius: 12px;
            margin-bottom: 20px;
        }
        .api-endpoint {
            background: #34495e;
            padding: 15px;
            border-radius: 8px;
            margin-bottom: 15px;
            font-family: 'Courier New', monospace;
        }
        .api-endpoint .method {
            color: #2ecc71;
            font-weight: bold;
            margin-right: 10px;
        }
        .api-endpoint .path {
            color: #3498db;
        }
        .api-endpoint .description {
            color: #bdc3c7;
            font-size: 0.9em;
            margin-top: 8px;
        }
        .loading {
            text-align: center;
            padding: 40px;
            color: #666;
        }
        .auto-refresh-indicator {
            position: fixed;
            top: 10px;
            right: 10px;
            background: #27ae60;
            color: white;
            padding: 8px 15px;
            border-radius: 20px;
            font-size: 0.85em;
            box-shadow: 0 2px 4px rgba(0,0,0,0.2);
            z-index: 1000;
        }
        .auto-refresh-indicator.updating {
            background: #f39c12;
        }
    </style>
</head>
<body>
    <div class="auto-refresh-indicator" id="refresh-indicator">
        🔄 Auto-Refresh: Active
    </div>
    
    <div class="container">
        <div class="header">
            <h1>🛡️ AgentX</h1>
            <p>Self-Checkout Fraud Detection & Loss Prevention System</p>
            <p style="font-size: 0.9em; opacity: 0.8;">Real-Time Monitoring - Auto-Updates Every 5 Seconds</p>
        </div>
        
        <div class="stats-grid" id="stats">
            <div class="stat-card total">
                <h3>Total Events</h3>
                <div class="value" id="total-events">-</div>
            </div>
            <div class="stat-card fraud">
                <h3>Fraud Detected</h3>
                <div class="value" id="fraud-events">-</div>
            </div>
            <div class="stat-card operational">
                <h3>Operational Issues</h3>
                <div class="value" id="operational-events">-</div>
            </div>
            <div class="stat-card inventory">
                <h3>Inventory Issues</h3>
                <div class="value" id="inventory-events">-</div>
            </div>
            <div class="stat-card success">
                <h3>Successful Operations</h3>
                <div class="value" id="success-events">-</div>
            </div>
        </div>
        
        <div class="content-section">
            <h2 class="section-title">📊 Recent Events</h2>
            <div id="events-table">
                <div class="loading">Loading events...</div>
            </div>
        </div>
        
        <div class="content-section">
            <h2 class="section-title">🏪 Station Overview</h2>
            <div id="stations-table">
                <div class="loading">Loading stations...</div>
            </div>
        </div>
        
        <div class="api-section">
            <h2 class="section-title" style="color: white; border-color: #3498db;">🔌 REST API Endpoints</h2>
            
            <div class="api-endpoint">
                <span class="method">GET</span>
                <span class="path">/api/summary</span>
                <div class="description">Get overall summary statistics</div>
            </div>
            
            <div class="api-endpoint">
                <span class="method">GET</span>
                <span class="path">/api/events</span>
                <div class="description">Get all events (supports ?event_type=, ?station_id=, ?limit= filters)</div>
            </div>
            
            <div class="api-endpoint">
                <span class="method">GET</span>
                <span class="path">/api/events/{event_type}</span>
                <div class="description">Get events filtered by event type</div>
            </div>
            
            <div class="api-endpoint">
                <span class="method">GET</span>
                <span class="path">/api/stations</span>
                <div class="description">Get all stations with event counts</div>
            </div>
            
            <div class="api-endpoint">
                <span class="method">GET</span>
                <span class="path">/api/stations/{station_id}</span>
                <div class="description">Get detailed information for specific station</div>
            </div>
            
            <div class="api-endpoint">
                <span class="method">GET</span>
                <span class="path">/api/fraud</span>
                <div class="description">Get all fraud-related events</div>
            </div>
            
            <div class="api-endpoint">
                <span class="method">GET</span>
                <span class="path">/api/operational</span>
                <div class="description">Get all operational issue events</div>
            </div>
            
            <div class="api-endpoint">
                <span class="method">GET</span>
                <span class="path">/api/inventory</span>
                <div class="description">Get all inventory-related events</div>
            </div>
        </div>
    </div>
    
    <script>
        // Show refresh indicator
        function showRefreshIndicator() {
            const indicator = document.getElementById('refresh-indicator');
            indicator.classList.add('updating');
            indicator.textContent = '🔄 Updating...';
        }
        
        function hideRefreshIndicator() {
            const indicator = document.getElementById('refresh-indicator');
            indicator.classList.remove('updating');
            indicator.textContent = '🔄 Auto-Refresh: Active';
        }
        
        // Fetch and display summary statistics
        async function loadSummary() {
            try {
                showRefreshIndicator();
                const response = await fetch('/api/summary');
                const data = await response.json();
                
                document.getElementById('total-events').textContent = data.total_events;
                document.getElementById('fraud-events').textContent = data.fraud_events;
                document.getElementById('operational-events').textContent = data.operational_events;
                document.getElementById('inventory-events').textContent = data.inventory_events;
                document.getElementById('success-events').textContent = data.normal_events;
                
                hideRefreshIndicator();
            } catch (error) {
                console.error('Error loading summary:', error);
                hideRefreshIndicator();
            }
        }
        
        // Fetch and display recent events
        async function loadEvents() {
            try {
                const response = await fetch('/api/events?limit=50');
                const data = await response.json();
                
                let html = '<table class="event-table"><thead><tr>';
                html += '<th>Timestamp</th><th>Event ID</th><th>Event Name</th><th>Station</th><th>Details</th>';
                html += '</tr></thead><tbody>';
                
                data.events.forEach(event => {
                    const eventName = event.event_data.event_name;
                    const badgeClass = getBadgeClass(event.event_id);
                    
                    html += '<tr>';
                    html += `<td>${event.timestamp}</td>`;
                    html += `<td><span class="badge ${badgeClass}">${event.event_id}</span></td>`;
                    html += `<td>${eventName}</td>`;
                    html += `<td>${event.event_data.station_id || 'N/A'}</td>`;
                    html += `<td>${getEventDetails(event)}</td>`;
                    html += '</tr>';
                });
                
                html += '</tbody></table>';
                document.getElementById('events-table').innerHTML = html;
            } catch (error) {
                console.error('Error loading events:', error);
                document.getElementById('events-table').innerHTML = '<p>Error loading events</p>';
            }
        }
        
        // Fetch and display stations
        async function loadStations() {
            try {
                const response = await fetch('/api/stations');
                const data = await response.json();
                
                let html = '<table class="event-table"><thead><tr>';
                html += '<th>Station ID</th><th>Total Events</th><th>Event Breakdown</th>';
                html += '</tr></thead><tbody>';
                
                data.stations.forEach(station => {
                    html += '<tr>';
                    html += `<td><strong>${station.station_id}</strong></td>`;
                    html += `<td>${station.total_events}</td>`;
                    html += `<td>${formatEventBreakdown(station.event_breakdown)}</td>`;
                    html += '</tr>';
                });
                
                html += '</tbody></table>';
                document.getElementById('stations-table').innerHTML = html;
            } catch (error) {
                console.error('Error loading stations:', error);
                document.getElementById('stations-table').innerHTML = '<p>Error loading stations</p>';
            }
        }
        
        function getBadgeClass(eventId) {
            if (['E001', 'E002', 'E003'].includes(eventId)) return 'fraud';
            if (['E004', 'E005', 'E006', 'E008'].includes(eventId)) return 'operational';
            if (eventId === 'E007') return 'inventory';
            return 'success';
        }
        
        function getEventDetails(event) {
            const data = event.event_data;
            if (data.customer_id) return `Customer: ${data.customer_id}`;
            if (data.product_sku) return `SKU: ${data.product_sku}`;
            if (data.num_of_customers) return `Queue: ${data.num_of_customers}`;
            if (data.wait_time_seconds) return `Wait: ${data.wait_time_seconds}s`;
            return 'See details via API';
        }
        
        function formatEventBreakdown(breakdown) {
            return Object.entries(breakdown)
                .map(([name, count]) => `${name}: ${count}`)
                .join(', ');
        }
        
        // Load data on page load
        loadSummary();
        loadEvents();
        loadStations();
        
        // Auto-refresh every 5 seconds to catch new data quickly
        setInterval(() => {
            loadSummary();
            loadEvents();
            loadStations();
        }, 5000);
    </script>
</body>
</html>
"""


def start_dashboard(events_file: str, host: str = '0.0.0.0', port: int = 5000):
    """Start the dashboard server"""
    global EVENTS_FILE
    EVENTS_FILE = events_file
    
    print("\n" + "="*70)
    print("🚀 STARTING AGENTX DASHBOARD")
    print("="*70)
    
    load_events_from_file(events_file)
    
    print(f"\n✅ Dashboard running at http://localhost:{port}")
    print(f"✅ API endpoints available at http://localhost:{port}/api/*")
    print("\nPress Ctrl+C to stop the server\n")
    
    app.run(host=host, port=port, debug=False)


if __name__ == '__main__':
    import sys
    if len(sys.argv) > 1:
        start_dashboard(sys.argv[1])
    else:
        print("Usage: python dashboard.py <events_file.jsonl>")

