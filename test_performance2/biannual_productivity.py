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


def generate_pdf_report(period, months, values, baseline, max_allowed, passed, exceeded, output_path):
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
    story.append(Paragraph(f"Bi-Annual Productivity KMPI Report", title_style))
    story.append(Paragraph(f"Period: {period}", styles['Normal']))
    story.append(Paragraph(f"Report Date: {datetime.now().strftime('%Y-%m-%d')}", styles['Normal']))
    story.append(Spacer(1, 0.3*inch))
    
    # Status box
    status_text = "✓ PASSED" if passed else "✗ FAILED"
    status_color = colors.green if passed else colors.red
    
    status_data = [
        ['KMPI', 'Description', 'Baseline', 'Max Allowed', 'Status'],
        ['#4', 'Article Processing Productivity', f'{baseline}', f'{max_allowed}', status_text],
    ]
    
    status_table = Table(status_data, colWidths=[0.7*inch, 2.3*inch, 1*inch, 1.2*inch, 1*inch])
    status_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 10),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ('FONTSIZE', (0, 1), (-1, -1), 9),
        ('TEXTCOLOR', (4, 1), (4, -1), status_color),
        ('FONTNAME', (4, 1), (4, -1), 'Helvetica-Bold'),
    ]))
    
    story.append(status_table)
    story.append(Spacer(1, 0.3*inch))
    
    story.append(Paragraph("<b>Evaluation Criteria:</b>", styles['Normal']))
    story.append(Paragraph(
        f"• Baseline: {baseline} articles per person per month (manual processing capacity)", 
        styles['Normal']
    ))
    story.append(Paragraph(
        f"• Maximum allowed: {max_allowed} articles per person per month (100% increase)", 
        styles['Normal']
    ))
    story.append(Paragraph(
        "• PASS if all 6 months ≤ 400 articles/person", 
        styles['Normal']
    ))
    story.append(Paragraph(
        "• FAIL if any month > 400 articles/person (triggers IRR re-assessment)", 
        styles['Normal']
    ))
    
    story.append(PageBreak())
    
    # Page 2: Monthly Results
    story.append(Paragraph("Monthly Productivity Values", heading_style))
    
    monthly_data = [['Month', 'Articles/Person', '% Increase', 'Status']]
    for i, month in enumerate(months):
        articles = values[i]
        increase = ((articles - baseline) / baseline) * 100
        month_passed = articles <= max_allowed
        month_status = "✓ PASS" if month_passed else "✗ FAIL"
        monthly_data.append([
            month, 
            f"{articles:.0f}", 
            f"{increase:+.1f}%", 
            month_status
        ])
    
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
    avg_articles = sum(values) / len(values)
    max_articles = max(values)
    min_articles = min(values)
    
    story.append(Paragraph(f"<b>Summary Statistics:</b>", styles['Normal']))
    story.append(Paragraph(f"• Average: {avg_articles:.0f} articles/person", styles['Normal']))
    story.append(Paragraph(f"• Maximum: {max_articles:.0f} articles/person", styles['Normal']))
    story.append(Paragraph(f"• Minimum: {min_articles:.0f} articles/person", styles['Normal']))
    
    story.append(PageBreak())
    
    # Page 3: Trend Plots
    story.append(Paragraph("Productivity Trends", heading_style))
    
    # Generate plot
    plot_path = config.KMPI_REPORTS_DIR / f"temp_plot_{period}.png"
    create_productivity_plots(months, values, baseline, max_allowed, plot_path)
    
    if plot_path.exists():
        img = Image(str(plot_path), width=6*inch, height=5.2*inch)
        story.append(img)
        plot_path.unlink()  # Clean up temp file
    
    story.append(PageBreak())
    
    # Page 4: IRR Re-assessment (if failed)
    if not passed:
        story.append(Paragraph("IRR Re-assessment Trigger", heading_style))
        story.append(Paragraph("⚠ PRODUCTIVITY LIMIT EXCEEDED - IRR RE-ASSESSMENT REQUIRED", 
                             ParagraphStyle('Warning', parent=styles['Normal'], 
                                          textColor=colors.red, fontSize=12, fontName='Helvetica-Bold')))
        story.append(Spacer(1, 0.2*inch))
        
        story.append(Paragraph("Months Exceeding Limit:", styles['Heading3']))
        for ex in exceeded:
            increase = ((ex['avg'] - baseline) / baseline) * 100
            story.append(Paragraph(
                f"• {ex['month']}: {ex['avg']:.0f} articles/person ({increase:+.1f}% increase)",
                styles['Normal']
            ))
        
        story.append(Spacer(1, 0.3*inch))
        story.append(Paragraph("Impact Analysis:", styles['Heading3']))
        story.append(Paragraph("[To be completed by Model Owner team]", styles['Italic']))
        story.append(Spacer(1, 0.1*inch))
        story.append(Paragraph("• Workload sustainability assessment:", styles['Normal']))
        story.append(Paragraph("_" * 80, styles['Normal']))
        story.append(Spacer(1, 0.1*inch))
        story.append(Paragraph("• Quality impact assessment:", styles['Normal']))
        story.append(Paragraph("_" * 80, styles['Normal']))
        story.append(Spacer(1, 0.1*inch))
        story.append(Paragraph("• Resource implications:", styles['Normal']))
        story.append(Paragraph("_" * 80, styles['Normal']))
        
        story.append(Spacer(1, 0.3*inch))
        story.append(Paragraph("Recommended Actions:", styles['Heading3']))
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
        generate_pdf_report(period, months, values, config.BASELINE_ARTICLES_PER_PERSON, 
                          config.MAX_ARTICLES_PER_PERSON, passed, exceeded, pdf_file)
    except Exception as e:
        print(f"ERROR generating PDF: {e}")
        print("JSON report saved successfully, but PDF generation failed")
    
    print(f"\nJSON report saved to: {json_file}")
    print(f"{'='*60}\n")
    
    return 0 if passed else 1

if __name__ == "__main__":
    sys.exit(main())
