"""
Dashboard Application for Project Sentinel - Team Gmora
Enhanced Web-based Real-Time Monitoring Dashboard
Comprehensive retail intelligence with advanced analytics
"""
from flask import Flask, render_template, jsonify, request
from flask_cors import CORS
import json
from pathlib import Path
from datetime import datetime, timedelta
from collections import defaultdict
import threading
import time
import statistics
import os

from event_engine import EventDetectionEngine
from config import THRESHOLDS, EVENT_TYPES


app = Flask(__name__)
CORS(app)

# Global state with enhanced tracking
dashboard_state = {
    'events': [],
    'summary': {},
    'last_update': None,
    'alerts': [],
    'metrics': {},
    'realtime_stats': {},
    'performance_analytics': {},
    'events_file': None,
    'last_file_mtime': None
}


def load_events_from_file(events_file: str):
    """Load events from JSONL file for visualization"""
    events = []
    if Path(events_file).exists():
        with open(events_file, 'r') as f:
            for line in f:
                if line.strip():
                    events.append(json.loads(line))
    return events


def reload_events_if_changed():
    """Check if events file has changed and reload if necessary"""
    events_file = dashboard_state.get('events_file')
    if not events_file or not Path(events_file).exists():
        return False

    try:
        current_mtime = os.path.getmtime(events_file)
        last_mtime = dashboard_state.get('last_file_mtime')

        # Reload if file has been modified
        if last_mtime is None or current_mtime > last_mtime:
            print(f"[AUTO-RELOAD] Detected changes in events file, reloading...")
            dashboard_state['events'] = load_events_from_file(events_file)
            dashboard_state['last_update'] = datetime.now().isoformat()
            dashboard_state['last_file_mtime'] = current_mtime
            dashboard_state['metrics'] = calculate_metrics(dashboard_state['events'])
            dashboard_state['metrics']['last_update'] = dashboard_state['last_update']

            # Extract high-priority alerts
            fraud_types = ['Scanner Avoidance', 'Barcode Switching', 'Weight Discrepancies', 'High-Risk Customer']
            dashboard_state['alerts'] = [
                e for e in dashboard_state['events']
                if e.get('event_data', {}).get('event_name') in fraud_types
            ][:10]

            print(f"[AUTO-RELOAD] Loaded {len(dashboard_state['events'])} events")
            print(f"[AUTO-RELOAD] Fraud: {dashboard_state['metrics'].get('fraud_count', 0)}, "
                  f"Operational: {dashboard_state['metrics'].get('operational_issues', 0)}")
            return True
    except Exception as e:
        print(f"[AUTO-RELOAD] Error checking file: {e}")
        return False

    return False


def file_watcher_thread():
    """Background thread to monitor events file for changes"""
    while True:
        try:
            reload_events_if_changed()
            time.sleep(2)  # Check every 2 seconds
        except Exception as e:
            print(f"[FILE-WATCHER] Error: {e}")
            time.sleep(5)


