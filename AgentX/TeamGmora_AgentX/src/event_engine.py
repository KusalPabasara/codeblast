"""
Event Detection Engine - Main processing pipeline
"""
import json
from pathlib import Path
from typing import Dict, List, Any
from collections import defaultdict

from data_loader import DataLoader
from algorithms import FraudDetectionAlgorithms, OperationalAlgorithms, InventoryAlgorithms
from config import EVENT_TYPES, THRESHOLDS


class EventDetectionEngine:
    """Main engine for detecting and processing retail events"""
    
    def __init__(self, data_dir: str):
        self.data_dir = Path(data_dir)
        self.data_loader = DataLoader(data_dir)
        
        # Initialize algorithm modules
        self.fraud_detector = FraudDetectionAlgorithms(THRESHOLDS)
        self.ops_detector = OperationalAlgorithms(THRESHOLDS)
        self.inventory_detector = InventoryAlgorithms(THRESHOLDS)
        
        # Storage for events and data
        self.detected_events = []
        self.products = {}
        self.customers = {}
        
    def load_all_data(self):
        """Load all required data sources"""
        print("\n🔄 Loading data sources...")
        
        # Load reference data
        self.products = self.data_loader.load_products_catalog()
        self.customers = self.data_loader.load_customer_data()
        
        # Load event streams
        self.pos_events = self.data_loader.load_jsonl_file("pos_transactions.jsonl")
        self.rfid_events = self.data_loader.load_jsonl_file("rfid_readings.jsonl")
        self.recognition_events = self.data_loader.load_jsonl_file("product_recognition.jsonl")
        self.queue_events = self.data_loader.load_jsonl_file("queue_monitoring.jsonl")
        self.inventory_snapshots = self.data_loader.load_jsonl_file("inventory_snapshots.jsonl")
        
        print(f"✓ Loaded {len(self.pos_events)} POS transactions")
        print(f"✓ Loaded {len(self.rfid_events)} RFID readings")
        print(f"✓ Loaded {len(self.recognition_events)} product recognitions")
        print(f"✓ Loaded {len(self.queue_events)} queue monitoring events")
        print(f"✓ Loaded {len(self.inventory_snapshots)} inventory snapshots")
        print(f"✓ Loaded {len(self.products)} products in catalog")
        print(f"✓ Loaded {len(self.customers)} customer records")
        
    def process_all_events(self):
        """Run all detection algorithms"""
        print("\n" + "="*70)
        print("🔍 RUNNING DETECTION ALGORITHMS")
        print("="*70)
        
        all_detected = []
        
        # Algorithm 1: Scanner Avoidance
        print("\n[1/9] Detecting Scanner Avoidance...")
        scanner_avoidance = self.fraud_detector.detect_scanner_avoidance(
            self.rfid_events,
            self.pos_events,
            THRESHOLDS['rfid_pos_time_window'],
            self.products
        )
        all_detected.extend(scanner_avoidance)
        print(f"   ✓ Found {len(scanner_avoidance)} scanner avoidance events")
        
        # Algorithm 2: Barcode Switching
        print("\n[2/9] Detecting Barcode Switching...")
        barcode_switching = self.fraud_detector.detect_barcode_switching(
            self.recognition_events,
            self.pos_events,
            THRESHOLDS['product_recognition_confidence'],
            self.products
        )
        all_detected.extend(barcode_switching)
        print(f"   ✓ Found {len(barcode_switching)} barcode switching events")
        
        # Algorithm 3: Weight Discrepancies
        print("\n[3/9] Detecting Weight Discrepancies...")
        weight_discrepancies = self.fraud_detector.detect_weight_discrepancies(
            self.pos_events,
            self.products,
            THRESHOLDS['weight_tolerance_percent']
        )
        all_detected.extend(weight_discrepancies)
        print(f"   ✓ Found {len(weight_discrepancies)} weight discrepancy events")
        
        # Algorithm 4: Long Queues
        print("\n[4/9] Detecting Long Queues...")
        long_queues = self.ops_detector.detect_long_queues(
            self.queue_events,
            THRESHOLDS['queue_length_alert']
        )
        all_detected.extend(long_queues)
        print(f"   ✓ Found {len(long_queues)} long queue events")
        
        # Algorithm 5: Long Wait Times
        print("\n[5/9] Detecting Long Wait Times...")
        long_waits = self.ops_detector.detect_long_wait_times(
            self.queue_events,
            THRESHOLDS['wait_time_alert']
        )
        all_detected.extend(long_waits)
        print(f"   ✓ Found {len(long_waits)} long wait time events")
        
        # Algorithm 6: System Crashes
        print("\n[6/9] Detecting System Crashes...")
        all_events_merged = self.data_loader.merge_all_events()
        system_crashes = self.ops_detector.detect_system_crashes(all_events_merged)
        all_detected.extend(system_crashes)
        print(f"   ✓ Found {len(system_crashes)} system crash events")
        
        # Algorithm 7: Staffing Needs
        print("\n[7/9] Analyzing Staffing Needs...")
        staffing_needs = self.ops_detector.detect_staffing_needs(
            self.queue_events,
            THRESHOLDS['queue_length_alert'],
            THRESHOLDS['staffing_wait_threshold']
        )
        all_detected.extend(staffing_needs)
        print(f"   ✓ Found {len(staffing_needs)} staffing need events")
        
        # Algorithm 8: Inventory Discrepancies
        if self.inventory_snapshots:
            print("\n[8/9] Detecting Inventory Discrepancies...")
            initial_snapshot = self.inventory_snapshots[0]['data']
            inventory_discrepancies = self.inventory_detector.detect_inventory_discrepancies(
                initial_snapshot,
                self.rfid_events,
                self.pos_events,
                THRESHOLDS['inventory_discrepancy_threshold']
            )
            all_detected.extend(inventory_discrepancies)
            print(f"   ✓ Found {len(inventory_discrepancies)} inventory discrepancy events")
        
        # Algorithm 9: Successful Operations
        print("\n[9/9] Tracking Successful Operations...")
        successful = self.inventory_detector.track_successful_operations(
            self.pos_events,
            self.rfid_events,
            self.recognition_events
        )
        all_detected.extend(successful)
        print(f"   ✓ Found {len(successful)} successful operations")
        
        self.detected_events = all_detected
        
        print("\n" + "="*70)
        print(f"✅ TOTAL EVENTS DETECTED: {len(all_detected)}")
        print("="*70)
        
        return all_detected
    
    def format_event_output(self, event: Dict[str, Any]) -> Dict[str, Any]:
        """Format detected event into required output schema"""
        event_type = event['type']
        event_id = EVENT_TYPES.get(event_type, {}).get('id', 'E999')
        event_name = EVENT_TYPES.get(event_type, {}).get('name', 'Unknown Event')
        
        # Build event_data based on type
        event_data = {'event_name': event_name}
        
        # Copy relevant fields
        for key, value in event.items():
            if key not in ['timestamp', 'type', 'risk_score', 'severity', '_source']:
                if value is not None:
                    event_data[key] = value
        
        # Format output
        output_event = {
            'timestamp': event['timestamp'],
            'event_id': event_id,
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
        
        print(f"\n✅ Saved {len(sorted_events)} events to {output_path}")
        
    def generate_summary(self) -> Dict[str, Any]:
        """Generate summary statistics"""
        event_counts = defaultdict(int)
        severity_counts = defaultdict(int)
        station_load = defaultdict(int)
        total_risk = 0
        risk_count = 0
        
        for event in self.detected_events:
            event_type = event['type']
            event_counts[event_type] += 1
            
            severity = event.get('severity', 'UNKNOWN')
            severity_counts[severity] += 1
            
            station_id = event.get('station_id')
            if station_id:
                station_load[station_id] += 1
            
            if 'risk_score' in event:
                total_risk += event['risk_score']
                risk_count += 1
        
        avg_risk = round(total_risk / risk_count, 2) if risk_count > 0 else 0
        
        # Top stations by event count
        top_stations = sorted(station_load.items(), key=lambda x: x[1], reverse=True)[:5]
        
        summary = {
            'total_events': len(self.detected_events),
            'event_breakdown': dict(event_counts),
            'severity_breakdown': dict(severity_counts),
            'average_risk_score': avg_risk,
            'fraud_events': (
                event_counts['SCANNER_AVOIDANCE'] +
                event_counts['BARCODE_SWITCHING'] +
                event_counts['WEIGHT_DISCREPANCY']
            ),
            'operational_events': (
                event_counts['LONG_QUEUE'] +
                event_counts['LONG_WAIT'] +
                event_counts['SYSTEM_CRASH'] +
                event_counts['STAFFING_NEEDS']
            ),
            'inventory_events': event_counts['INVENTORY_DISCREPANCY'],
            'successful_operations': event_counts['SUCCESS'],
            'top_stations': [
                {'station_id': station, 'event_count': count}
                for station, count in top_stations
            ]
        }
        
        return summary

