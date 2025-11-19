"""
Quick Visualization Script - Generate charts and statistics
"""
import json
from pathlib import Path
from collections import Counter
import sys


def analyze_events(events_file):
    """Analyze events and print statistics"""
    events = []
    
    with open(events_file, 'r') as f:
        for line in f:
            if line.strip():
                events.append(json.loads(line))
    
    print("\n" + "="*70)
    print("EVENT ANALYSIS REPORT")
    print("="*70)
    
    print(f"\nTotal Events: {len(events)}")
    
    # Count by event type
    event_types = Counter()
    stations = Counter()
    timestamps = []
    
    for event in events:
        event_name = event.get('event_data', {}).get('event_name', 'Unknown')
        event_types[event_name] += 1
        
        station = event.get('event_data', {}).get('station_id')
        if station:
            stations[station] += 1
            
        timestamps.append(event.get('timestamp'))
    
    print("\n📊 Event Distribution:")
    for event_type, count in event_types.most_common():
        percentage = (count / len(events)) * 100
        bar = "█" * int(percentage / 2)
        print(f"  {event_type:.<40} {count:>4} ({percentage:>5.1f}%) {bar}")
    
    if stations:
        print("\n🏪 Station Distribution:")
        for station, count in stations.most_common():
            percentage = (count / len(events)) * 100
            print(f"  {station}: {count} events ({percentage:.1f}%)")
    
    # Time analysis
    if timestamps:
        timestamps.sort()
        print(f"\n⏰ Time Range:")
        print(f"  First Event: {timestamps[0]}")
        print(f"  Last Event: {timestamps[-1]}")
    
    # Category analysis
    fraud_types = ['Scanner Avoidance', 'Barcode Switching', 'Weight Discrepancies']
    operational_types = ['Long Queue Length', 'Long Wait Time', 'Unexpected Systems Crash', 'Staffing Needs']
    inventory_types = ['Inventory Discrepancy']
    
    fraud_count = sum(event_types[t] for t in fraud_types)
    operational_count = sum(event_types[t] for t in operational_types)
    inventory_count = sum(event_types[t] for t in inventory_types)
    success_count = event_types.get('Succes Operation', 0)
    
    print("\n🎯 Category Summary:")
    print(f"  🚨 Fraud & Theft Events:     {fraud_count:>4}")
    print(f"  ⚙️  Operational Issues:       {operational_count:>4}")
    print(f"  📦 Inventory Discrepancies:  {inventory_count:>4}")
    print(f"  ✅ Successful Operations:    {success_count:>4}")
    
    print("\n" + "="*70)
    
    return {
        'total': len(events),
        'fraud': fraud_count,
        'operational': operational_count,
        'inventory': inventory_count,
        'success': success_count,
        'by_type': dict(event_types),
        'by_station': dict(stations)
    }


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python visualize.py <path-to-events.jsonl>")
        sys.exit(1)
    
    events_file = Path(sys.argv[1])
    
    if not events_file.exists():
        print(f"Error: File not found: {events_file}")
        sys.exit(1)
    
    stats = analyze_events(events_file)
    
    # Save stats
    stats_file = events_file.parent / "statistics.json"
    with open(stats_file, 'w') as f:
        json.dump(stats, f, indent=2)
    
    print(f"\n💾 Statistics saved to: {stats_file}")