def calculate_metrics(events):
    """Calculate comprehensive dashboard metrics with advanced analytics"""
    metrics = {
        'total_events': len(events),
        'fraud_count': 0,
        'operational_issues': 0,
        'inventory_issues': 0,
        'success_operations': 0,
        'high_priority_alerts': 0,
        'event_types': defaultdict(int),
        'stations': defaultdict(int),
        'timeline': [],
        'severity_breakdown': defaultdict(int),
        'average_risk_score': 0.0,
        'top_risk_events': [],
        'high_risk_customers': [],
        'last_event_time': None,
        'hourly_distribution': defaultdict(int),
        'station_performance': {},
        'financial_impact': 0.0,
        'detection_efficiency': 0.0,
        'fraud_prevention_score': 0.0,
        'customer_experience_score': 0.0,
        'system_health_score': 100.0,
        'critical_alerts': 0,
        'peak_hour': None,
        'most_problematic_station': None,
        'trend_analysis': {}
    }

    fraud_types = ['Scanner Avoidance', 'Barcode Switching', 'Weight Discrepancies']
    operational_types = ['Long Queue Length', 'Long Wait Time', 'Unexpected Systems Crash', 'Staffing Needs', 'Station Performance Alert', 'Checkout Station Action']
    success_types = ['Success Operation']
    inventory_types = ['Inventory Discrepancy']
    severity_counts = defaultdict(int)
    risk_events = []
    timeline_buckets = defaultdict(int)
    high_risk_customers = []
    hourly_events = defaultdict(int)
    station_metrics = defaultdict(lambda: {'events': 0, 'fraud': 0, 'operational': 0, 'risk_sum': 0.0})
    total_estimated_loss = 0.0
    critical_count = 0

    for event in events:
        event_data = event.get('event_data', {})
        event_name = event_data.get('event_name', '')
        metrics['event_types'][event_name] += 1

        station = event_data.get('station_id')
        if station:
            metrics['stations'][station] += 1
            station_metrics[station]['events'] += 1
            if event_name in fraud_types:
                station_metrics[station]['fraud'] += 1
            elif event_name in operational_types:
                station_metrics[station]['operational'] += 1

        severity = event_data.get('severity', 'UNSPECIFIED')
        severity_counts[severity] += 1
        if severity == 'HIGH':
            critical_count += 1

        risk_score = event_data.get('risk_score')
        if risk_score is not None:
            risk_events.append({
                'risk_score': risk_score,
                'event_name': event_name,
                'timestamp': event.get('timestamp'),
                'station_id': station,
                'severity': event_data.get('severity')
            })
            if station:
                station_metrics[station]['risk_sum'] += risk_score

        # Track financial impact with smart calculation
        if 'estimated_loss' in event_data:
            total_estimated_loss += event_data['estimated_loss']
        if 'price_gap' in event_data:
            total_estimated_loss += event_data['price_gap']

        # Calculate estimated loss for fraud events without explicit loss values
        if event_name in fraud_types and 'estimated_loss' not in event_data:
            if event_name == 'Scanner Avoidance':
                # Estimate average product value of $5-50 (LKR 280-14000, assume ~$20)
                total_estimated_loss += 20.0
            elif event_name == 'Barcode Switching':
                # Use price_gap if available, otherwise estimate $15 average loss
                if 'price_gap' not in event_data:
                    total_estimated_loss += 15.0
            elif event_name == 'Weight Discrepancies':
                # Estimate based on expected vs actual weight difference
                if 'expected_weight' in event_data and 'actual_weight' in event_data:
                    weight_diff = abs(event_data['actual_weight'] - event_data['expected_weight'])
                    # Assume $0.02 per gram of discrepancy
                    total_estimated_loss += (weight_diff * 0.02)

        # Inventory discrepancy losses
        if 'Inventory' in event_name:
            exp_inv = event_data.get('Expected_Inventory', event_data.get('expected_inventory', 0))
            act_inv = event_data.get('Actual_Inventory', event_data.get('actual_inventory', 0))
            if exp_inv and act_inv:
                # Use SKU to estimate value (simplified: assume $2 per unit)
                inv_diff = abs(exp_inv - act_inv)
                total_estimated_loss += (inv_diff * 2.0)

        timestamp_str = event.get('timestamp')
        if timestamp_str:
            try:
                ts = datetime.fromisoformat(timestamp_str)
                bucket_key = ts.strftime('%Y-%m-%d %H:%M')
                timeline_buckets[bucket_key] += 1
                hour_key = ts.strftime('%H:00')
                hourly_events[hour_key] += 1
                metrics['last_event_time'] = ts.isoformat()
            except ValueError:
                pass

        if event_name in fraud_types:
            metrics['fraud_count'] += 1
            metrics['high_priority_alerts'] += 1
        elif event_name in operational_types:
            metrics['operational_issues'] += 1
        elif event_name in inventory_types or 'Inventory' in event_name:
            metrics['inventory_issues'] += 1
        elif event_name in success_types:
            metrics['success_operations'] += 1

        if event_name == 'High-Risk Customer':
            high_risk_customers.append({
                'customer_id': event_data.get('customer_id'),
                'risk_score': event_data.get('risk_score'),
                'fraud_event_count': event_data.get('fraud_event_count'),
                'severity': event_data.get('severity'),
                'station_id': event_data.get('station_id'),
                'stations_involved': event_data.get('stations_involved', []),
                'station_summary': event_data.get('station_summary', [])
            })

    # Calculate advanced metrics
    metrics['severity_breakdown'] = dict(severity_counts)
    metrics['critical_alerts'] = critical_count
    metrics['financial_impact'] = round(total_estimated_loss, 2)

    if risk_events:
        avg_risk = sum(item['risk_score'] for item in risk_events) / len(risk_events)
        metrics['average_risk_score'] = round(avg_risk, 2)
        metrics['top_risk_events'] = sorted(
            risk_events,
            key=lambda x: x['risk_score'],
            reverse=True
        )[:5]

    metrics['high_risk_customers'] = sorted(
        high_risk_customers,
        key=lambda x: x.get('risk_score', 0),
        reverse=True
    )

    metrics['timeline'] = [
        {'time': key, 'count': count}
        for key, count in sorted(timeline_buckets.items())
    ]

    # Hourly distribution for peak analysis
    metrics['hourly_distribution'] = dict(sorted(hourly_events.items()))
    if hourly_events:
        peak_hour = max(hourly_events.items(), key=lambda x: x[1])
        metrics['peak_hour'] = f"{peak_hour[0]} ({peak_hour[1]} events)"

    # Station performance analysis
    for station, data in station_metrics.items():
        avg_station_risk = data['risk_sum'] / data['events'] if data['events'] > 0 else 0
        metrics['station_performance'][station] = {
            'total_events': data['events'],
            'fraud_events': data['fraud'],
            'operational_events': data['operational'],
            'average_risk': round(avg_station_risk, 2),
            'health_score': max(0, round(100 - (data['fraud'] * 10 + data['operational'] * 5), 1))
        }

    if station_metrics:
        most_problematic = max(station_metrics.items(), key=lambda x: x[1]['fraud'] + x[1]['operational'] * 0.5)
        metrics['most_problematic_station'] = most_problematic[0]

    # Calculate overall system scores with improved logic
    total_ops = metrics['fraud_count'] + metrics['operational_issues']
    if len(events) > 0:
        metrics['detection_efficiency'] = round((total_ops / len(events)) * 100, 1)

        # Improved fraud prevention score (normalized by total events)
        fraud_ratio = metrics['fraud_count'] / len(events) if len(events) > 0 else 0
        metrics['fraud_prevention_score'] = max(0, round(100 - (fraud_ratio * 200), 1))

        # Improved customer experience score (normalized by total events)
        ops_ratio = metrics['operational_issues'] / len(events) if len(events) > 0 else 0
        metrics['customer_experience_score'] = max(0, round(100 - (ops_ratio * 150), 1))

        # Improved system health with proper bounds
        critical_ratio = critical_count / len(events) if len(events) > 0 else 0
        critical_score = max(0, round(100 - (critical_ratio * 300), 1))

        metrics['system_health_score'] = max(0, min(100, round(
            (metrics['fraud_prevention_score'] * 0.4 +
             metrics['customer_experience_score'] * 0.4 +
             critical_score * 0.2), 1
        )))

    metrics['event_types'] = dict(metrics['event_types'])
    metrics['stations'] = dict(metrics['stations'])

    return metrics


