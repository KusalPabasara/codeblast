"""
Sentinel - Self-Checkout Fraud Detection System
Main entry point for processing and analysis
"""
import sys
import argparse
import json
from pathlib import Path

from event_engine import EventDetectionEngine
from dashboard import start_dashboard


def main():
    """Main entry point with CLI interface"""
    parser = argparse.ArgumentParser(
        description='Sentinel - Self-Checkout Fraud Detection System',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Process data and generate events
  python main.py --data-dir ../data/input --output ../data/output/events.jsonl
  
  # Process with summary
  python main.py --data-dir ../data/input --output events.jsonl --summary
  
  # Start dashboard after processing
  python main.py --data-dir ../data/input --output events.jsonl --dashboard
  
  # Just start dashboard with existing events
  python main.py --dashboard-only --events events.jsonl
        """
    )
    
    parser.add_argument('--data-dir', type=str,
                       help='Path to data directory containing input files')
    parser.add_argument('--output', type=str,
                       help='Path to output events.jsonl file')
    parser.add_argument('--summary', action='store_true',
                       help='Generate and display summary report')
    parser.add_argument('--dashboard', action='store_true',
                       help='Start dashboard after processing')
    parser.add_argument('--dashboard-only', action='store_true',
                       help='Only start dashboard (no processing)')
    parser.add_argument('--events', type=str,
                       help='Events file for dashboard-only mode')
    parser.add_argument('--port', type=int, default=5000,
                       help='Dashboard port (default: 5000)')
    
    args = parser.parse_args()
    
    # Validate arguments
    if args.dashboard_only:
        if not args.events:
            print("❌ Error: --events required for --dashboard-only mode")
            sys.exit(1)
        
        print("\n" + "="*70)
        print("🛡️  SENTINEL - SELF-CHECKOUT FRAUD DETECTION SYSTEM")
        print("="*70)
        print("\n📊 Dashboard Mode")
        
        start_dashboard(args.events, port=args.port)
        return
    
    if not args.data_dir or not args.output:
        parser.print_help()
        sys.exit(1)
    
    # Validate data directory
    data_path = Path(args.data_dir)
    if not data_path.exists():
        print(f"❌ Error: Data directory '{args.data_dir}' not found")
        sys.exit(1)
    
    try:
        print("\n" + "="*70)
        print("🛡️  SENTINEL - SELF-CHECKOUT FRAUD DETECTION SYSTEM")
        print("="*70)
        print("\n📋 Configuration:")
        print(f"   Data Directory: {args.data_dir}")
        print(f"   Output File: {args.output}")
        print(f"   Summary Report: {'Yes' if args.summary else 'No'}")
        print(f"   Dashboard: {'Yes' if args.dashboard else 'No'}")
        
        # Initialize engine
        print("\n⚙️  Initializing detection engine...")
        engine = EventDetectionEngine(args.data_dir)
        
        # Load all data
        engine.load_all_data()
        
        # Process and detect events
        print("\n🔍 Running detection algorithms...")
        detected_events = engine.process_all_events()
        
        # Validate output directory
        output_path = Path(args.output)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Save results
        print("\n💾 Saving results...")
        engine.save_events(args.output)
        
        # Generate summary
        if args.summary or args.dashboard:
            summary = engine.generate_summary()
            
            print("\n" + "="*70)
            print("📊 SUMMARY REPORT")
            print("="*70)
            print(f"\n📈 Total Events Detected: {summary['total_events']}")
            print(f"   • Fraud Events: {summary['fraud_events']}")
            print(f"   • Operational Events: {summary['operational_events']}")
            print(f"   • Inventory Events: {summary['inventory_events']}")
            print(f"   • Successful Operations: {summary['successful_operations']}")
            print(f"   • Average Risk Score: {summary['average_risk_score']}")
            
            print("\n📋 Event Breakdown:")
            for event_type, count in sorted(summary['event_breakdown'].items()):
                print(f"   • {event_type}: {count}")
            
            if summary['top_stations']:
                print("\n🏪 Top Stations by Activity:")
                for station in summary['top_stations']:
                    print(f"   • {station['station_id']}: {station['event_count']} events")
            
            # Save summary to JSON
            summary_path = output_path.parent / "summary.json"
            with open(summary_path, 'w', encoding='utf-8') as f:
                json.dump(summary, f, indent=2)
            print(f"\n✅ Summary saved to {summary_path}")
        
        print("\n" + "="*70)
        print("✅ PROCESSING COMPLETE")
        print("="*70)
        print(f"\n📁 Results saved to: {args.output}")
        
        # Start dashboard if requested
        if args.dashboard:
            print("\n🚀 Starting dashboard...")
            start_dashboard(args.output, port=args.port)
        else:
            print("\n💡 Tip: Use --dashboard to start the web interface")
            print(f"   Or run: python dashboard.py {args.output}")
        
    except KeyboardInterrupt:
        print("\n\n⚠️  Process interrupted by user")
        sys.exit(0)
    except FileNotFoundError as e:
        print(f"\n❌ File Error: {e}")
        print("   Please check that all required data files are present")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Unexpected Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()

