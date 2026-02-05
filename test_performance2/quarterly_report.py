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

try:
    from reportlab.lib.pagesizes import letter, A4
    from reportlab.lib import colors
    from reportlab.lib.units import inch
    from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, PageBreak, Image
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib.enums import TA_CENTER, TA_LEFT
except ImportError:
    print("ERROR: Required libraries not installed")
    print("Run: pip install reportlab matplotlib --break-system-packages")
    sys.exit(1)


def generate_pdf_report(quarter, months, entity_vals, crime_vals, passed, failed_months, output_path):
    """Generate PDF report with tables and plots"""
    doc = SimpleDocTemplate(str(output_path), pagesize=letter)
    story = []
    styles = getSampleStyleSheet()
    
    # Custom styles
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=20,
        textColor=colors.HexColor('#1f4788'),
        spaceAfter=30,
        alignment=TA_CENTER
    )
    
    heading_style = ParagraphStyle(
        'CustomHeading',
        parent=styles['Heading2'],
        fontSize=14,
        textColor=colors.HexColor('#1f4788'),
        spaceAfter=12,
        spaceBefore=12
    )
    
    # Page 1: Executive Summary
    story.append(Paragraph(f"Quarterly KMPI Report", title_style))
    story.append(Paragraph(f"Quarter: {quarter}", styles['Normal']))
    story.append(Paragraph(f"Report Date: {datetime.now().strftime('%Y-%m-%d')}", styles['Normal']))
    story.append(Spacer(1, 0.3*inch))
    
    # Status box
    status_text = "✓ PASSED" if passed else "✗ FAILED"
    status_color = colors.green if passed else colors.red
    
    status_data = [
        ['KMPI', 'Description', 'Threshold', 'Status'],
        ['#1', 'Entity Recall', '≥ 85%', status_text],
        ['#2', 'Crime Recall', '≥ 85%', status_text],
    ]
    
    status_table = Table(status_data, colWidths=[0.8*inch, 2.5*inch, 1.2*inch, 1.2*inch])
    status_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 11),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ('FONTSIZE', (0, 1), (-1, -1), 10),
        ('TEXTCOLOR', (3, 1), (3, -1), status_color),
        ('FONTNAME', (3, 1), (3, -1), 'Helvetica-Bold'),
    ]))
    
    story.append(status_table)
    story.append(Spacer(1, 0.4*inch))
    
    # Page 2: Monthly Results
    story.append(Paragraph("Monthly Test Results", heading_style))
    
    monthly_data = [['Month', 'Entity Recall', 'Crime Recall', 'Status']]
    for i, month in enumerate(months):
        entity_pct = f"{entity_vals[i]:.1%}"
        crime_pct = f"{crime_vals[i]:.1%}"
        month_passed = entity_vals[i] >= config.ENTITY_THRESHOLD and crime_vals[i] >= config.CRIME_THRESHOLD
        month_status = "✓ PASS" if month_passed else "✗ FAIL"
        monthly_data.append([month, entity_pct, crime_pct, month_status])
    
    monthly_table = Table(monthly_data, colWidths=[1.5*inch, 1.5*inch, 1.5*inch, 1.2*inch])
    monthly_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 11),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ('FONTSIZE', (0, 1), (-1, -1), 10),
    ]))
    
    story.append(monthly_table)
    story.append(Spacer(1, 0.3*inch))
    
    # Summary stats
    story.append(Paragraph(f"Average Entity Recall: {sum(entity_vals)/len(entity_vals):.1%}", styles['Normal']))
    story.append(Paragraph(f"Average Crime Recall: {sum(crime_vals)/len(crime_vals):.1%}", styles['Normal']))
    story.append(PageBreak())
    
    # Page 3: Trend Plots
    story.append(Paragraph("Performance Trends", heading_style))
    
    # Generate plot
    plot_path = config.KMPI_REPORTS_DIR / f"temp_plot_{quarter}.png"
    create_quarterly_trend_plot(months, entity_vals, crime_vals, plot_path, config.ENTITY_THRESHOLD)
    
    if plot_path.exists():
        img = Image(str(plot_path), width=6*inch, height=4.5*inch)
        story.append(img)
        plot_path.unlink()  # Clean up temp file
    
    story.append(PageBreak())
    
    # Page 4: Root Cause Analysis (if failed)
    if not passed:
        story.append(Paragraph("Root Cause Analysis", heading_style))
        story.append(Paragraph("⚠ KMPI FAILURE DETECTED - INVESTIGATION REQUIRED", 
                             ParagraphStyle('Warning', parent=styles['Normal'], 
                                          textColor=colors.red, fontSize=12, fontName='Helvetica-Bold')))
        story.append(Spacer(1, 0.2*inch))
        
        story.append(Paragraph("Failed Months:", styles['Heading3']))
        for fm in failed_months:
            story.append(Paragraph(
                f"• {fm['month']}: Entity={fm['entity']:.1%}, Crime={fm['crime']:.1%}",
                styles['Normal']
            ))
        
        story.append(Spacer(1, 0.3*inch))
        story.append(Paragraph("Investigation Findings:", styles['Heading3']))
        story.append(Paragraph("[To be completed by Model Owner team]", styles['Italic']))
        story.append(Spacer(1, 0.1*inch))
        story.append(Paragraph("_" * 80, styles['Normal']))
        story.append(Spacer(1, 0.1*inch))
        story.append(Paragraph("_" * 80, styles['Normal']))
        
        story.append(Spacer(1, 0.3*inch))
        story.append(Paragraph("Corrective Actions:", styles['Heading3']))
        story.append(Paragraph("[To be completed by Model Owner team]", styles['Italic']))
        story.append(Spacer(1, 0.1*inch))
        story.append(Paragraph("_" * 80, styles['Normal']))
        story.append(Spacer(1, 0.1*inch))
        story.append(Paragraph("_" * 80, styles['Normal']))
    
    # Build PDF
    doc.build(story)
    print(f"PDF report generated: {output_path}")


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
        generate_pdf_report(quarter, months, entity_vals, crime_vals, passed, failed_months, pdf_file)
    except Exception as e:
        print(f"ERROR generating PDF: {e}")
        print("JSON report saved successfully, but PDF generation failed")
    
    print(f"\nJSON report saved to: {json_file}")
    print(f"{'='*60}\n")
    
    return 0 if passed else 1

if __name__ == "__main__":
    sys.exit(main())
