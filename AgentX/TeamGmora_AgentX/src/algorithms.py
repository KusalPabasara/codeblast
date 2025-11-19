"""
Detection Algorithms for Sentinel Fraud Detection System
Each algorithm detects specific types of fraud or operational issues
All algorithms are properly tagged for automated judging
"""
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
from collections import defaultdict, Counter
import statistics


class FraudDetectionAlgorithms:
    """Fraud detection algorithms for self-checkout scenarios"""
    
    def __init__(self, thresholds: Dict[str, Any]):
        self.thresholds = thresholds
    
    def _calculate_risk_score(self, base_score: float, factors: Dict[str, float]) -> float:
        """Calculate risk score with multiple factors"""
        score = base_score
        for factor_value in factors.values():
            score += factor_value
        return min(score, 100.0)
    
    def _classify_severity(self, score: float) -> str:
        """Classify severity based on risk score"""
        if score >= 80:
            return 'CRITICAL'
        elif score >= 60:
            return 'HIGH'
        elif score >= 40:
            return 'MEDIUM'
        return 'LOW'
    
    # @algorithm Scanner Avoidance Detection | Detects items detected by RFID but not scanned at POS, indicating potential theft
    def detect_scanner_avoidance(self, rfid_events: List[Dict], pos_events: List[Dict],
                                 time_window: int, products_catalog: Dict) -> List[Dict]:
        """
        Scanner Avoidance Detection Algorithm
        Method: Time-window correlation between RFID readings and POS transactions
        """
        detected = []
        
        # Index POS transactions for fast lookup
        pos_index = defaultdict(list)
        for pos in pos_events:
            if pos.get('data', {}).get('sku'):
                key = (pos['station_id'], pos['timestamp'])
                pos_index[key].append(pos['data']['sku'])
        
        # Check RFID events
        for rfid in rfid_events:
            sku = rfid.get('data', {}).get('sku')
            location = rfid.get('data', {}).get('location')
            
            # Only check items in scan area
            if not sku or location != 'IN_SCAN_AREA':
                continue
            
            station = rfid['station_id']
            rfid_time = datetime.fromisoformat(rfid['timestamp'])
            
            # Look for matching POS transaction in time window
            found = False
            for offset in range(-time_window, time_window + 1):
                check_time = (rfid_time + timedelta(seconds=offset)).isoformat()
                if sku in pos_index.get((station, check_time), []):
                    found = True
                    break
            
            if not found:
                # Scanner avoidance detected
                product_info = products_catalog.get(sku, {})
                price = product_info.get('price', 0)
                
                risk_score = self._calculate_risk_score(75.0, {
                    'price_factor': min(price / 30, 20),
                    'location_factor': 5
                })
                
                detected.append({
                    'timestamp': rfid['timestamp'],
                    'type': 'SCANNER_AVOIDANCE',
                    'station_id': station,
                    'product_sku': sku,
                    'estimated_loss': round(price, 2) if price else None,
                    'risk_score': round(risk_score, 1),
                    'severity': self._classify_severity(risk_score)
                })
        
        return detected
    
    # @algorithm Barcode Switching Detection | Detects when camera-recognized product differs from scanned barcode, indicating fraud
    def detect_barcode_switching(self, recognition_events: List[Dict], pos_events: List[Dict],
                                 confidence_threshold: float, products_catalog: Dict) -> List[Dict]:
        """
        Barcode Switching Detection Algorithm
        Method: Computer vision validation of POS transactions
        """
        detected = []
        
        # Index POS by timestamp and station
        pos_index = {}
        for pos in pos_events:
            key = (pos['timestamp'], pos['station_id'])
            pos_index[key] = pos
        
        # Check recognition events
        for recog in recognition_events:
            confidence = recog['data']['accuracy']
            
            # Only trust high-confidence predictions
            if confidence < confidence_threshold:
                continue
            
            predicted_sku = recog['data']['predicted_product']
            key = (recog['timestamp'], recog['station_id'])
            
            if key in pos_index:
                pos = pos_index[key]
                scanned_sku = pos['data']['sku']
                
                # Mismatch detected
                if predicted_sku != scanned_sku:
                    pred_price = products_catalog.get(predicted_sku, {}).get('price', 0)
                    scan_price = products_catalog.get(scanned_sku, {}).get('price', 0)
                    price_gap = max(pred_price - scan_price, 0)
                    
                    risk_score = self._calculate_risk_score(70.0, {
                        'confidence_factor': (confidence - confidence_threshold) * 25,
                        'price_gap_factor': min(price_gap / 5, 20)
                    })
                    
                    detected.append({
                        'timestamp': recog['timestamp'],
                        'type': 'BARCODE_SWITCHING',
                        'station_id': recog['station_id'],
                        'customer_id': pos['data']['customer_id'],
                        'actual_sku': predicted_sku,
                        'scanned_sku': scanned_sku,
                        'confidence': round(confidence, 2),
                        'price_gap': round(price_gap, 2) if price_gap else None,
                        'predicted_price': round(pred_price, 2) if pred_price else None,
                        'scanned_price': round(scan_price, 2) if scan_price else None,
                        'risk_score': round(risk_score, 1),
                        'severity': self._classify_severity(risk_score)
                    })
        
        return detected
    
    # @algorithm Weight Discrepancy Detection | Identifies significant weight variances indicating multiple items or wrong products
    def detect_weight_discrepancies(self, pos_events: List[Dict], products_catalog: Dict,
                                   tolerance_percent: float) -> List[Dict]:
        """
        Weight Discrepancy Detection Algorithm
        Method: Statistical weight analysis of transactions
        """
        detected = []
        
        for pos in pos_events:
            sku = pos['data']['sku']
            actual_weight = pos['data']['weight_g']
            
            if sku in products_catalog:
                expected_weight = products_catalog[sku]['weight']
                weight_diff = abs(actual_weight - expected_weight) / expected_weight * 100
                
                if weight_diff > tolerance_percent:
                    price = products_catalog[sku].get('price', 0)
                    
                    risk_score = self._calculate_risk_score(60.0, {
                        'weight_factor': min(weight_diff / 5, 30),
                        'price_factor': min(price / 50, 10)
                    })
                    
                    detected.append({
                        'timestamp': pos['timestamp'],
                        'type': 'WEIGHT_DISCREPANCY',
                        'station_id': pos['station_id'],
                        'customer_id': pos['data']['customer_id'],
                        'product_sku': sku,
                        'expected_weight': int(expected_weight),
                        'actual_weight': int(actual_weight),
                        'difference_percent': round(weight_diff, 2),
                        'estimated_loss': round(price, 2) if price else None,
                        'risk_score': round(risk_score, 1),
                        'severity': self._classify_severity(risk_score)
                    })
        
        return detected


