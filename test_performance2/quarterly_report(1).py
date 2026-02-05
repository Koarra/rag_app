#!/usr/bin/env python3
"""
Quarterly KMPI Report Generator with PDF output
Checks KMPI #1 (entity recall) and KMPI #2 (crime recall)
Usage: python3 quarterly_report.py
"""
import sys
import json
from datetime import datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))
import test_performance.config as config
from test_performance.plot_utils import create_quarterly_trend_plot
from test_performance.pdf_utils import generate_quarterly_pdf_report


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
    
    # Check each month
    entity_vals = []
    crime_vals = []
    failed_months = []
    
    for r in results:
        month = r['timestamp'][:7]
        entity = r['aggregate_metrics']['avg_entity_similarity']
        crime = r['aggregate_metrics']['avg_crime_similarity']
        
        entity_vals.append(entity)
        crime_vals.append(crime)
        
        # Check 85% threshold (KMPI #1 and #2)
        if entity < config.ENTITY_THRESHOLD or crime < config.CRIME_THRESHOLD:
            failed_months.append({'month': month, 'entity': entity, 'crime': crime})
    
    # Calculate pass/fail
    passed = len(failed_months) == 0
    
    # Print console report
    months = [r['timestamp'][:7] for r in results]
    print(f"Months checked: {', '.join(months)}\n")
    
    print(f"KMPI #1: Entity recall (85% threshold)")
    print(f"  Average: {sum(entity_vals)/3:.2%}")
    print(f"KMPI #2: Crime recall (85% threshold)")
    print(f"  Average: {sum(crime_vals)/3:.2%}")
    print(f"\nOverall Status: {'✓ PASSED' if passed else '✗ FAILED'}")
    
    if not passed:
        print(f"\nFailed months:")
        for fm in failed_months:
            print(f"  {fm['month']}: entity={fm['entity']:.2%}, crime={fm['crime']:.2%}")
        print(f"\n✗ ROOT CAUSE ANALYSIS REQUIRED")
    
    # Save JSON report
    quarter = f"{datetime.now().year}_Q{(datetime.now().month-1)//3 + 1}"
    report = {
        'quarter': quarter,
        'months': months,
        'kmpi_1_entity': {
            'passed': passed,
            'entity_avg': sum(entity_vals)/3,
            'failed_months': failed_months
        },
        'kmpi_2_crime': {
            'passed': passed,
            'crime_avg': sum(crime_vals)/3,
            'failed_months': failed_months
        },
        'overall_passed': passed
    }
    
    json_file = config.KMPI_REPORTS_DIR / f"kmpi_{quarter}.json"
    with open(json_file, 'w') as f:
        json.dump(report, f, indent=2)
    
    # Generate PDF report
    pdf_file = config.KMPI_REPORTS_DIR / f"kmpi_quarterly_{quarter}.pdf"
    try:
        # Generate plot
        plot_path = config.KMPI_REPORTS_DIR / f"temp_plot_{quarter}.png"
        create_quarterly_trend_plot(months, entity_vals, crime_vals, plot_path, config.ENTITY_THRESHOLD)
        
        # Generate PDF
        generate_quarterly_pdf_report(quarter, months, entity_vals, crime_vals, passed, 
                                     failed_months, plot_path, pdf_file, config.ENTITY_THRESHOLD)
        
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
