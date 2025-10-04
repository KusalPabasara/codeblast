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
        """Load product catalog from CSV, then enrich from POS transactions if needed"""
        products = {}
        filepath = self.data_dir / filename

        # Try to load from CSV first
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    sku = row['SKU']
                    products[sku] = {
                        'product_name': row['product_name'],
                        'barcode': row['barcode'],
                        'weight': float(row['weight']),
                        'price': float(row['price']),
                        'epc_range': row.get('EPC_range', '')
                    }
        except Exception as e:
            print(f"   Warning: Could not load products_list.csv completely: {e}")

        # If we have very few products, enrich from POS transactions
        if len(products) < 10:
            print("   Enriching product catalog from POS transactions...")
            pos_filepath = self.data_dir / "pos_transactions.jsonl"
            try:
                with open(pos_filepath, 'r', encoding='utf-8') as f:
                    for line in f:
                        if line.strip():
                            transaction = json.loads(line)
                            if transaction.get('status') == 'Active' and 'data' in transaction:
                                data = transaction['data']
                                sku = data.get('sku')
                                if sku and sku not in products:
                                    products[sku] = {
                                        'product_name': data.get('product_name', 'Unknown'),
                                        'barcode': data.get('barcode', ''),
                                        'weight': float(data.get('weight_g', 0)),
                                        'price': float(data.get('price', 0)),
                                        'epc_range': ''
                                    }
            except Exception as e:
                print(f"   Warning: Could not enrich from POS: {e}")

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
