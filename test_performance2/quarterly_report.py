#!/usr/bin/env python3
"""
Generate quarterly KMPI report from last 3 monthly tests
Usage: python3 quarterly_report.py
"""
import sys
import json
from datetime import datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))
import test_performance.config as config

def main():
    print(f"\n{'='*60}")
    print(f"Quarterly KMPI Report - {datetime.now().strftime('%Y Q%q')}")
    print(f"{'='*60}\n")
    
    # Get last 3 monthly results
    monthly_files = sorted(config.LOGS_DIR.glob("monthly_*.json"))[-3:]
    
    if len(monthly_files) < 3:
        print(f"ERROR: Need 3 monthly results, found {len(monthly_files)}")
        return 1
    
    # Load results
    results = []
    for f in monthly_files:
        with open(f) as file:
            results.append(json.load(file))
    
    # Check each month for both thresholds
    entity_vals = []
    crime_vals = []
    failed_85 = []  # KMPI #1 and #2 (85%)
    failed_83 = []  # KMPI #5 (83%)
    
    for r in results:
        month = r['timestamp'][:7]
        entity = r['aggregate_metrics']['avg_entity_similarity']
        crime = r['aggregate_metrics']['avg_crime_similarity']
        
        entity_vals.append(entity)
        crime_vals.append(crime)
        
        # Check 85% threshold (KMPI #1 and #2)
        if entity < config.ENTITY_THRESHOLD or crime < config.CRIME_THRESHOLD:
            failed_85.append({'month': month, 'entity': entity, 'crime': crime})
        
        # Check 83% threshold for entity (KMPI #5)
        if entity < config.ENTITY_THRESHOLD_ALT:
            failed_83.append({'month': month, 'entity': entity})
    
    # Calculate pass/fail
    kmpi_1_2_passed = len(failed_85) == 0
    kmpi_5_passed = len(failed_83) == 0
    
    # Print report
    print(f"Months checked: {', '.join([r['timestamp'][:7] for r in results])}\n")
    
    print(f"KMPI #1 & #2 (85% threshold):")
    print(f"  Entity recall: {sum(entity_vals)/3:.2%} avg")
    print(f"  Crime recall:  {sum(crime_vals)/3:.2%} avg")
    print(f"  Status: {'✓ PASSED' if kmpi_1_2_passed else '✗ FAILED'}")
    if not kmpi_1_2_passed:
        for fm in failed_85:
            print(f"    {fm['month']}: entity={fm['entity']:.2%}, crime={fm['crime']:.2%}")
    
    print(f"\nKMPI #5 (83% threshold):")
    print(f"  Entity recall: {sum(entity_vals)/3:.2%} avg")
    print(f"  Status: {'✓ PASSED' if kmpi_5_passed else '✗ FAILED'}")
    if not kmpi_5_passed:
        for fm in failed_83:
            print(f"    {fm['month']}: entity={fm['entity']:.2%}")
    
    overall_passed = kmpi_1_2_passed and kmpi_5_passed
    
    if not overall_passed:
        print(f"\n✗ ROOT CAUSE ANALYSIS REQUIRED")
    
    # Save report
    quarter = f"{datetime.now().year}_Q{(datetime.now().month-1)//3 + 1}"
    report = {
        'quarter': quarter,
        'months': [r['timestamp'][:7] for r in results],
        'kmpi_1_2': {
            'passed': kmpi_1_2_passed,
            'entity_avg': sum(entity_vals)/3,
            'crime_avg': sum(crime_vals)/3,
            'failed_months': failed_85
        },
        'kmpi_5': {
            'passed': kmpi_5_passed,
            'entity_avg': sum(entity_vals)/3,
            'failed_months': failed_83
        },
        'overall_passed': overall_passed
    }
    
    report_file = config.KMPI_REPORTS_DIR / f"kmpi_{quarter}.json"
    with open(report_file, 'w') as f:
        json.dump(report, f, indent=2)
    
    print(f"\nReport saved to: {report_file}")
    print(f"{'='*60}\n")
    
    return 0 if overall_passed else 1

if __name__ == "__main__":
    sys.exit(main())
