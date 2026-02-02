#!/usr/bin/env python3
"""
Run monthly KMPI test
Usage: python3 monthly_test.py
"""
import sys
import json
from datetime import datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from test_performance.run_test import run_performance_test
import test_performance.config as config

def main():
    print(f"\n{'='*60}")
    print(f"Monthly KMPI Test - {datetime.now().strftime('%Y-%m')}")
    print(f"{'='*60}\n")
    
    # Run test
    result = run_performance_test(verbose=True)
    
    if result is None:
        print("ERROR: Test failed to run")
        return 1
    
    # Save monthly result
    month = datetime.now().strftime('%Y%m')
    result_file = config.LOGS_DIR / f"monthly_{month}.json"
    with open(result_file, 'w') as f:
        json.dump(result, f, indent=2)
    
    print(f"\nSaved to: {result_file}")
    
    # Return exit code
    return 0 if result['aggregate_metrics']['overall_passed'] else 1

if __name__ == "__main__":
    sys.exit(main())