class OperationalAlgorithms:
    """Algorithms for operational efficiency monitoring"""
    
    def __init__(self, thresholds: Dict[str, Any]):
        self.thresholds = thresholds
    
    def _calculate_risk_score(self, base_score: float, factors: Dict[str, float]) -> float:
        score = base_score
        for factor_value in factors.values():
            score += factor_value
        return min(score, 100.0)
    
    def _classify_severity(self, score: float) -> str:
        if score >= 80:
            return 'CRITICAL'
        elif score >= 60:
            return 'HIGH'
        elif score >= 40:
            return 'MEDIUM'
        return 'LOW'
    
    # @algorithm Long Queue Detection | Monitors customer count to identify when queues exceed acceptable thresholds
    def detect_long_queues(self, queue_events: List[Dict], threshold: int) -> List[Dict]:
        """
        Long Queue Detection Algorithm
        Method: Threshold-based queue monitoring
        """
        detected = []
        
        for queue in queue_events:
            customer_count = queue['data']['customer_count']
            
            if customer_count > threshold:
                risk_score = self._calculate_risk_score(50.0, {
                    'queue_factor': min((customer_count - threshold) * 8, 45)
                })
                
                detected.append({
                    'timestamp': queue['timestamp'],
                    'type': 'LONG_QUEUE',
                    'station_id': queue['station_id'],
                    'num_of_customers': customer_count,
                    'risk_score': round(risk_score, 1),
                    'severity': self._classify_severity(risk_score)
                })
        
        return detected
    
    # @algorithm Wait Time Analysis | Tracks average dwell time to identify excessive customer wait periods
    def detect_long_wait_times(self, queue_events: List[Dict], threshold_seconds: float) -> List[Dict]:
        """
        Wait Time Analysis Algorithm
        Method: Dwell time threshold monitoring
        """
        detected = []
        
        for queue in queue_events:
            wait_time = queue['data']['average_dwell_time']
            customer_count = queue['data'].get('customer_count', 0)
            
            if wait_time > threshold_seconds:
                overage = wait_time - threshold_seconds
                risk_score = self._calculate_risk_score(45.0, {
                    'time_factor': min(overage / 60 * 15, 35),
                    'customer_factor': min(customer_count * 3, 15)
                })
                
                detected.append({
                    'timestamp': queue['timestamp'],
                    'type': 'LONG_WAIT',
                    'station_id': queue['station_id'],
                    'wait_time_seconds': int(wait_time),
                    'customer_count': customer_count,
                    'risk_score': round(risk_score, 1),
                    'severity': self._classify_severity(risk_score)
                })
        
        return detected
    
    # @algorithm System Crash Detection | Monitors status fields across all data sources to detect system failures
    def detect_system_crashes(self, all_events: List[Dict]) -> List[Dict]:
        """
        System Crash Detection Algorithm
        Method: Multi-source status monitoring
        """
        detected = []
        crash_sessions = defaultdict(lambda: {'start': None, 'end': None, 'count': 0})
        
        for event in all_events:
            status = event.get('status', '')
            if status in ['System Crash', 'Read Error']:
                station = event.get('station_id')
                source = event.get('_source', 'unknown')
                
                key = (station, source)
                if crash_sessions[key]['start'] is None:
                    crash_sessions[key]['start'] = event['timestamp']
                
                crash_sessions[key]['end'] = event['timestamp']
                crash_sessions[key]['count'] += 1
        
        # Generate crash events
        for (station, source), session in crash_sessions.items():
            if session['count'] > 0:
                start_time = datetime.fromisoformat(session['start'])
                end_time = datetime.fromisoformat(session['end'])
                duration = int((end_time - start_time).total_seconds())
                
                risk_score = min(75.0 + session['count'] * 2 + duration / 10, 100)
                
                detected.append({
                    'timestamp': session['start'],
                    'type': 'SYSTEM_CRASH',
                    'station_id': station,
                    'duration_seconds': duration,
                    'crash_count': session['count'],
                    'system_source': source,
                    'risk_score': round(risk_score, 1),
                    'severity': self._classify_severity(risk_score)
                })
        
        return detected
    
    # @algorithm Staffing Optimization | Analyzes queue and wait time patterns to recommend optimal staffing levels
    def detect_staffing_needs(self, queue_events: List[Dict], queue_threshold: int,
                            wait_threshold: float) -> List[Dict]:
        """
        Staffing Optimization Algorithm
        Method: Multi-factor heuristic analysis
        """
        detected = []
        
        for queue in queue_events:
            customer_count = queue['data']['customer_count']
            wait_time = queue['data']['average_dwell_time']
            
            needs_staff = False
            if customer_count > queue_threshold and wait_time > wait_threshold:
                needs_staff = True
            elif customer_count > queue_threshold * 1.5:
                needs_staff = True
            
            if needs_staff:
                risk_score = self._calculate_risk_score(55.0, {
                    'queue_factor': max(customer_count - queue_threshold, 0) * 4,
                    'wait_factor': min((wait_time - wait_threshold) / 60 * 5, 20) if wait_time > wait_threshold else 0
                })
                
                detected.append({
                    'timestamp': queue['timestamp'],
                    'type': 'STAFFING_NEEDS',
                    'station_id': queue['station_id'],
                    'Staff_type': 'Cashier',
                    'reason': f"Queue: {customer_count}, Wait: {int(wait_time)}s",
                    'risk_score': round(risk_score, 1),
                    'severity': self._classify_severity(risk_score)
                })
        
        return detected
    
    # @algorithm Station Activation Recommendation | Determines when to activate additional checkout stations based on traffic
    def recommend_station_activation(self, queue_events: List[Dict], 
                                     target_ratio: float = 6.0) -> List[Dict]:
        """
        Station Activation Recommendation Algorithm
        Method: Traffic-based station activation planning
        """
        detected = []
        
        # Aggregate queue data by timestamp
        time_aggregates = defaultdict(lambda: {'total_customers': 0, 'active_stations': set()})
        
        for queue in queue_events:
            timestamp = queue['timestamp']
            station = queue['station_id']
            customers = queue['data']['customer_count']
            
            time_aggregates[timestamp]['total_customers'] += customers
            if customers > 0:
                time_aggregates[timestamp]['active_stations'].add(station)
        
        # Analyze each time point
        for timestamp, data in time_aggregates.items():
            total_customers = data['total_customers']
            active_count = len(data['active_stations'])
            
            if active_count > 0:
                ratio = total_customers / active_count
                
                # Recommend activation if ratio exceeds target
                if ratio > target_ratio:
                    detected.append({
                        'timestamp': timestamp,
                        'type': 'CHECKOUT_ACTION',
                        'Action': 'Open',
                        'reason': f'Customer ratio {ratio:.1f} exceeds target {target_ratio}',
                        'current_stations': active_count,
                        'total_customers': total_customers,
                        'risk_score': min(50 + (ratio - target_ratio) * 5, 90),
                        'severity': 'MEDIUM'
                    })
        
        return detected


