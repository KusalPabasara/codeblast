#!/usr/bin/env python3
"""
Comprehensive Test Suite for Project Sentinel
Validates all components before submission
"""
import sys
import os
from pathlib import Path
import json


def print_header(text):
    """Print formatted header"""
    print("\n" + "="*70)
    print(text.center(70))
    print("="*70 + "\n")


def test_directory_structure():
    """Verify directory structure compliance"""
    print("[FOLDER] Testing Directory Structure...")
    
    required_paths = [
        "README.md",
        "SUBMISSION_GUIDE.md",
        "requirements.txt",
        "src/algorithms.py",
        "src/config.py",
        "src/data_loader.py",
        "src/event_engine.py",
        "src/main.py",
        "src/dashboard.py",
        "src/streaming_client.py",
        "src/test_algorithms.py",
        "src/templates/dashboard.html",
        "evidence/executables/run_demo.py",
        "evidence/output/test/",
        "evidence/output/final/",
        "evidence/screenshots/"
    ]
    
    all_exist = True
    for path in required_paths:
        full_path = Path(path)
        if full_path.exists():
            print(f"   [OK] {path}")
        else:
            print(f"   [X] MISSING: {path}")
            all_exist = False

    return all_exist


def test_algorithm_tags():
    """Verify algorithm tags are present"""
    print("\n[SEARCH] Testing Algorithm Tags...")
    
    algorithms_file = Path("src/algorithms.py")
    
    if not algorithms_file.exists():
        print("   ✗ algorithms.py not found")
        return False
    
    with open(algorithms_file, 'r') as f:
        content = f.read()
    
    required_tags = [
        "Scanner Avoidance Detection",
        "Barcode Switching Detection",
        "Weight Discrepancy Detection",
        "Queue Length Monitoring",
        "Wait Time Analysis",
        "System Health Monitoring",
        "Staffing Optimization",
        "Inventory Discrepancy Detection",
        "Transaction Success Tracking"
    ]
    
    found_tags = []
    for tag in required_tags:
        if f"@algorithm {tag}" in content:
            print(f"   [OK] Found: {tag}")
            found_tags.append(tag)
        else:
            print(f"   [X] MISSING: {tag}")
    
    print(f"\n   Total: {len(found_tags)}/{len(required_tags)} algorithms tagged")
    return len(found_tags) == len(required_tags)


def test_imports():
    """Test that all modules can be imported"""
    print("\n[PACKAGE] Testing Module Imports...")
    
    sys.path.insert(0, str(Path("src").absolute()))
    
    modules = [
        "config",
        "data_loader",
        "algorithms",
        "event_engine",
        "streaming_client"
    ]
    
    all_imported = True
    for module in modules:
        try:
            __import__(module)
            print(f"   [OK] {module}")
        except Exception as e:
            print(f"   [X] {module}: {e}")
            all_imported = False
    
    return all_imported


def test_config():
    """Verify configuration is valid"""
    print("\n[CONFIG] Testing Configuration...")
    
    try:
        from config import EVENT_TYPES, THRESHOLDS, DATA_SOURCES

        print(f"   [OK] EVENT_TYPES defined ({len(EVENT_TYPES)} types)")
        print(f"   [OK] THRESHOLDS defined ({len(THRESHOLDS)} thresholds)")
        print(f"   [OK] DATA_SOURCES defined ({len(DATA_SOURCES)} sources)")

        # Verify required event types
        required_events = [
            "SUCCESS", "SCANNER_AVOIDANCE", "BARCODE_SWITCHING",
            "WEIGHT_DISCREPANCY", "SYSTEM_CRASH", "LONG_QUEUE",
            "LONG_WAIT", "INVENTORY_DISCREPANCY", "STAFFING_NEEDS"
        ]

        for event in required_events:
            if event in EVENT_TYPES:
                print(f"   [OK] Event type: {event}")
            else:
                print(f"   [X] MISSING event type: {event}")
                return False

        return True

    except Exception as e:
        print(f"   [X] Configuration error: {e}")
        return False


