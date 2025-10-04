"""
Test suite for Project Sentinel algorithms
"""
import unittest
from datetime import datetime
from algorithms import FraudDetectionAlgorithms, OperationalAlgorithms, InventoryAlgorithms
from config import THRESHOLDS


class TestFraudDetection(unittest.TestCase):
    """Test fraud detection algorithms"""
    
    def setUp(self):
        self.detector = FraudDetectionAlgorithms({'THRESHOLDS': THRESHOLDS})
        
    def test_scanner_avoidance_detection(self):
        """Test scanner avoidance detection"""
        rfid_events = [
            {
                'timestamp': '2025-08-13T16:00:04',
                'station_id': 'SCC1',
                'data': {'sku': 'PRD_T_03', 'location': 'IN_SCAN_AREA'}
            }
        ]
        pos_events = []
        
        results = self.detector.detect_scanner_avoidance(rfid_events, pos_events, 10)
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]['type'], 'SCANNER_AVOIDANCE')
        self.assertIn('risk_score', results[0])
        self.assertIn('severity', results[0])
        
    def test_barcode_switching_detection(self):
        """Test barcode switching detection"""
        recognition = [
            {
                'timestamp': '2025-08-13T16:00:02',
                'station_id': 'SCC1',
                'data': {'predicted_product': 'PRD_A_03', 'accuracy': 0.95}
            }
        ]
        pos_events = [
            {
                'timestamp': '2025-08-13T16:00:02',
                'station_id': 'SCC1',
                'data': {'sku': 'PRD_A_01', 'customer_id': 'C001'}
            }
        ]
        
        results = self.detector.detect_barcode_switching(recognition, pos_events, 0.75)
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]['type'], 'BARCODE_SWITCHING')
        self.assertIn('risk_score', results[0])
        
    def test_weight_discrepancy_detection(self):
        """Test weight discrepancy detection"""
        pos_events = [
            {
                'timestamp': '2025-08-13T16:00:01',
                'station_id': 'SCC1',
                'data': {'sku': 'PRD_F_01', 'weight_g': 300, 'customer_id': 'C001'}
            }
        ]
        products = {
            'PRD_F_01': {'weight': 150, 'price': 280}
        }
        
        results = self.detector.detect_weight_discrepancies(pos_events, products, 15)
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]['type'], 'WEIGHT_DISCREPANCY')
        self.assertIn('risk_score', results[0])

    def test_high_risk_customer_detection(self):
        """Ensure aggregated high-risk customers are detected"""
        fraud_events = [
            {
                'timestamp': '2025-08-13T16:05:00',
                'type': 'SCANNER_AVOIDANCE',
                'customer_id': 'C010',
                'risk_score': 86,
                'station_id': 'SCC1'
            },
            {
                'timestamp': '2025-08-13T16:07:00',
                'type': 'BARCODE_SWITCHING',
                'customer_id': 'C010',
                'risk_score': 82,
                'station_id': 'SCC1'
            }
        ]

        results = self.detector.detect_high_risk_customers(fraud_events, min_events=2, min_score=80)
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]['type'], 'HIGH_RISK_CUSTOMER')
        self.assertGreaterEqual(results[0]['risk_score'], 80)
        self.assertEqual(results[0]['customer_id'], 'C010')
        self.assertEqual(results[0].get('station_id'), 'SCC1')
        self.assertIn('SCC1', results[0].get('stations_involved', []))


class TestOperationalAlgorithms(unittest.TestCase):
    """Test operational monitoring algorithms"""
    
    def setUp(self):
        self.detector = OperationalAlgorithms({'THRESHOLDS': THRESHOLDS})
        
    def test_long_queue_detection(self):
        """Test long queue detection"""
        queue_events = [
            {
                'timestamp': '2025-08-13T16:00:03',
                'station_id': 'SCC1',
                'data': {'customer_count': 8, 'average_dwell_time': 200}
            }
        ]
        
        results = self.detector.detect_long_queue(queue_events, 5)
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]['type'], 'LONG_QUEUE')
        self.assertIn('risk_score', results[0])
        
    def test_long_wait_detection(self):
        """Test long wait time detection"""
        queue_events = [
            {
                'timestamp': '2025-08-13T16:00:03',
                'station_id': 'SCC1',
                'data': {'customer_count': 3, 'average_dwell_time': 350}
            }
        ]
        
        results = self.detector.detect_long_wait_time(queue_events, 300)
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]['type'], 'LONG_WAIT')
        self.assertIn('risk_score', results[0])

    def test_station_pressure_detection(self):
        """Station pressure alert is triggered when thresholds are exceeded"""
        queue_events = [
            {
                'timestamp': '2025-08-13T16:00:03',
                'station_id': 'SCC1',
                'data': {'customer_count': 8, 'average_dwell_time': 320}
            },
            {
                'timestamp': '2025-08-13T16:05:03',
                'station_id': 'SCC1',
                'data': {'customer_count': 7, 'average_dwell_time': 360}
            },
            {
                'timestamp': '2025-08-13T16:09:03',
                'station_id': 'SCC1',
                'data': {'customer_count': 6, 'average_dwell_time': 310}
            }
        ]

        results = self.detector.detect_station_pressure(queue_events, 5, 300, 2, 15)
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]['type'], 'STATION_PERFORMANCE_ALERT')
        self.assertIn('risk_score', results[0])


if __name__ == '__main__':
    unittest.main()
