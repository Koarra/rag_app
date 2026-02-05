#!/usr/bin/env python3
"""
Quarterly KMPI Report Generator
Evaluates KMPI #1 (entity recall) and KMPI #2 (crime recall)
Generates PDF report with plots
Usage: python3 quarterly_report.py
"""
import sys
import json
from datetime import datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))
import test_performance.config as config
from test_performance.entity_recall import evaluate_entity_recall
from test_performance.crime_recall import evaluate_crime_recall
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
    
    # Load results and extract months from filenames
    results = []
    months = []
    
    for f in monthly_files:
        with open(f) as file:
            results.append(json.load(file))
        
        # Extract month from filename (monthly_YYYYMM.json -> YYYY-MM)
        filename = f.stem
        month = filename.replace('monthly_', '')
        if len(month) == 6:
            months.append(f"{month[:4]}-{month[4:]}")
        else:
            # Fallback to timestamp
            months.append(results[-1]['timestamp'][:7])
    
    print(f"Months checked: {', '.join(months)}\n")
    
    # Evaluate KMPI #1: Entity Recall
    kmpi1 = evaluate_entity_recall(results, months, config.ENTITY_THRESHOLD)
    
    # Evaluate KMPI #2: Crime Recall
    kmpi2 = evaluate_crime_recall(results, months, config.CRIME_THRESHOLD)
    
    # Overall pass/fail
    overall_passed = kmpi1['passed'] and kmpi2['passed']
    
    # Combine failed months from both KMPIs
    failed_months = []
    for i in range(len(months)):
        entity = kmpi1['entity_vals'][i]
        crime = kmpi2['crime_vals'][i]
        
        if entity < config.ENTITY_THRESHOLD or crime < config.CRIME_THRESHOLD:
            failed_months.append({
                'month': months[i],
                'entity': entity,
                'crime': crime
            })
    
    # Print console report
    print(f"KMPI #1: Entity recall ({config.ENTITY_THRESHOLD:.0%} threshold)")
    print(f"  Average: {kmpi1['average']:.2%}")
    print(f"  Status: {'✓ PASSED' if kmpi1['passed'] else '✗ FAILED'}")
    
    print(f"\nKMPI #2: Crime recall ({config.CRIME_THRESHOLD:.0%} threshold)")
    print(f"  Average: {kmpi2['average']:.2%}")
    print(f"  Status: {'✓ PASSED' if kmpi2['passed'] else '✗ FAILED'}")
    
    print(f"\nOverall Status: {'✓ PASSED' if overall_passed else '✗ FAILED'}")
    
    if not overall_passed:
        print(f"\nFailed months:")
        for fm in failed_months:
            print(f"  {fm['month']}: entity={fm['entity']:.2%}, crime={fm['crime']:.2%}")
        print(f"\n✗ ROOT CAUSE ANALYSIS REQUIRED")
    
    # Save JSON report
    quarter = f"{datetime.now().year}_Q{(datetime.now().month-1)//3 + 1}"
    report = {
        'quarter': quarter,
        'months': months,
        'kmpi_1': kmpi1,
        'kmpi_2': kmpi2,
        'overall_passed': overall_passed,
        'failed_months': failed_months
    }
    
    json_file = config.KMPI_REPORTS_DIR / f"kmpi_{quarter}.json"
    with open(json_file, 'w') as f:
        json.dump(report, f, indent=2)
    
    # Generate PDF report
    pdf_file = config.KMPI_REPORTS_DIR / f"kmpi_quarterly_{quarter}.pdf"
    try:
        # Generate plot
        plot_path = config.KMPI_REPORTS_DIR / f"temp_plot_{quarter}.png"
        print(f"\nGenerating plot at: {plot_path}")
        
        create_quarterly_trend_plot(months, kmpi1['entity_vals'], kmpi2['crime_vals'], 
                                   plot_path, config.ENTITY_THRESHOLD)
        
        # Verify plot was created
        if not plot_path.exists():
            raise FileNotFoundError(f"Plot file was not created at {plot_path}")
        
        print(f"Plot created successfully")
        
        # Generate PDF
        generate_quarterly_pdf_report(quarter, months, kmpi1['entity_vals'], kmpi2['crime_vals'], 
                                     overall_passed, failed_months, plot_path, pdf_file, 
                                     config.ENTITY_THRESHOLD, config.CRIME_THRESHOLD)
        
        # Clean up temp file
        if plot_path.exists():
            plot_path.unlink()
            
        print(f"PDF report generated: {pdf_file}")
    except Exception as e:
        print(f"ERROR generating PDF: {e}")
        import traceback
        traceback.print_exc()
        print("JSON report saved successfully, but PDF generation failed")
    
    print(f"\nJSON report saved to: {json_file}")
    print(f"{'='*60}\n")
    
    return 0 if overall_passed else 1

if __name__ == "__main__":
    sys.exit(main())
