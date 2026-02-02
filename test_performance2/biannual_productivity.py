#!/usr/bin/env python3
"""
Bi-annual productivity KMPI report (KMPI #4)
Checks last 6 months of article processing data
Usage: python3 biannual_productivity.py
"""
import sys
import json
from datetime import datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))
import test_performance.config as config

def main():
    print(f"\n{'='*60}")
    print(f"Bi-Annual Productivity Report - {datetime.now().strftime('%Y H%H')}")
    print(f"{'='*60}\n")
    
    # Load productivity data
    metrics_file = config.PRODUCTION_METRICS_DIR / "productivity.json"
    
    if not metrics_file.exists():
        print(f"ERROR: Productivity data not found at {metrics_file}")
        print(f"\nYou need to track production metrics in this format:")
        print("""[
  {"month": "2025-01", "avg_articles_per_person": 210},
  {"month": "2025-02", "avg_articles_per_person": 225},
  ...
]""")
        return 1
    
    with open(metrics_file) as f:
        all_data = json.load(f)
    
    # Get last 6 months
    if len(all_data) < 6:
        print(f"ERROR: Need 6 months of data, found {len(all_data)}")
        return 1
    
    last_6_months = all_data[-6:]
    
    # Check if any month exceeded limit
    exceeded = []
    for data in last_6_months:
        month = data['month']
        avg = data['avg_articles_per_person']
        
        if avg > config.MAX_ARTICLES_PER_PERSON:
            exceeded.append({'month': month, 'avg': avg})
    
    passed = len(exceeded) == 0
    
    # Print report
    print(f"Period: {last_6_months[0]['month']} to {last_6_months[-1]['month']}")
    print(f"Baseline: {config.BASELINE_ARTICLES_PER_PERSON} articles/person/month")
    print(f"Max allowed: {config.MAX_ARTICLES_PER_PERSON} articles/person/month (100% increase)\n")
    
    print("Monthly values:")
    for data in last_6_months:
        avg = data['avg_articles_per_person']
        increase = ((avg - config.BASELINE_ARTICLES_PER_PERSON) / config.BASELINE_ARTICLES_PER_PERSON) * 100
        status = "✗ EXCEEDED" if avg > config.MAX_ARTICLES_PER_PERSON else "✓"
        print(f"  {data['month']}: {avg:.0f} articles ({increase:+.1f}%) {status}")
    
    if passed:
        print(f"\n✓ KMPI #4 PASSED")
    else:
        print(f"\n✗ KMPI #4 FAILED - IRR re-assessment required")
        for ex in exceeded:
            print(f"  {ex['month']}: {ex['avg']:.0f} articles (exceeded {config.MAX_ARTICLES_PER_PERSON})")
    
    # Save report
    semester = "H1" if datetime.now().month <= 6 else "H2"
    year = datetime.now().year
    
    report = {
        'period': f"{year}_{semester}",
        'months': [d['month'] for d in last_6_months],
        'baseline': config.BASELINE_ARTICLES_PER_PERSON,
        'max_allowed': config.MAX_ARTICLES_PER_PERSON,
        'passed': passed,
        'exceeded_months': exceeded,
        'monthly_values': last_6_months
    }
    
    report_file = config.KMPI_REPORTS_DIR / f"productivity_{year}_{semester}.json"
    with open(report_file, 'w') as f:
        json.dump(report, f, indent=2)
    
    print(f"\nReport saved to: {report_file}")
    print(f"{'='*60}\n")
    
    return 0 if passed else 1

if __name__ == "__main__":
    sys.exit(main())
