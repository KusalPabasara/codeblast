"""
Detection Algorithms for Project Sentinel - Team Gmora
Enhanced algorithms with improved accuracy and efficiency
Each algorithm is tagged for automated judging
"""
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
from collections import defaultdict, Counter
import statistics
import math


class FraudDetectionAlgorithms:
    """Collection of enhanced fraud detection algorithms with improved accuracy"""

    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.thresholds = config.get('THRESHOLDS', {})
        self.detection_history = defaultdict(list)

    def _classify_severity(self, score: float) -> str:
        """Enhanced severity classification with granular thresholds"""
        if score >= 85:
            return 'HIGH'
        if score >= 60:
            return 'MEDIUM'
        return 'LOW'

    def _calculate_confidence_score(self, evidence_count: int, consistency_score: float) -> float:
        """Calculate confidence based on multiple evidence sources"""
        base_confidence = min(evidence_count * 25, 75)
        return min(base_confidence + (consistency_score * 25), 100)
    
    # @algorithm Scanner Avoidance Detection | Detects items scanned by RFID but not in POS transaction
    def detect_scanner_avoidance(self, rfid_events: List[Dict], pos_events: List[Dict], 
                                 time_window: int = 10,
                                 products_catalog: Optional[Dict[str, Dict[str, Any]]] = None) -> List[Dict]:
        """
        Detects scanner avoidance by comparing RFID readings with POS transactions.
        Items detected by RFID but not scanned at POS indicate potential theft.
        
        Algorithm:
        1. Group RFID events by customer session (time-based clustering)
        2. Match with POS transactions within time window
        3. Flag RFID items not found in POS as scanner avoidance
        """
        detected_events = []
        
        # Create time-indexed POS transactions
        pos_by_time = defaultdict(list)
        for pos in pos_events:
            timestamp = datetime.fromisoformat(pos['timestamp'])
            pos_by_time[timestamp].append(pos)
        
        # Check each RFID event - only process events with actual SKU data
        for rfid in rfid_events:
            rfid_sku = rfid['data'].get('sku')
            rfid_location = rfid['data'].get('location')

            # Skip if no SKU or not in scan area
            if not rfid_sku or rfid_location != 'IN_SCAN_AREA':
                continue

            rfid_time = datetime.fromisoformat(rfid['timestamp'])
            station = rfid['station_id']

            # Look for matching POS transaction within time window
            found_in_pos = False
            for offset in range(-time_window, time_window + 1):
                check_time = rfid_time + timedelta(seconds=offset)
                if check_time in pos_by_time:
                    for pos in pos_by_time[check_time]:
                        if (pos['data']['sku'] == rfid_sku and
                            pos['station_id'] == station):
                            found_in_pos = True
                            break
                if found_in_pos:
                    break

            if not found_in_pos:
                product_info = (products_catalog or {}).get(rfid_sku, {})
                estimated_loss = product_info.get('price')

                # Enhanced risk scoring with multiple factors
                base_risk = 75.0
                price_factor = min(estimated_loss / 30.0, 20) if estimated_loss else 0
                time_factor = 5.0  # In scan area but not scanned
                risk_score = min(base_risk + price_factor + time_factor, 100)

                severity = self._classify_severity(risk_score)
                confidence = self._calculate_confidence_score(1, 0.8)

                event = {
                    'timestamp': rfid['timestamp'],
                    'type': 'SCANNER_AVOIDANCE',
                    'station_id': station,
                    'product_sku': rfid_sku,
                    'risk_score': round(risk_score, 1),
                    'severity': severity,
                    'confidence': round(confidence, 1),
                    'evidence': rfid
                }
                if estimated_loss:
                    event['estimated_loss'] = round(estimated_loss, 2)
                detected_events.append(event)
        
        return detected_events
    
    # @algorithm Barcode Switching Detection | Identifies mismatches between visual recognition and scanned barcode
    def detect_barcode_switching(self, product_recognition: List[Dict], pos_events: List[Dict],
                                confidence_threshold: float = 0.60,
                                products_catalog: Optional[Dict[str, Dict[str, Any]]] = None) -> List[Dict]:
        """
        Detects barcode switching by comparing product recognition with POS scans.
        High-confidence vision system predictions that don't match scanned items indicate fraud.

        Algorithm:
        1. Filter product recognition events by confidence threshold (0.60 minimum)
        2. Match with POS transactions by timestamp and station
        3. Flag mismatches as barcode switching
        """
        detected_events = []

        # Index POS events by timestamp and station
        pos_index = {}
        for pos in pos_events:
            key = (pos['timestamp'], pos['station_id'])
            pos_index[key] = pos

        for recognition in product_recognition:
            confidence = recognition['data']['accuracy']

            # Consider predictions with confidence >= 0.60
            if confidence >= confidence_threshold:
                predicted_sku = recognition['data']['predicted_product']
                timestamp = recognition['timestamp']
                station = recognition['station_id']
                
                # Check for matching POS transaction
                key = (timestamp, station)
                if key in pos_index:
                    pos = pos_index[key]
                    scanned_sku = pos['data']['sku']
                    
                    # If predicted product doesn't match scanned product
                    if predicted_sku != scanned_sku:
                        products = products_catalog or {}
                        predicted_price = products.get(predicted_sku, {}).get('price')
                        scanned_price = products.get(scanned_sku, {}).get('price')
                        price_gap = 0.0
                        if predicted_price is not None and scanned_price is not None:
                            price_gap = max(predicted_price - scanned_price, 0.0)

                        # Enhanced risk scoring with confidence weighting
                        base_risk = 70.0
                        confidence_boost = (confidence - confidence_threshold) * 30.0
                        price_gap_factor = min(price_gap / 5.0, 25.0) if price_gap > 0 else 0
                        risk_score = min(base_risk + confidence_boost + price_gap_factor, 100.0)

                        severity = self._classify_severity(risk_score)
                        detection_confidence = self._calculate_confidence_score(2, confidence)

                        event = {
                            'timestamp': timestamp,
                            'type': 'BARCODE_SWITCHING',
                            'station_id': station,
                            'customer_id': pos['data']['customer_id'],
                            'actual_sku': predicted_sku,
                            'scanned_sku': scanned_sku,
                            'confidence': confidence,
                            'risk_score': round(risk_score, 1),
                            'severity': severity,
                            'detection_confidence': round(detection_confidence, 1),
                            'price_gap': round(price_gap, 2),
                            'evidence': {
                                'recognition': recognition,
                                'pos': pos
                            }
                        }
                        if predicted_price is not None:
                            event['predicted_price'] = round(predicted_price, 2)
                        if scanned_price is not None:
                            event['scanned_price'] = round(scanned_price, 2)
                        detected_events.append(event)
        
        return detected_events
    
    # @algorithm Weight Discrepancy Detection | Identifies weight anomalies in self-checkout transactions
    def detect_weight_discrepancies(self, pos_events: List[Dict], products_catalog: Dict,
                                   tolerance_percent: float = 15) -> List[Dict]:
        """
        Detects weight discrepancies by comparing expected product weight with actual weight.
        Significant differences indicate potential fraud (multiple items, wrong item).
        
        Algorithm:
        1. For each POS transaction, lookup expected weight from catalog
        2. Compare with actual scanned weight
        3. Flag if difference exceeds tolerance threshold
        """
        detected_events = []
        
        for pos in pos_events:
            sku = pos['data']['sku']
            actual_weight = pos['data']['weight_g']
            
            if sku in products_catalog:
                expected_weight = products_catalog[sku]['weight']
                
                # Calculate percentage difference with enhanced precision
                weight_diff_percent = abs(actual_weight - expected_weight) / expected_weight * 100

                if weight_diff_percent > tolerance_percent:
                    price = products_catalog[sku].get('price') if sku in products_catalog else None

                    # Enhanced risk calculation with non-linear scaling
                    base_risk = 55.0
                    weight_factor = min(math.log(weight_diff_percent + 1) * 15, 35.0)
                    price_risk = min(price / 40.0, 15.0) if price else 0
                    risk_score = min(base_risk + weight_factor + price_risk, 100.0)

                    severity = self._classify_severity(risk_score)
                    confidence = self._calculate_confidence_score(1, 0.85)

                    event = {
                        'timestamp': pos['timestamp'],
                        'type': 'WEIGHT_DISCREPANCY',
                        'station_id': pos['station_id'],
                        'customer_id': pos['data']['customer_id'],
                        'product_sku': sku,
                        'expected_weight': expected_weight,
                        'actual_weight': actual_weight,
                        'difference_percent': round(weight_diff_percent, 2),
                        'risk_score': round(risk_score, 1),
                        'severity': severity,
                        'confidence': round(confidence, 1),
                        'evidence': pos
                    }
                    if price:
                        event['estimated_loss'] = round(price, 2)
                    detected_events.append(event)
        
        return detected_events

    def detect_high_risk_customers(self, fraud_events: List[Dict[str, Any]],
                                   min_events: int = 2,
                                   min_score: float = 80.0) -> List[Dict[str, Any]]:
        """Aggregate fraud events to identify high-risk customers"""
        customer_events: Dict[str, List[Dict[str, Any]]] = defaultdict(list)
        for event in fraud_events:
            customer_id = event.get('customer_id')
            if not customer_id:
                continue
            customer_events[customer_id].append(event)
        detected_events: List[Dict[str, Any]] = []
        for customer_id, events in customer_events.items():
            qualified_events = [e for e in events if e.get('risk_score', 0) >= (min_score - 10)]
            if len(qualified_events) < min_events:
                continue
            avg_score = sum(e.get('risk_score', 0) for e in qualified_events) / len(qualified_events)
            compounded_score = min(avg_score + (len(qualified_events) - min_events + 1) * 5, 100)
            severity = self._classify_severity(compounded_score)
            station_ids = [e.get('station_id') for e in qualified_events if e.get('station_id')]
            station_counts = Counter(station_ids)
            primary_station: Optional[str] = station_counts.most_common(1)[0][0] if station_counts else None
            stations_involved = [station for station, _ in station_counts.most_common()]
            station_summary = [
                {'station_id': station, 'event_count': count}
                for station, count in station_counts.most_common()
            ]
            recent = [
                {
                    'type': e['type'],
                    'timestamp': e['timestamp'],
                    'risk_score': e.get('risk_score'),
                    'station_id': e.get('station_id')
                }
                for e in qualified_events[-3:]
            ]
            detected_events.append({
                'timestamp': qualified_events[-1]['timestamp'],
                'type': 'HIGH_RISK_CUSTOMER',
                'customer_id': customer_id,
                'risk_score': round(compounded_score, 1),
                'severity': severity,
                'fraud_event_count': len(events),
                'recent_events': recent,
                'station_id': primary_station,
                'stations_involved': stations_involved,
                'station_summary': station_summary
            })
        return detected_events


