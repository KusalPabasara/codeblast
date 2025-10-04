"""
Main Application for Project Sentinel - Team Gmora
Enhanced with comprehensive error handling and logging
"""
import sys
import argparse
from pathlib import Path
import traceback

from event_engine import EventDetectionEngine
from config import THRESHOLDS
import json


def main():
    """Main entry point with enhanced error handling"""
    parser = argparse.ArgumentParser(
        description='Project Sentinel - Advanced Retail Intelligence System - Team Gmora'
    )
    parser.add_argument('--data-dir', type=str, required=True,
                       help='Path to data directory containing input files')
    parser.add_argument('--output', type=str, required=True,
                       help='Path to output events.jsonl file')
    parser.add_argument('--summary', action='store_true',
                       help='Print summary report')

    args = parser.parse_args()

    try:
        print("="*70)
        print("PROJECT SENTINEL - TEAM GMORA".center(70))
        print("="*70)
        print("\nAdvanced Retail Intelligence & Loss Prevention System")
        print("   Multi-Algorithm Event Detection Engine")
        print("   Detecting: Fraud, Theft, Operational Issues, Inventory Problems")
        print()

        # Validate data directory
        data_path = Path(args.data_dir)
        if not data_path.exists():
            print(f"[ERROR] Data directory '{args.data_dir}' not found")
            sys.exit(1)

        # Initialize engine with error handling
        print("[*] Initializing detection engine...")
        engine = EventDetectionEngine(args.data_dir, {'THRESHOLDS': THRESHOLDS})

        # Load all data
        print("\n[*] Loading data sources...")
        engine.load_all_data()

        # Process and detect events
        print("\n[*] Running detection algorithms...")
        detected_events = engine.process_all_events()

        # Validate output directory
        output_path = Path(args.output)
        output_path.parent.mkdir(parents=True, exist_ok=True)

        # Save results
        print("\n[*] Saving results...")
        engine.save_events(args.output)

    except KeyboardInterrupt:
        print("\n\n[WARNING] Process interrupted by user")
        sys.exit(0)
    except FileNotFoundError as e:
        print(f"\n[ERROR] File Error: {e}")
        print("   Please check that all required data files are present")
        sys.exit(1)
    except KeyError as e:
        print(f"\n[ERROR] Data Error: Missing key {e}")
        print("   Please check data file format")
        sys.exit(1)
    except Exception as e:
        print(f"\n[ERROR] Unexpected Error: {e}")
        print("\n[TRACEBACK]:")
        traceback.print_exc()
        sys.exit(1)
    
    # Generate summary
    if args.summary:
        summary = engine.generate_summary_report()
        print("\n" + "="*70)
        print("SUMMARY REPORT")
        print("="*70)
        print(f"\nTotal Events Detected: {summary['total_events']}")
        print(f"  • Fraud Events: {summary['fraud_events']}")
        print(f"  • Operational Events: {summary['operational_events']}")
        print(f"  • Inventory Events: {summary['inventory_events']}")
        print(f"  • Successful Operations: {summary['successful_operations']}")
        print(f"  • Average Risk Score: {summary['average_risk_score']}")
        
        print("\nEvent Breakdown:")
        for event_type, count in sorted(summary['event_breakdown'].items()):
            print(f"  • {event_type}: {count}")
        
        if summary['high_risk_customers']:
            print("\nHigh-Risk Customers:")
            for customer in summary['high_risk_customers'][:5]:
                station_display = customer.get('station_id') or ', '.join(customer.get('stations_involved', []) or []) or 'N/A'
                print(f"  • {customer['customer_id']} | Risk {customer['risk_score']} | Events {customer['fraud_event_count']} | Station {station_display}")
        
        if summary['busiest_stations']:
            print("\nStations with Highest Event Volume:")
            for station in summary['busiest_stations']:
                print(f"  • {station['station_id']}: {station['event_count']} events")
        
        # Save summary to JSON
        summary_path = Path(args.output).parent / "summary.json"
        with open(summary_path, 'w') as f:
            json.dump(summary, f, indent=2)
        print(f"\n✓ Summary saved to {summary_path}")
    
        print("\n" + "="*70)
        print("[SUCCESS] PROCESSING COMPLETE - ALL SYSTEMS OPERATIONAL")
        print("="*70)
        print(f"\n[+] Results saved to: {args.output}")
        if args.summary:
            print(f"[+] Summary saved to: {Path(args.output).parent / 'summary.json'}")
        print("\n[*] Ready for competition submission!")
        print()

if __name__ == "__main__":
    main()
