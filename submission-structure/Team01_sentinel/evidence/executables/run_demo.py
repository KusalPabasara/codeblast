#!/usr/bin/env python3
"""
Automation script for Project Sentinel - Demo Runner
This script sets up dependencies, processes data, and generates all outputs
"""
import subprocess
import sys
import os
from pathlib import Path
import shutil


def print_banner():
    """Print startup banner"""
    print("="*70)
    print("PROJECT SENTINEL - AUTOMATED DEMO RUNNER")
    print("="*70)
    print()


def install_dependencies():
    """Install required Python packages"""
    print("📦 Installing dependencies...")
    
    requirements = [
        'flask',
        'flask-cors'
    ]
    
    for package in requirements:
        try:
            subprocess.check_call([sys.executable, '-m', 'pip', 'install', '-q', package])
            print(f"   ✓ Installed {package}")
        except subprocess.CalledProcessError:
            print(f"   ⚠ Failed to install {package}, continuing...")
    
    print()


def run_processing(data_dir, output_dir):
    """Run the event detection engine"""
    print("🔍 Running event detection engine...")
    
    # Get absolute paths
    script_dir = Path(__file__).parent.absolute()
    src_dir = script_dir.parent.parent / 'src'
    
    # Add src to Python path
    sys.path.insert(0, str(src_dir))
    
    # Run main processing
    cmd = [
        sys.executable,
        str(src_dir / 'main.py'),
        '--data-dir', str(data_dir),
        '--output', str(output_dir / 'events.jsonl'),
        '--summary'
    ]
    
    try:
        subprocess.check_call(cmd)
        print("   ✓ Processing complete")
    except subprocess.CalledProcessError as e:
        print(f"   ✗ Processing failed: {e}")
        return False
    
    return True


def copy_results_to_evidence(output_dir, evidence_dir):
    """Copy results to evidence directories"""
    print("\n📋 Copying results to evidence directories...")
    
    events_file = output_dir / 'events.jsonl'
    summary_file = output_dir / 'summary.json'
    
    if events_file.exists():
        # Determine which evidence directory to use (test or final)
        # For demo, we'll copy to both
        for target in ['test', 'final']:
            target_dir = evidence_dir / target
            target_dir.mkdir(parents=True, exist_ok=True)
            
            shutil.copy(events_file, target_dir / 'events.jsonl')
            print(f"   ✓ Copied events.jsonl to {target}/")
            
            if summary_file.exists():
                shutil.copy(summary_file, target_dir / 'summary.json')
                print(f"   ✓ Copied summary.json to {target}/")
    else:
        print("   ⚠ No events.jsonl found to copy")


def start_dashboard(output_dir):
    """Start the dashboard server"""
    print("\n🚀 Starting dashboard server...")
    print("   Dashboard will be available at: http://localhost:5000")
    print("   Press Ctrl+C to stop")
    print()
    
    script_dir = Path(__file__).parent.absolute()
    src_dir = script_dir.parent.parent / 'src'
    
    cmd = [
        sys.executable,
        str(src_dir / 'dashboard.py'),
        '--events-file', str(output_dir / 'events.jsonl'),
        '--port', '5000'
    ]
    
    try:
        subprocess.check_call(cmd)
    except KeyboardInterrupt:
        print("\n\n✓ Dashboard stopped")
    except subprocess.CalledProcessError as e:
        print(f"\n⚠ Dashboard error: {e}")


def main():
    """Main execution flow"""
    print_banner()
    
    # Determine paths
    script_dir = Path(__file__).parent.absolute()
    project_root = script_dir.parent.parent
    
    # Check if custom data directory provided via command line FIRST
    if len(sys.argv) > 1:
        data_dir = Path(sys.argv[1]).resolve()
        print(f"Using custom data directory: {data_dir}\n")
    else:
        # Default data directory (assuming running from evidence/executables/)
        # Look for data in project root or use relative path
        data_dir = Path('../../../../../../data/input').resolve()
        
        # Check if data directory exists, otherwise use alternative paths
        if not data_dir.exists():
            # Try relative to project root
            data_dir = project_root / 'data' / 'input'
            
        if not data_dir.exists():
            # Try to find it in parent directories
            for parent in [script_dir.parent, script_dir.parent.parent, script_dir.parent.parent.parent]:
                potential_data = parent / 'data' / 'input'
                if potential_data.exists():
                    data_dir = potential_data
                    break
    
    # Output directory for results
    output_dir = script_dir / 'results'
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Evidence directory
    evidence_dir = project_root / 'evidence' / 'output'
    
    print(f"📂 Data directory: {data_dir}")
    print(f"📂 Output directory: {output_dir}")
    print(f"📂 Evidence directory: {evidence_dir}")
    print()
    
    # Check if data directory exists
    if not data_dir.exists():
        print(f"❌ Error: Data directory not found at {data_dir}")
        print("\nPlease ensure the data directory exists or provide the path as argument:")
        print(f"   python {Path(__file__).name} <path-to-data-directory>")
        sys.exit(1)
    
    # Step 1: Install dependencies
    install_dependencies()
    
    # Step 2: Run processing
    success = run_processing(data_dir, output_dir)
    
    if not success:
        print("\n❌ Processing failed. Please check errors above.")
        sys.exit(1)
    
    # Step 3: Copy results to evidence
    copy_results_to_evidence(output_dir, evidence_dir)
    
    # Step 4: Start dashboard
    print("\n" + "="*70)
    print("✅ SETUP COMPLETE - ALL OUTPUTS GENERATED")
    print("="*70)
    print(f"\n📊 Results available at: {output_dir}")
    print(f"📁 Evidence copied to: {evidence_dir}")
    
    # Ask if user wants to start dashboard
    print("\n" + "="*70)
    response = input("Would you like to start the dashboard? (y/n): ").strip().lower()
    
    if response == 'y':
        start_dashboard(output_dir)
    else:
        print("\n✓ Demo complete. Run dashboard manually with:")
        print(f"   cd {project_root / 'src'}")
        print(f"   python dashboard.py --events-file {output_dir / 'events.jsonl'}")
    
    print("\n" + "="*70)
    print("Thank you for using Project Sentinel!")
    print("="*70)


if __name__ == "__main__":
    main()
