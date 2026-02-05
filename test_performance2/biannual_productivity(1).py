#!/usr/bin/env python3
"""
Bi-annual productivity KMPI report (KMPI #4) with PDF output
Checks last 6 months of article processing data
Usage: python3 biannual_productivity.py
"""
import sys
import json
from datetime import datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))
import test_performance.config as config
from test_performance.plot_utils import create_productivity_plots
from test_performance.pdf_utils import generate_productivity_pdf_report


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
    
    # Extract data
    months = [d['month'] for d in last_6_months]
    values = [d['avg_articles_per_person'] for d in last_6_months]
    
    # Check if any month exceeded limit
    exceeded = []
    for data in last_6_months:
        month = data['month']
        avg = data['avg_articles_per_person']
        
        if avg > config.MAX_ARTICLES_PER_PERSON:
            exceeded.append({'month': month, 'avg': avg})
    
    passed = len(exceeded) == 0
    
    # Print console report
    print(f"Period: {months[0]} to {months[-1]}")
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
    
    # Save JSON report
    semester = "H1" if datetime.now().month <= 6 else "H2"
    year = datetime.now().year
    period = f"{year}_{semester}"
    
    report = {
        'period': period,
        'months': months,
        'baseline': config.BASELINE_ARTICLES_PER_PERSON,
        'max_allowed': config.MAX_ARTICLES_PER_PERSON,
        'passed': passed,
        'exceeded_months': exceeded,
        'monthly_values': last_6_months
    }
    
    json_file = config.KMPI_REPORTS_DIR / f"productivity_{period}.json"
    with open(json_file, 'w') as f:
        json.dump(report, f, indent=2)
    
    # Generate PDF report
    pdf_file = config.KMPI_REPORTS_DIR / f"kmpi_productivity_{period}.pdf"
    try:
        # Generate plot
        plot_path = config.KMPI_REPORTS_DIR / f"temp_plot_{period}.png"
        create_productivity_plots(months, values, config.BASELINE_ARTICLES_PER_PERSON, 
                                config.MAX_ARTICLES_PER_PERSON, plot_path)
        
        # Generate PDF
        generate_productivity_pdf_report(period, months, values, config.BASELINE_ARTICLES_PER_PERSON, 
                                        config.MAX_ARTICLES_PER_PERSON, passed, exceeded, plot_path, pdf_file)
        
        # Clean up temp file
        if plot_path.exists():
            plot_path.unlink()
            
        print(f"PDF report generated: {pdf_file}")
    except Exception as e:
        print(f"ERROR generating PDF: {e}")
        print("JSON report saved successfully, but PDF generation failed")
    
    print(f"\nJSON report saved to: {json_file}")
    print(f"{'='*60}\n")
    
    return 0 if passed else 1

if __name__ == "__main__":
    sys.exit(main())