@app.route('/')
def index():
    """Render main dashboard page"""
    return render_template('dashboard.html')


@app.route('/api/events')
def get_events():
    """API endpoint to get all events"""
    return jsonify(dashboard_state['events'])


@app.route('/api/summary')
def get_summary():
    """API endpoint to get summary statistics"""
    return jsonify(dashboard_state['summary'])


@app.route('/api/metrics')
def get_metrics():
    """API endpoint to get dashboard metrics"""
    return jsonify(dashboard_state['metrics'])


@app.route('/api/alerts')
def get_alerts():
    """API endpoint to get high-priority alerts"""
    return jsonify(dashboard_state['alerts'])


@app.route('/api/stations')
def get_stations():
    """API endpoint to get station-specific data"""
    return jsonify(dashboard_state['metrics'].get('station_performance', {}))


@app.route('/api/stations/<station_id>')
def get_station_details(station_id):
    """API endpoint to get specific station details"""
    station_events = [
        e for e in dashboard_state['events']
        if e.get('event_data', {}).get('station_id') == station_id
    ]
    station_metrics = calculate_metrics(station_events)
    return jsonify({
        'station_id': station_id,
        'events': station_events,
        'metrics': station_metrics
    })


@app.route('/api/event-types')
def get_event_types():
    """API endpoint to get event type breakdown"""
    return jsonify(dashboard_state['metrics'].get('event_types', {}))


