"""
Real-time streaming client for Project Sentinel
Connects to the streaming server and processes events in real-time
"""
import socket
import json
from typing import Callable, Optional
from threading import Thread
import time


class StreamingClient:
    """Client for connecting to the event stream server"""
    
    def __init__(self, host: str = "127.0.0.1", port: int = 8765):
        self.host = host
        self.port = port
        self.socket = None
        self.running = False
        self.event_handlers = []
        
    def connect(self):
        """Connect to the streaming server"""
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.connect((self.host, self.port))
        print(f"Connected to stream server at {self.host}:{self.port}")
        
        # Read banner
        banner_line = self.socket.recv(4096).decode('utf-8')
        banner = json.loads(banner_line)
        print(f"\nStream Info:")
        print(f"  Service: {banner.get('service')}")
        print(f"  Datasets: {', '.join(banner.get('datasets', []))}")
        print(f"  Total Events: {banner.get('total_events')}")
        print(f"  Looping: {banner.get('looping')}")
        print(f"  Speed Factor: {banner.get('speed_factor')}x")
        print()
        
    def add_event_handler(self, handler: Callable):
        """Add a callback function to handle incoming events"""
        self.event_handlers.append(handler)
        
    def start_streaming(self, limit: Optional[int] = None):
        """Start receiving events from the stream"""
        self.running = True
        event_count = 0
        buffer = ""
        
        try:
            while self.running:
                # Receive data
                chunk = self.socket.recv(4096).decode('utf-8')
                if not chunk:
                    break
                
                buffer += chunk
                
                # Process complete lines
                while '\n' in buffer:
                    line, buffer = buffer.split('\n', 1)
                    if line.strip():
                        try:
                            event = json.loads(line)
                            event_count += 1
                            
                            # Call all registered handlers
                            for handler in self.event_handlers:
                                handler(event)
                            
                            # Check limit
                            if limit and event_count >= limit:
                                self.running = False
                                break
                                
                        except json.JSONDecodeError:
                            print(f"Failed to parse event: {line[:100]}")
                            
        except KeyboardInterrupt:
            print("\nStopped by user")
        finally:
            self.close()
            
        print(f"\nProcessed {event_count} events")
        
    def close(self):
        """Close the connection"""
        self.running = False
        if self.socket:
            self.socket.close()
            print("Connection closed")


class EventBuffer:
    """Buffer for accumulating events by type"""
    
    def __init__(self):
        self.pos_events = []
        self.rfid_events = []
        self.product_recognition = []
        self.queue_monitoring = []
        self.inventory_snapshots = []
        
    def add_event(self, event: dict):
        """Add event to appropriate buffer based on dataset"""
        dataset = event.get('dataset', '')
        payload = event.get('payload', {})
        
        # Add metadata from envelope
        payload['timestamp'] = event.get('timestamp')
        
        if 'POS_Transactions' in dataset:
            self.pos_events.append(payload)
        elif 'RFID_data' in dataset:
            self.rfid_events.append(payload)
        elif 'Product_recognism' in dataset:
            self.product_recognition.append(payload)
        elif 'Queue_monitor' in dataset:
            self.queue_monitoring.append(payload)
        elif 'Current_inventory_data' in dataset:
            self.inventory_snapshots.append(payload)
            
    def get_all_buffers(self):
        """Return all buffered events"""
        return {
            'pos_events': self.pos_events,
            'rfid_events': self.rfid_events,
            'product_recognition': self.product_recognition,
            'queue_monitoring': self.queue_monitoring,
            'inventory_snapshots': self.inventory_snapshots
        }
        
    def clear(self):
        """Clear all buffers"""
        self.pos_events.clear()
        self.rfid_events.clear()
        self.product_recognition.clear()
        self.queue_monitoring.clear()
        self.inventory_snapshots.clear()