class InventoryAlgorithms:
    """Algorithms for inventory management"""
    
    def __init__(self, thresholds: Dict[str, Any]):
        self.thresholds = thresholds
    
    def _classify_severity(self, score: float) -> str:
        if score >= 80:
            return 'CRITICAL'
        elif score >= 60:
            return 'HIGH'
        elif score >= 40:
            return 'MEDIUM'
        return 'LOW'
    
    # @algorithm Inventory Reconciliation | Compares expected vs actual inventory using snapshot data and transaction logs
    def detect_inventory_discrepancies(self, inventory_snapshot: Dict, rfid_events: List[Dict],
                                      pos_events: List[Dict], threshold_percent: float) -> List[Dict]:
        """
        Inventory Reconciliation Algorithm
        Method: Snapshot-based reconciliation with transaction history
        """
        detected = []
        
        # Start with initial inventory
        expected_inventory = inventory_snapshot.copy()
        
        # Subtract POS transactions
        for pos in pos_events:
            sku = pos['data']['sku']
            if sku in expected_inventory:
                expected_inventory[sku] -= 1
        
        # Count RFID detected items
        rfid_inventory = defaultdict(int)
        for rfid in rfid_events:
            sku = rfid['data'].get('sku')
            location = rfid['data'].get('location')
            if sku and location in ['IN_SCAN_AREA', 'SHELF']:
                rfid_inventory[sku] += 1
        
        # Compare and detect discrepancies
        for sku, expected_count in expected_inventory.items():
            actual_count = rfid_inventory.get(sku, 0)
            
            if expected_count > 0:
                diff_percent = abs(actual_count - expected_count) / expected_count * 100
                
                if diff_percent > threshold_percent:
                    risk_score = min(50 + diff_percent * 1.1, 95)
                    
                    # Use latest timestamp
                    timestamp = rfid_events[-1]['timestamp'] if rfid_events else datetime.now().isoformat()
                    
                    detected.append({
                        'timestamp': timestamp,
                        'type': 'INVENTORY_DISCREPANCY',
                        'SKU': sku,
                        'Expected_Inventory': expected_count,
                        'Actual_Inventory': actual_count,
                        'Difference': actual_count - expected_count,
                        'Difference_Percent': round(diff_percent, 2),
                        'risk_score': round(risk_score, 1),
                        'severity': self._classify_severity(risk_score)
                    })
        
        return detected
    
    # @algorithm Multi-Source Validation | Validates transactions where all systems (RFID, POS, Camera) agree for baseline metrics
    def track_successful_operations(self, pos_events: List[Dict], rfid_events: List[Dict],
                                   recognition_events: List[Dict]) -> List[Dict]:
        """
        Multi-Source Validation Algorithm
        Method: Three-way data correlation for transaction validation
        """
        successful = []
        
        # Index RFID and recognition by timestamp/station
        rfid_index = {}
        for rfid in rfid_events:
            if rfid['data'].get('sku'):
                key = (rfid['timestamp'], rfid['station_id'])
                rfid_index[key] = rfid['data']['sku']
        
        recognition_index = {}
        for recog in recognition_events:
            key = (recog['timestamp'], recog['station_id'])
            recognition_index[key] = recog['data']['predicted_product']
        
        # Check POS transactions
        for pos in pos_events:
            key = (pos['timestamp'], pos['station_id'])
            pos_sku = pos['data']['sku']
            
            rfid_sku = rfid_index.get(key)
            recog_sku = recognition_index.get(key)
            
            # All systems agree
            if rfid_sku == recog_sku == pos_sku:
                successful.append({
                    'timestamp': pos['timestamp'],
                    'type': 'SUCCESS',
                    'station_id': pos['station_id'],
                    'customer_id': pos['data']['customer_id'],
                    'product_sku': pos_sku,
                    'service_score': 95,
                    'risk_score': 5.0,
                    'severity': 'LOW'
                })
        
        return successful