@app.route('/api/refresh', methods=['POST'])
def refresh_data():
    """Refresh dashboard data"""
    data = request.json
    events_file = data.get('events_file', 'events.jsonl')

    if Path(events_file).exists():
        dashboard_state['events'] = load_events_from_file(events_file)
        dashboard_state['last_update'] = datetime.now().isoformat()
        dashboard_state['metrics'] = calculate_metrics(dashboard_state['events'])
        dashboard_state['metrics']['last_update'] = dashboard_state['last_update']

        # Extract high-priority alerts
        fraud_types = ['Scanner Avoidance', 'Barcode Switching', 'Weight Discrepancies', 'High-Risk Customer']
        dashboard_state['alerts'] = [
            e for e in dashboard_state['events']
            if e.get('event_data', {}).get('event_name') in fraud_types
        ][:10]  # Top 10 alerts

        return jsonify({'status': 'success', 'message': 'Data refreshed'})
    else:
        return jsonify({'status': 'error', 'message': 'Events file not found'}), 404


def start_dashboard(events_file: str = None, port: int = 5000):
    """Start the enhanced dashboard server with comprehensive monitoring"""
    if events_file:
        # Store absolute events file path for auto-reload
        events_file = str(Path(events_file).resolve())
        dashboard_state['events_file'] = events_file
        dashboard_state['events'] = load_events_from_file(events_file)
        dashboard_state['last_update'] = datetime.now().isoformat()
        if Path(events_file).exists():
            dashboard_state['last_file_mtime'] = os.path.getmtime(events_file)
        dashboard_state['metrics'] = calculate_metrics(dashboard_state['events'])
        dashboard_state['metrics']['last_update'] = dashboard_state['last_update']

        # Extract high-priority alerts
        fraud_types = ['Scanner Avoidance', 'Barcode Switching', 'Weight Discrepancies', 'High-Risk Customer']
        dashboard_state['alerts'] = [
            e for e in dashboard_state['events']
            if e.get('event_data', {}).get('event_name') in fraud_types
        ][:10]

        # Start file watcher thread for auto-reload
        watcher = threading.Thread(target=file_watcher_thread, daemon=True)
        watcher.start()
        print("[FILE-WATCHER] Auto-reload enabled - monitoring events file for changes...")

    print("\n" + "="*70)
    print("PROJECT SENTINEL - TEAM GMORA".center(70))
    print("="*70)
    print(f"\nDashboard Server Status:")
    print(f"   * URL: http://localhost:{port}")
    print(f"   * Events Loaded: {len(dashboard_state['events'])}")
    print(f"   * Fraud Alerts: {dashboard_state['metrics'].get('fraud_count', 0)}")
    print(f"   * Operational Issues: {dashboard_state['metrics'].get('operational_issues', 0)}")
    print(f"   * System Health: {dashboard_state['metrics'].get('system_health_score', 100)}%")
    print(f"   * Auto-Reload: {'Enabled' if events_file else 'Disabled'}")
    print(f"\n   Dashboard Features:")
    print(f"   - Real-time Event Monitoring")
    print(f"   - Advanced Risk Analytics")
    print(f"   - Station Performance Tracking")
    print(f"   - Financial Impact Assessment")
    print(f"   - High-Risk Customer Detection")
    print(f"   - Auto-reload on dataset changes")
    print(f"\n   Press Ctrl+C to stop the server\n")
    print("="*70 + "\n")

    app.run(host='0.0.0.0', port=port, debug=False, threaded=True)


if __name__ == '__main__':
    import argparse
    
    parser = argparse.ArgumentParser(description='Project Sentinel Dashboard')
    parser.add_argument('--events-file', type=str, default='events.jsonl',
                       help='Path to events.jsonl file')
    parser.add_argument('--port', type=int, default=5000,
                       help='Port to run dashboard on')
    
    args = parser.parse_args()
    start_dashboard(args.events_file, args.port)