def test_output_format():
    """Verify output format is correct"""
    print("\n[FILE] Testing Output Format...")
    
    test_output = Path("evidence/output/test/events.jsonl")
    
    if not test_output.exists():
        print("   [!] No test output found (run processing first)")
        return None

    try:
        with open(test_output, 'r') as f:
            lines = f.readlines()

        print(f"   [OK] Found {len(lines)} events")

        # Validate format of first event
        if lines:
            event = json.loads(lines[0])

            required_fields = ['timestamp', 'event_id', 'event_data']
            for field in required_fields:
                if field in event:
                    print(f"   [OK] Field present: {field}")
                else:
                    print(f"   [X] MISSING field: {field}")
                    return False

            # Check event_data structure
            if 'event_name' in event['event_data']:
                print(f"   [OK] event_name present: {event['event_data']['event_name']}")
            else:
                print(f"   [X] MISSING event_data.event_name")
                return False

        return True

    except Exception as e:
        print(f"   [X] Output format error: {e}")
        return False


def test_documentation():
    """Verify documentation completeness"""
    print("\n[DOCS] Testing Documentation...")
    
    docs = {
        "README.md": ["Quick Start", "Architecture", "Algorithm"],
        "SUBMISSION_GUIDE.md": ["Team details", "Judge run command"],
        "QUICKSTART.md": ["Step", "Usage"],
        "ALGORITHMS.md": ["Algorithm", "Purpose", "Implementation"]
    }
    
    all_complete = True
    for doc, keywords in docs.items():
        doc_path = Path(doc)
        if doc_path.exists():
            with open(doc_path, 'r', encoding='utf-8') as f:
                content = f.read()

            found_keywords = sum(1 for kw in keywords if kw.lower() in content.lower())
            print(f"   [OK] {doc} ({found_keywords}/{len(keywords)} keywords)")

            if found_keywords < len(keywords):
                all_complete = False
        else:
            print(f"   [X] MISSING: {doc}")
            all_complete = False

    return all_complete


def test_dependencies():
    """Check requirements.txt"""
    print("\n[DEPS] Testing Dependencies...")
    
    req_file = Path("requirements.txt")

    if not req_file.exists():
        print("   [X] requirements.txt not found")
        return False

    with open(req_file, 'r') as f:
        requirements = f.read().strip().split('\n')

    print(f"   [OK] Found {len(requirements)} dependencies")
    for req in requirements:
        print(f"     - {req}")

    return True


def generate_report(results):
    """Generate final test report"""
    print_header("TEST REPORT SUMMARY")
    
    total_tests = len(results)
    passed_tests = sum(1 for r in results.values() if r is True)
    failed_tests = sum(1 for r in results.values() if r is False)
    skipped_tests = sum(1 for r in results.values() if r is None)

    print(f"Total Tests:   {total_tests}")
    print(f"[+] Passed:    {passed_tests}")
    print(f"[-] Failed:    {failed_tests}")
    print(f"[!] Skipped:   {skipped_tests}")
    print()
    
    success_rate = (passed_tests / (total_tests - skipped_tests)) * 100 if (total_tests - skipped_tests) > 0 else 0
    print(f"Success Rate:  {success_rate:.1f}%")
    
    print("\nDetailed Results:")
    for test_name, result in results.items():
        if result is True:
            status = "[+] PASS"
        elif result is False:
            status = "[-] FAIL"
        else:
            status = "[!] SKIP"
        print(f"  {status} - {test_name}")
    
    print()
    
    if failed_tests == 0 and passed_tests > 0:
        print("[SUCCESS] ALL TESTS PASSED! System is ready for submission.")
        return True
    elif failed_tests > 0:
        print("[WARNING] SOME TESTS FAILED! Please fix issues before submission.")
        return False
    else:
        print("[WARNING] RUN PROCESSING FIRST to generate outputs for validation.")
        return None


def main():
    """Run all tests"""
    print_header("PROJECT SENTINEL - COMPREHENSIVE TEST SUITE")
    
    # Change to project root (where this script is located)
    script_dir = Path(__file__).parent
    os.chdir(script_dir)
    
    print(f"Working directory: {Path.cwd()}")
    
    # Run all tests
    results = {
        "Directory Structure": test_directory_structure(),
        "Algorithm Tags": test_algorithm_tags(),
        "Module Imports": test_imports(),
        "Configuration": test_config(),
        "Output Format": test_output_format(),
        "Documentation": test_documentation(),
        "Dependencies": test_dependencies()
    }
    
    # Generate report
    success = generate_report(results)
    
    # Exit code
    if success is True:
        sys.exit(0)
    elif success is False:
        sys.exit(1)
    else:
        sys.exit(2)


if __name__ == "__main__":
    main()
