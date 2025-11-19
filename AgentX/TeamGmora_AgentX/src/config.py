"""
Configuration and Thresholds for Sentinel Fraud Detection System
"""

# Event Type Definitions
EVENT_TYPES = {
    'SUCCESS': {'id': 'E000', 'name': 'Successful Operation'},
    'SCANNER_AVOIDANCE': {'id': 'E001', 'name': 'Scanner Avoidance'},
    'BARCODE_SWITCHING': {'id': 'E002', 'name': 'Barcode Switching'},
    'WEIGHT_DISCREPANCY': {'id': 'E003', 'name': 'Weight Discrepancies'},
    'SYSTEM_CRASH': {'id': 'E004', 'name': 'Unexpected Systems Crash'},
    'LONG_QUEUE': {'id': 'E005', 'name': 'Long Queue Length'},
    'LONG_WAIT': {'id': 'E006', 'name': 'Long Wait Time'},
    'INVENTORY_DISCREPANCY': {'id': 'E007', 'name': 'Inventory Discrepancy'},
    'STAFFING_NEEDS': {'id': 'E008', 'name': 'Staffing Needs'},
    'CHECKOUT_ACTION': {'id': 'E009', 'name': 'Checkout Station Action'},
}

# Detection Thresholds
THRESHOLDS = {
    # Fraud Detection
    'weight_tolerance_percent': 15,  # Allow 15% weight variance
    'product_recognition_confidence': 0.60,  # Minimum confidence for barcode switching detection
    'rfid_pos_time_window': 10,  # Seconds to match RFID with POS
    
    # Operational Thresholds
    'queue_length_alert': 5,  # Alert when queue exceeds 5 customers
    'wait_time_alert': 60,  # Alert when wait time exceeds 60 seconds
    'system_crash_gap': 30,  # Seconds of silence indicating crash
    
    # Inventory
    'inventory_discrepancy_threshold': 10,  # Percent difference threshold
    
    # Staffing
    'staffing_queue_threshold': 7,  # Queue length requiring staff
    'staffing_wait_threshold': 300,  # Wait time requiring staff (5 minutes)
    
    # Risk Scoring
    'high_risk_customer_events': 2,  # Number of fraud events to flag customer
    'high_risk_customer_score': 80,  # Minimum risk score for flagging
    
    # Station Performance
    'station_alert_wait_threshold': 60,  # Wait time for station pressure
    'station_alert_occurrences': 3,  # Number of incidents to trigger alert
    'station_alert_window_minutes': 30,  # Time window for aggregation
}

# Dashboard Configuration
DASHBOARD_CONFIG = {
    'title': 'Sentinel - Self-Checkout Fraud Detection System',
    'refresh_interval': 5000,  # milliseconds
    'port': 5000,
    'host': '0.0.0.0'
}

