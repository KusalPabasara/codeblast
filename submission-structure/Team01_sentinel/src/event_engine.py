"""
Event Detection Engine - Main processing pipeline
"""
import json
from typing import Dict, List, Any
from datetime import datetime
from pathlib import Path
from collections import defaultdict

from data_loader import DataLoader
from algorithms import FraudDetectionAlgorithms, OperationalAlgorithms, InventoryAlgorithms
from config import EVENT_TYPES, THRESHOLDS


class EventDetectionEngine:
    """Main engine for detecting and processing retail events"""
    
    def __init__(self, data_dir: str, config: Dict[str, Any]):
        self.data_dir = Path(data_dir)
        self.config = config
        self.data_loader = DataLoader(data_dir)
        
        # Initialize algorithm modules
        self.fraud_detector = FraudDetectionAlgorithms({'THRESHOLDS': THRESHOLDS})
        self.ops_detector = OperationalAlgorithms({'THRESHOLDS': THRESHOLDS})
        self.inventory_detector = InventoryAlgorithms({'THRESHOLDS': THRESHOLDS})
        
        # Storage for processed events
        self.detected_events = []
        self.event_counter = 0
        
    def load_all_data(self):
        """Load all required data sources"""
        print("Loading data sources...")
        
        # Load reference data
        self.products = self.data_loader.load_products_catalog()
        self.customers = self.data_loader.load_customer_data()
        
        # Load streaming data
        self.pos_events = self.data_loader.load_jsonl_file("pos_transactions.jsonl")
        self.rfid_events = self.data_loader.load_jsonl_file("rfid_readings.jsonl")
        self.product_recognition = self.data_loader.load_jsonl_file("product_recognition.jsonl")
        self.queue_monitoring = self.data_loader.load_jsonl_file("queue_monitoring.jsonl")
        self.inventory_snapshots = self.data_loader.load_jsonl_file("inventory_snapshots.jsonl")
        
        print(f"Loaded {len(self.pos_events)} POS transactions")
        print(f"Loaded {len(self.rfid_events)} RFID readings")
        print(f"Loaded {len(self.product_recognition)} product recognitions")
        print(f"Loaded {len(self.queue_monitoring)} queue monitoring events")
        print(f"Loaded {len(self.inventory_snapshots)} inventory snapshots")
        print(f"Loaded {len(self.products)} products")
        print(f"Loaded {len(self.customers)} customers")
        
    def process_all_events(self):
        """Run all detection algorithms"""
        print("\n" + "="*60)
        print("RUNNING DETECTION ALGORITHMS")
        print("="*60)
        
        all_detected = []
        
        # 1. Fraud Detection
        print("\n[1/8] Detecting Scanner Avoidance...")
        scanner_avoidance = self.fraud_detector.detect_scanner_avoidance(
            self.rfid_events, 
            self.pos_events,
            THRESHOLDS['rfid_pos_time_window'],
            self.products
        )
        all_detected.extend(scanner_avoidance)
        print(f"   Found {len(scanner_avoidance)} scanner avoidance events")
        
        print("\n[2/8] Detecting Barcode Switching...")
        barcode_switching = self.fraud_detector.detect_barcode_switching(
            self.product_recognition,
            self.pos_events,
            THRESHOLDS['product_recognition_confidence'],
            self.products
        )
        all_detected.extend(barcode_switching)
        print(f"   Found {len(barcode_switching)} barcode switching events")
        
        print("\n[3/8] Detecting Weight Discrepancies...")
        weight_discrepancies = self.fraud_detector.detect_weight_discrepancies(
            self.pos_events,
            self.products,
            THRESHOLDS['weight_tolerance_percent']
        )
        all_detected.extend(weight_discrepancies)
        print(f"   Found {len(weight_discrepancies)} weight discrepancy events")
        
        # 2. Operational Monitoring
        print("\n[4/8] Detecting Long Queues...")
        long_queues = self.ops_detector.detect_long_queue(
            self.queue_monitoring,
            THRESHOLDS['queue_length_alert']
        )
        all_detected.extend(long_queues)
        print(f"   Found {len(long_queues)} long queue events")
        
        print("\n[5/8] Detecting Long Wait Times...")
        long_waits = self.ops_detector.detect_long_wait_time(
            self.queue_monitoring,
            THRESHOLDS['wait_time_alert']
        )
        all_detected.extend(long_waits)
        print(f"   Found {len(long_waits)} long wait time events")
        
        print("\n[6/8] Detecting System Crashes...")
        # Check status fields for System Crash events
        system_crashes = self.ops_detector.detect_system_crashes(
            pos_events=self.pos_events,
            product_recognition=self.product_recognition,
            rfid_events=self.rfid_events,
            queue_events=self.queue_monitoring
        )
        all_detected.extend(system_crashes)
        print(f"   Found {len(system_crashes)} system crash events")
        
        print("\n[7/8] Analyzing Staffing Needs...")
        staffing_needs = self.ops_detector.recommend_staffing(
            self.queue_monitoring,
            THRESHOLDS['queue_length_alert'],
            THRESHOLDS['wait_time_alert']
        )
        all_detected.extend(staffing_needs)
        print(f"   Found {len(staffing_needs)} staffing need events")

        print("\n[8/8] Scoring Station Pressure...")
        station_pressure = self.ops_detector.detect_station_pressure(
            self.queue_monitoring,
            THRESHOLDS['queue_length_alert'],
            THRESHOLDS['station_alert_wait_threshold'],
            THRESHOLDS['station_alert_occurrences'],
            THRESHOLDS['station_alert_window_minutes']
        )
        all_detected.extend(station_pressure)
        print(f"   Found {len(station_pressure)} station performance alerts")

        # Aggregate high-risk customers after primary fraud detections
        fraud_events = scanner_avoidance + barcode_switching + weight_discrepancies
        high_risk_customers = self.fraud_detector.detect_high_risk_customers(
            fraud_events,
            THRESHOLDS['high_risk_customer_events'],
            THRESHOLDS['high_risk_customer_score']
        )
        all_detected.extend(high_risk_customers)
        if high_risk_customers:
            print(f"\n[BONUS] Identified {len(high_risk_customers)} high-risk customers")
        
        # 3. Inventory Analysis (if snapshot available)
        if self.inventory_snapshots:
            print("\n[BONUS] Detecting Inventory Discrepancies...")
            initial_snapshot = self.inventory_snapshots[0]['data']
            inventory_discrepancies = self.inventory_detector.detect_inventory_discrepancies(
                initial_snapshot,
                self.rfid_events,
                self.pos_events,
                THRESHOLDS['inventory_discrepancy_threshold']
            )
            all_detected.extend(inventory_discrepancies)
            print(f"   Found {len(inventory_discrepancies)} inventory discrepancy events")
        
        # 4. Track Successful Operations
        print("\n[BONUS] Tracking Successful Operations...")
        successful = self.inventory_detector.track_successful_operations(
            self.pos_events,
            self.rfid_events,
            self.product_recognition
        )
        all_detected.extend(successful)
        print(f"   Found {len(successful)} successful operations")
        
        self.detected_events = all_detected
        
        print("\n" + "="*60)
        print(f"TOTAL EVENTS DETECTED: {len(all_detected)}")
        print("="*60)
        
        return all_detected
    
    def format_event_output(self, event: Dict[str, Any]) -> Dict[str, Any]:
        """Format detected event into required output schema"""
        event_type = event['type']
        event_id = EVENT_TYPES.get(event_type, {}).get('id', 'E999')
        event_name = EVENT_TYPES.get(event_type, {}).get('name', 'Unknown Event')
        
        # Build event_data based on type
        event_data = {'event_name': event_name}
        
        if event_type == 'SUCCESS':
            event_data.update({
                'station_id': event.get('station_id'),
                'customer_id': event.get('customer_id'),
                'product_sku': event.get('product_sku'),
                'service_score': event.get('service_score', 95)
            })
        
        elif event_type == 'SCANNER_AVOIDANCE':
            event_data.update({
                'station_id': event.get('station_id'),
                'product_sku': event.get('product_sku'),
                'estimated_loss': event.get('estimated_loss')
            })
        
        elif event_type == 'BARCODE_SWITCHING':
            event_data.update({
                'station_id': event.get('station_id'),
                'customer_id': event.get('customer_id'),
                'actual_sku': event.get('actual_sku'),
                'scanned_sku': event.get('scanned_sku'),
                'confidence': event.get('confidence'),
                'price_gap': event.get('price_gap'),
                'predicted_price': event.get('predicted_price'),
                'scanned_price': event.get('scanned_price')
            })
        
        elif event_type == 'WEIGHT_DISCREPANCY':
            event_data.update({
                'station_id': event.get('station_id'),
                'customer_id': event.get('customer_id'),
                'product_sku': event.get('product_sku'),
                'expected_weight': int(event.get('expected_weight', 0)),
                'actual_weight': int(event.get('actual_weight', 0)),
                'difference_percent': round(event.get('difference_percent', 0), 2),
                'estimated_loss': event.get('estimated_loss')
            })
        
        elif event_type == 'SYSTEM_CRASH':
            event_data.update({
                'station_id': event.get('station_id'),
                'duration_seconds': event.get('duration_seconds')
            })
        
        elif event_type == 'LONG_QUEUE':
            event_data.update({
                'station_id': event.get('station_id'),
                'num_of_customers': event.get('num_of_customers')
            })
        
        elif event_type == 'LONG_WAIT':
            event_data.update({
                'station_id': event.get('station_id'),
                'wait_time_seconds': int(event.get('wait_time_seconds', 0))
            })
        
        elif event_type == 'INVENTORY_DISCREPANCY':
            event_data.update({
                'SKU': event.get('sku'),
                'Expected_Inventory': event.get('expected_inventory'),
                'Actual_Inventory': event.get('actual_inventory'),
                'Difference_Percent': round(event.get('difference_percent', 0), 2)
            })
        
        elif event_type == 'STAFFING_NEEDS':
            event_data.update({
                'station_id': event.get('station_id'),
                'Staff_type': event.get('staff_type')
            })
        
        elif event_type == 'CHECKOUT_ACTION':
            event_data.update({
                'station_id': event.get('station_id'),
                'Action': event.get('action', 'Open')
            })
        
        elif event_type == 'HIGH_RISK_CUSTOMER':
            event_data.update({
                'customer_id': event.get('customer_id'),
                'fraud_event_count': event.get('fraud_event_count'),
                'recent_events': event.get('recent_events', []),
                'station_id': event.get('station_id'),
                'stations_involved': event.get('stations_involved'),
                'station_summary': event.get('station_summary')
            })
        
        elif event_type == 'STATION_PERFORMANCE_ALERT':
            event_data.update({
                'station_id': event.get('station_id'),
                'issues_detected': event.get('issues_detected'),
                'max_queue': event.get('max_queue'),
                'max_wait_seconds': int(event.get('max_wait_seconds', 0)),
                'average_queue': event.get('average_queue'),
                'average_wait_seconds': event.get('average_wait_seconds'),
                'recent_samples': event.get('recent_samples', []),
                'window_minutes': event.get('window_minutes')
            })
        
        # Clean up None values
        event_data = {k: v for k, v in event_data.items() if v is not None}
        if event.get('risk_score') is not None:
            event_data['risk_score'] = float(round(event.get('risk_score'), 1))
        if event.get('severity'):
            event_data['severity'] = event.get('severity')
        
        output_event = {
            'timestamp': event['timestamp'],
            'event_id': f"{event_id}",
            'event_data': event_data
        }
        
        return output_event
    
    def save_events(self, output_path: str):
        """Save detected events to JSONL file"""
        output_file = Path(output_path)
        output_file.parent.mkdir(parents=True, exist_ok=True)
        
        # Sort events by timestamp
        sorted_events = sorted(self.detected_events, key=lambda x: x['timestamp'])
        
        with open(output_file, 'w', encoding='utf-8') as f:
            for event in sorted_events:
                formatted_event = self.format_event_output(event)
                f.write(json.dumps(formatted_event, separators=(',', ':')) + '\n')
        
        print(f"\n[OK] Saved {len(sorted_events)} events to {output_path}")
        
    def generate_summary_report(self) -> Dict[str, Any]:
        """Generate summary statistics"""
        event_counts = {}
        severity_counts = defaultdict(int)
        total_risk = 0.0
        risk_event_count = 0
        station_load = defaultdict(int)
        high_risk_customers = []
        for event in self.detected_events:
            event_type = event['type']
            event_counts[event_type] = event_counts.get(event_type, 0) + 1
            severity = event.get('severity') or 'UNSPECIFIED'
            severity_counts[severity] += 1
            if event.get('risk_score') is not None:
                total_risk += event.get('risk_score')
                risk_event_count += 1
            station_id = event.get('station_id')
            if station_id:
                station_load[station_id] += 1
            if event_type == 'HIGH_RISK_CUSTOMER':
                high_risk_customers.append({
                    'customer_id': event.get('customer_id'),
                    'risk_score': event.get('risk_score'),
                    'fraud_event_count': event.get('fraud_event_count'),
                    'station_id': event.get('station_id'),
                    'stations_involved': event.get('stations_involved'),
                    'station_summary': event.get('station_summary')
                })

        average_risk = round(total_risk / risk_event_count, 2) if risk_event_count else 0.0
        top_risk_events = sorted(
            [e for e in self.detected_events if e.get('risk_score')],
            key=lambda x: x.get('risk_score', 0),
            reverse=True
        )[:5]
        top_risk_highlights = [
            {
                'type': event['type'],
                'timestamp': event['timestamp'],
                'risk_score': event.get('risk_score'),
                'severity': event.get('severity'),
                'station_id': event.get('station_id')
            }
            for event in top_risk_events
        ]
        busiest_stations = sorted(
            station_load.items(),
            key=lambda x: x[1],
            reverse=True
        )[:5]
        
        summary = {
            'total_events': len(self.detected_events),
            'event_breakdown': event_counts,
            'fraud_events': (
                event_counts.get('SCANNER_AVOIDANCE', 0) +
                event_counts.get('BARCODE_SWITCHING', 0) +
                event_counts.get('WEIGHT_DISCREPANCY', 0)
            ),
            'operational_events': (
                event_counts.get('LONG_QUEUE', 0) +
                event_counts.get('LONG_WAIT', 0) +
                event_counts.get('SYSTEM_CRASH', 0) +
                event_counts.get('STAFFING_NEEDS', 0) +
                event_counts.get('STATION_PERFORMANCE_ALERT', 0)
            ),
            'inventory_events': event_counts.get('INVENTORY_DISCREPANCY', 0),
            'successful_operations': event_counts.get('SUCCESS', 0),
            'severity_breakdown': dict(severity_counts),
            'average_risk_score': average_risk,
            'high_risk_customers': high_risk_customers,
            'top_risk_events': top_risk_highlights,
            'busiest_stations': [{'station_id': station, 'event_count': count} for station, count in busiest_stations]
        }
        
        return summary