class OperationalAlgorithms:
    """Algorithms for operational efficiency and customer experience"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.thresholds = config.get('THRESHOLDS', {})

    def _classify_severity(self, score: float) -> str:
        if score >= 80:
            return 'HIGH'
        if score >= 55:
            return 'MEDIUM'
        return 'LOW'
    
    # @algorithm Queue Length Monitoring | Detects excessive queue lengths requiring intervention
    def detect_long_queue(self, queue_events: List[Dict], 
                         threshold: int = 5) -> List[Dict]:
        """
        Detects long queues that require additional staff or checkout stations.
        
        Algorithm:
        1. Monitor customer_count in queue monitoring data
        2. Flag when count exceeds threshold
        3. Trigger staffing alerts
        """
        detected_events = []
        
        for queue in queue_events:
            customer_count = queue['data']['customer_count']
            
            if customer_count > threshold:
                risk_score = min(48 + max(customer_count - threshold, 0) * 8, 92)
                severity = self._classify_severity(risk_score)
                detected_events.append({
                    'timestamp': queue['timestamp'],
                    'type': 'LONG_QUEUE',
                    'station_id': queue['station_id'],
                    'num_of_customers': customer_count,
                    'risk_score': round(risk_score, 1),
                    'severity': severity,
                    'evidence': queue
                })
        
        return detected_events
    
    # @algorithm Wait Time Analysis | Identifies excessive customer wait times
    def detect_long_wait_time(self, queue_events: List[Dict],
                            threshold_seconds: float = 60) -> List[Dict]:
        """
        Detects excessive wait times that harm customer experience.

        Algorithm:
        1. Monitor average_dwell_time in queue data
        2. Flag when dwell time exceeds threshold (60 seconds)
        3. Generate customer experience alerts
        """
        detected_events = []

        for queue in queue_events:
            dwell_time = queue['data']['average_dwell_time']
            customer_count = queue['data'].get('customer_count', 0)

            if dwell_time > threshold_seconds:
                overage = dwell_time - threshold_seconds
                # Risk increases with both wait time and customer count
                time_risk = min((overage / 60) * 15, 35)
                customer_risk = min(customer_count * 3, 15)
                risk_score = min(45 + time_risk + customer_risk, 90)
                severity = self._classify_severity(risk_score)
                detected_events.append({
                    'timestamp': queue['timestamp'],
                    'type': 'LONG_WAIT',
                    'station_id': queue['station_id'],
                    'wait_time_seconds': round(dwell_time, 1),
                    'customer_count': customer_count,
                    'risk_score': round(risk_score, 1),
                    'severity': severity,
                    'evidence': queue
                })

        return detected_events
    
    # @algorithm System Health Monitoring | Detects system crashes and downtime
    def detect_system_crashes(self, pos_events: List[Dict] = None,
                             product_recognition: List[Dict] = None,
                             rfid_events: List[Dict] = None,
                             queue_events: List[Dict] = None) -> List[Dict]:
        """
        Detects system crashes by checking status field in data streams.

        Algorithm:
        1. Check all event streams for status="System Crash" or "Read Error"
        2. Flag each crash event with appropriate severity
        3. Group consecutive crashes to identify crash duration
        """
        detected_events = []

        # Combine all event sources
        all_sources = []
        if pos_events:
            all_sources.extend([(e, 'POS') for e in pos_events if e.get('status') in ['System Crash', 'Read Error']])
        if product_recognition:
            all_sources.extend([(e, 'Product Recognition') for e in product_recognition if e.get('status') in ['System Crash', 'Read Error']])
        if rfid_events:
            all_sources.extend([(e, 'RFID') for e in rfid_events if e.get('status') in ['System Crash', 'Read Error']])
        if queue_events:
            all_sources.extend([(e, 'Queue Monitor') for e in queue_events if e.get('status') in ['System Crash', 'Read Error']])

        # Sort by timestamp
        all_sources.sort(key=lambda x: x[0]['timestamp'])

        # Track crash sessions
        crash_sessions = defaultdict(lambda: {'start': None, 'end': None, 'count': 0, 'source': None})

        for event, source in all_sources:
            station_id = event.get('station_id')
            timestamp = event['timestamp']
            status = event.get('status', 'Unknown')

            key = (station_id, source)

            # Start or extend crash session
            if crash_sessions[key]['start'] is None:
                crash_sessions[key] = {
                    'start': timestamp,
                    'end': timestamp,
                    'count': 1,
                    'source': source,
                    'status': status
                }
            else:
                crash_sessions[key]['end'] = timestamp
                crash_sessions[key]['count'] += 1

        # Generate events for each crash session
        for (station_id, source), session_data in crash_sessions.items():
            if session_data['count'] > 0:
                # Calculate duration if multiple crash events
                start_time = datetime.fromisoformat(session_data['start'])
                end_time = datetime.fromisoformat(session_data['end'])
                duration = (end_time - start_time).total_seconds()

                # Risk score based on crash count and duration
                base_risk = 75.0
                count_factor = min(session_data['count'] * 2, 20)
                duration_factor = min(duration / 10, 5)
                risk_score = min(base_risk + count_factor + duration_factor, 100)

                severity = self._classify_severity(risk_score)

                detected_events.append({
                    'timestamp': session_data['start'],
                    'type': 'SYSTEM_CRASH',
                    'station_id': station_id,
                    'system_source': session_data['source'],
                    'crash_count': session_data['count'],
                    'duration_seconds': int(duration),
                    'status': session_data['status'],
                    'risk_score': round(risk_score, 1),
                    'severity': severity
                })

        return detected_events
    
    # @algorithm Staffing Optimization | Recommends staffing needs based on queue metrics
    def recommend_staffing(self, queue_events: List[Dict],
                          customer_threshold: int = 5,
                          wait_threshold: float = 300) -> List[Dict]:
        """
        Recommends staffing needs based on queue length and wait times.
        
        Algorithm:
        1. Analyze queue metrics (length and wait time)
        2. Apply heuristics to determine staffing needs
        3. Generate staffing recommendations
        """
        detected_events = []
        
        for queue in queue_events:
            customer_count = queue['data']['customer_count']
            dwell_time = queue['data']['average_dwell_time']
            
            needs_staff = False
            staff_type = "Cashier"
            
            if customer_count > customer_threshold and dwell_time > wait_threshold:
                needs_staff = True
                staff_type = "Cashier"
            elif customer_count > customer_threshold * 1.5:
                needs_staff = True
                staff_type = "Cashier"
            
            if needs_staff:
                risk_score = 58.0
                risk_score += max(customer_count - customer_threshold, 0) * 4
                if dwell_time > wait_threshold:
                    risk_score += min((dwell_time - wait_threshold) / 60 * 5, 20)
                risk_score = min(risk_score, 96)
                severity = self._classify_severity(risk_score)
                detected_events.append({
                    'timestamp': queue['timestamp'],
                    'type': 'STAFFING_NEEDS',
                    'station_id': queue['station_id'],
                    'staff_type': staff_type,
                    'reason': f"Queue: {customer_count}, Wait: {dwell_time}s",
                    'risk_score': round(risk_score, 1),
                    'severity': severity,
                    'evidence': queue
                })

        return detected_events

    def detect_station_pressure(self, queue_events: List[Dict[str, Any]],
                                queue_threshold: int,
                                wait_threshold: float,
                                occurrences_threshold: int,
                                window_minutes: int) -> List[Dict[str, Any]]:
        """Aggregate queue signals to highlight struggling stations"""
        station_events: Dict[str, List[Dict[str, Any]]] = defaultdict(list)
        for event in queue_events:
            station_events[event['station_id']].append(event)

        detected_events: List[Dict[str, Any]] = []
        for station_id, events in station_events.items():
            if not events:
                continue
            events_sorted = sorted(events, key=lambda e: e['timestamp'])
            pressure_samples = [
                e for e in events_sorted
                if e['data']['customer_count'] > queue_threshold or
                e['data']['average_dwell_time'] > wait_threshold
            ]
            if window_minutes:
                try:
                    reference_time = datetime.fromisoformat(events_sorted[-1]['timestamp'])
                except ValueError:
                    reference_time = None
                if reference_time:
                    window_delta = timedelta(minutes=window_minutes)
                    filtered_samples = []
                    for sample in pressure_samples:
                        try:
                            sample_time = datetime.fromisoformat(sample['timestamp'])
                        except ValueError:
                            continue
                        if reference_time - sample_time <= window_delta:
                            filtered_samples.append(sample)
                    pressure_samples = filtered_samples
            if len(pressure_samples) < occurrences_threshold:
                continue

            max_queue = max(e['data']['customer_count'] for e in pressure_samples)
            max_wait = max(e['data']['average_dwell_time'] for e in pressure_samples)
            avg_queue = statistics.mean(e['data']['customer_count'] for e in pressure_samples)
            avg_wait = statistics.mean(e['data']['average_dwell_time'] for e in pressure_samples)
            risk_score = min(60 + (max_queue - queue_threshold) * 7 + max(0, (max_wait - wait_threshold) / 60 * 6), 100)
            severity = self._classify_severity(risk_score)
            recent_samples = [
                {
                    'timestamp': sample['timestamp'],
                    'queue': sample['data']['customer_count'],
                    'wait_seconds': sample['data']['average_dwell_time']
                }
                for sample in pressure_samples[-3:]
            ]

            detected_events.append({
                'timestamp': pressure_samples[-1]['timestamp'],
                'type': 'STATION_PERFORMANCE_ALERT',
                'station_id': station_id,
                'issues_detected': len(pressure_samples),
                'max_queue': max_queue,
                'max_wait_seconds': max_wait,
                'average_queue': round(avg_queue, 1),
                'average_wait_seconds': round(avg_wait, 1),
                'risk_score': round(risk_score, 1),
                'severity': severity,
                'recent_samples': recent_samples,
                'window_minutes': window_minutes
            })
        
        return detected_events


class InventoryAlgorithms:
    """Algorithms for inventory management and shrinkage detection"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.thresholds = config.get('THRESHOLDS', {})

    def _classify_severity(self, score: float) -> str:
        if score >= 80:
            return 'HIGH'
        if score >= 55:
            return 'MEDIUM'
        return 'LOW'
    
    # @algorithm Inventory Discrepancy Detection | Identifies inventory shrinkage and misplacement
    def detect_inventory_discrepancies(self, inventory_snapshot: Dict,
                                      rfid_events: List[Dict],
                                      pos_events: List[Dict],
                                      threshold_percent: float = 10) -> List[Dict]:
        """
        Detects inventory discrepancies by reconciling snapshot with RFID and POS data.
        
        Algorithm:
        1. Start with initial inventory snapshot
        2. Apply POS transactions (subtract sold items)
        3. Compare with RFID-detected inventory
        4. Flag significant discrepancies as shrinkage
        """
        detected_events = []
        
        # Calculate expected inventory after POS transactions
        expected_inventory = inventory_snapshot.copy()
        
        for pos in pos_events:
            sku = pos['data']['sku']
            if sku in expected_inventory:
                expected_inventory[sku] -= 1
        
        # Count RFID detected items
        rfid_inventory = defaultdict(int)
        for rfid in rfid_events:
            sku = rfid['data']['sku']
            if rfid['data']['location'] in ['IN_SCAN_AREA', 'SHELF']:
                rfid_inventory[sku] += 1
        
        # Compare and detect discrepancies
        for sku, expected_count in expected_inventory.items():
            actual_count = rfid_inventory.get(sku, 0)
            
            if expected_count > 0:
                diff_percent = abs(actual_count - expected_count) / expected_count * 100
                
                if diff_percent > threshold_percent:
                    timestamp = datetime.now().isoformat()
                    risk_score = min(50 + diff_percent * 1.1, 95)
                    severity = self._classify_severity(risk_score)
                    detected_events.append({
                        'timestamp': timestamp,
                        'type': 'INVENTORY_DISCREPANCY',
                        'sku': sku,
                        'expected_inventory': expected_count,
                        'actual_inventory': actual_count,
                        'difference': actual_count - expected_count,
                        'difference_percent': diff_percent,
                        'risk_score': round(risk_score, 1),
                        'severity': severity
                    })
        
        return detected_events
    
    # @algorithm Transaction Success Tracking | Logs successful transactions for baseline analysis
    def track_successful_operations(self, pos_events: List[Dict],
                                   rfid_events: List[Dict],
                                   product_recognition: List[Dict]) -> List[Dict]:
        """
        Tracks successful operations where all systems agree.
        
        Algorithm:
        1. Match POS with RFID readings
        2. Match with product recognition
        3. Log as successful when all systems agree
        """
        successful_events = []
        
        # Index RFID and recognition by timestamp and station
        rfid_index = {}
        for rfid in rfid_events:
            key = (rfid['timestamp'], rfid['station_id'])
            rfid_index[key] = rfid
        
        recognition_index = {}
        for recog in product_recognition:
            key = (recog['timestamp'], recog['station_id'])
            recognition_index[key] = recog
        
        for pos in pos_events:
            key = (pos['timestamp'], pos['station_id'])
            
            # Check if RFID and recognition agree
            has_rfid = key in rfid_index
            has_recognition = key in recognition_index
            
            if has_rfid and has_recognition:
                rfid_sku = rfid_index[key]['data']['sku']
                recog_sku = recognition_index[key]['data']['predicted_product']
                pos_sku = pos['data']['sku']
                
                # All systems agree
                if rfid_sku == recog_sku == pos_sku:
                    successful_events.append({
                        'timestamp': pos['timestamp'],
                        'type': 'SUCCESS',
                        'station_id': pos['station_id'],
                        'customer_id': pos['data']['customer_id'],
                        'product_sku': pos_sku,
                        'service_score': 95,
                        'severity': 'LOW',
                        'risk_score': 5.0
                    })
        
        return successful_events
