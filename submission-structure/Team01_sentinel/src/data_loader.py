"""
Data loading and preprocessing module for Project Sentinel
"""
import json
import csv
from datetime import datetime
from typing import Dict, List, Any
from pathlib import Path


class DataLoader:
    """Loads and preprocesses data from various sources"""
    
    def __init__(self, data_dir: str):
        self.data_dir = Path(data_dir)
        self.products = {}
        self.customers = {}
        
    def load_products_catalog(self, filename: str = "products_list.csv") -> Dict[str, Dict]:
        """Load product catalog from CSV"""
        products = {}
        filepath = self.data_dir / filename
        
        with open(filepath, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                sku = row['SKU']
                products[sku] = {
                    'product_name': row['product_name'],
                    'barcode': row['barcode'],
                    'weight': float(row['weight']),
                    'price': float(row['price']),
                    'epc_range': row['EPC_range']
                }
        
        self.products = products
        return products
    
    def load_customer_data(self, filename: str = "customer_data.csv") -> Dict[str, Dict]:
        """Load customer data from CSV"""
        customers = {}
        filepath = self.data_dir / filename
        
        with open(filepath, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                customer_id = row['Customer_ID']
                customers[customer_id] = {
                    'name': row['Name'],
                    'age': row['Age'],
                    'address': row['Address'],
                    'phone': row['TP']
                }
        
        self.customers = customers
        return customers
    
    def load_jsonl_file(self, filename: str) -> List[Dict[str, Any]]:
        """Load JSONL file and return list of events"""
        events = []
        filepath = self.data_dir / filename
        
        with open(filepath, 'r', encoding='utf-8') as f:
            for line in f:
                if line.strip():
                    events.append(json.loads(line))
        
        return events
    
    def parse_timestamp(self, timestamp_str: str) -> datetime:
        """Parse ISO format timestamp"""
        return datetime.fromisoformat(timestamp_str)
    
    def get_product_by_sku(self, sku: str) -> Dict[str, Any]:
        """Get product information by SKU"""
        return self.products.get(sku, {})
    
    def get_customer_by_id(self, customer_id: str) -> Dict[str, Any]:
        """Get customer information by ID"""
        return self.customers.get(customer_id, {})
