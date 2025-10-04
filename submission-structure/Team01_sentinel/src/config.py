"""
Configuration settings for Project Sentinel
"""

# Event IDs and Names
EVENT_TYPES = {
    "SUCCESS": {"id": "E000", "name": "Succes Operation"},
    "SCANNER_AVOIDANCE": {"id": "E001", "name": "Scanner Avoidance"},
    "BARCODE_SWITCHING": {"id": "E002", "name": "Barcode Switching"},
    "WEIGHT_DISCREPANCY": {"id": "E003", "name": "Weight Discrepancies"},
    "SYSTEM_CRASH": {"id": "E004", "name": "Unexpected Systems Crash"},
    "LONG_QUEUE": {"id": "E005", "name": "Long Queue Length"},
    "LONG_WAIT": {"id": "E006", "name": "Long Wait Time"},
    "INVENTORY_DISCREPANCY": {"id": "E007", "name": "Inventory Discrepancy"},
    "STAFFING_NEEDS": {"id": "E008", "name": "Staffing Needs"},
    "CHECKOUT_ACTION": {"id": "E009", "name": "Checkout Station Action"},
    "HIGH_RISK_CUSTOMER": {"id": "E010", "name": "High-Risk Customer"},
    "STATION_PERFORMANCE_ALERT": {"id": "E011", "name": "Station Performance Alert"}
}

# Detection Thresholds
THRESHOLDS = {
    "weight_tolerance_percent": 15,  # Weight difference tolerance
    "product_recognition_confidence": 0.75,  # Minimum confidence for product recognition
    "queue_length_alert": 5,  # Number of customers
    "wait_time_alert": 300,  # Seconds (5 minutes)
    "dwell_time_alert": 180,  # Seconds (3 minutes)
    "inventory_discrepancy_threshold": 10,  # Percentage difference
    "system_crash_duration": 30,  # Seconds without activity
    "rfid_pos_time_window": 10,  # Seconds for matching RFID to POS
    "station_alert_wait_threshold": 300,  # Seconds for persistent dwell time pressure
    "station_alert_occurrences": 3,  # Minimum breaches before alerting
    "station_alert_window_minutes": 15,  # Look-back window for station pressure
    "high_risk_customer_events": 2,  # Minimum fraud events before aggregation
    "high_risk_customer_score": 80  # Minimum average risk to flag customer
}

# Data Sources
DATA_SOURCES = {
    "pos_transactions": "pos_transactions.jsonl",
    "rfid_readings": "rfid_readings.jsonl",
    "product_recognition": "product_recognition.jsonl",
    "queue_monitoring": "queue_monitoring.jsonl",
    "inventory_snapshots": "inventory_snapshots.jsonl",
    "products_list": "products_list.csv",
    "customer_data": "customer_data.csv"
}

# Stream Server Configuration
STREAM_SERVER = {
    "host": "127.0.0.1",
    "port": 8765,
    "speed": 10,
    "loop": True
}
