"""
Data Loader Module - Loads and merges data from multiple sources
"""
import json
import csv
from pathlib import Path
from typing import Dict, List, Any
from datetime import datetime


class DataLoader:
    """Handles loading and merging data from multiple sources"""
    
    def __init__(self, data_dir: str):
        self.data_dir = Path(data_dir)
        
    def load_jsonl_file(self, filename: str) -> List[Dict[str, Any]]:
        """Load JSONL file and return list of events"""
        file_path = self.data_dir / filename
        events = []
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                for line in f:
                    line = line.strip()
                    if line:
                        events.append(json.loads(line))
        except FileNotFoundError:
            print(f"Warning: {filename} not found")
            return []
        
        return events
    
    def load_csv_file(self, filename: str) -> List[Dict[str, Any]]:
        """Load CSV file and return list of dictionaries"""
        file_path = self.data_dir / filename
        data = []
        
        try:
            # Try utf-8-sig first to handle BOM, then fall back to utf-8
            for encoding in ['utf-8-sig', 'utf-8', 'latin-1']:
                try:
                    with open(file_path, 'r', encoding=encoding) as f:
                        # Skip empty lines at the beginning
                        lines = [line for line in f if line.strip()]
                        if not lines:
                            continue
                        reader = csv.DictReader(lines)
                        data = list(reader)
                        # Verify we got valid data with proper headers
                        if data and any(key and key.strip() for key in data[0].keys()):
                            break
                except (UnicodeDecodeError, csv.Error):
                    continue
        except FileNotFoundError:
            print(f"Warning: {filename} not found")
            return []
        
        return data
    
    def load_products_catalog(self) -> Dict[str, Dict[str, Any]]:
        """Load products catalog indexed by SKU"""
        products_list = self.load_csv_file('products_list.csv')
        catalog = {}
        
        for product in products_list:
            sku = product['SKU']
            catalog[sku] = {
                'product_name': product['product_name'],
                'barcode': product['barcode'],
                'weight': float(product['weight']),
                'price': float(product['price']),
                'quantity': int(product['quantity']),
                'epc_range': product['EPC_range']
            }
        
        return catalog
    
    def load_customer_data(self) -> Dict[str, Dict[str, Any]]:
        """Load customer data indexed by Customer_ID"""
        customers_list = self.load_csv_file('customer_data.csv')
        customers = {}
        
        for customer in customers_list:
            if 'Customer_ID' in customer:
                customers[customer['Customer_ID']] = customer
        
        return customers
    
    def merge_all_events(self) -> List[Dict[str, Any]]:
        """Load all events from different sources and merge them by timestamp"""
        all_events = []
        
        # Load all event sources
        pos_events = self.load_jsonl_file('pos_transactions.jsonl')
        rfid_events = self.load_jsonl_file('rfid_readings.jsonl')
        recognition_events = self.load_jsonl_file('product_recognition.jsonl')
        queue_events = self.load_jsonl_file('queue_monitoring.jsonl')
        inventory_events = self.load_jsonl_file('inventory_snapshots.jsonl')
        
        # Tag events with source type
        for event in pos_events:
            event['_source'] = 'pos'
            all_events.append(event)
        
        for event in rfid_events:
            event['_source'] = 'rfid'
            all_events.append(event)
        
        for event in recognition_events:
            event['_source'] = 'recognition'
            all_events.append(event)
        
        for event in queue_events:
            event['_source'] = 'queue'
            all_events.append(event)
        
        for event in inventory_events:
            event['_source'] = 'inventory'
            all_events.append(event)
        
        # Sort all events by timestamp
        all_events.sort(key=lambda x: x['timestamp'])
        
        return all_events

