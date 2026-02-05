"""
PDF report generation utilities for KMPI reports
Generates formatted PDF documents with tables and charts
"""
from pathlib import Path

try:
    from reportlab.lib.pagesizes import letter
    from reportlab.lib import colors
    from reportlab.lib.units import inch
    from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, PageBreak, Image
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib.enums import TA_CENTER
except ImportError:
    print("ERROR: reportlab not installed")
    print("Run: pip install reportlab --break-system-packages")
    raise


def generate_quarterly_pdf_report(quarter, months, entity_vals, crime_vals, passed, 
                                  failed_months, plot_path, output_path, entity_threshold, crime_threshold):
    """
    Generate quarterly KMPI PDF report
    
    Args:
        quarter: Quarter string (e.g., '2025_Q1')
        months: List of month strings
        entity_vals: List of entity similarity values (0-1)
        crime_vals: List of crime similarity values (0-1)
        passed: Boolean, overall pass/fail
        failed_months: List of dicts with failed month details
        plot_path: Path to trend plot image
        output_path: Path to save PDF
        entity_threshold: Entity recall threshold (e.g., 0.85)
        crime_threshold: Crime recall threshold (e.g., 0.85)
    """
    from datetime import datetime
    
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
        ['#1', 'Entity Recall', f'≥ {entity_threshold:.0%}', status_text],
        ['#2', 'Crime Recall', f'≥ {crime_threshold:.0%}', status_text],
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
        month_passed = entity_vals[i] >= entity_threshold and crime_vals[i] >= crime_threshold
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
    
    if plot_path.exists():
        img = Image(str(plot_path), width=6*inch, height=4.5*inch)
        story.append(img)
    
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


def generate_productivity_pdf_report(period, months, values, baseline, max_allowed, 
                                    passed, exceeded, plot_path, output_path):
    """
    Generate bi-annual productivity KMPI PDF report
    
    Args:
        period: Period string (e.g., '2025_H1')
        months: List of month strings
        values: List of articles per person values
        baseline: Baseline value (e.g., 200)
        max_allowed: Maximum allowed value (e.g., 400)
        passed: Boolean, overall pass/fail
        exceeded: List of dicts with exceeded month details
        plot_path: Path to productivity plot image
        output_path: Path to save PDF
    """
    from datetime import datetime
    
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
        f"• PASS if all 6 months ≤ {max_allowed} articles/person", 
        styles['Normal']
    ))
    story.append(Paragraph(
        f"• FAIL if any month > {max_allowed} articles/person (triggers IRR re-assessment)", 
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
    
    if plot_path.exists():
        img = Image(str(plot_path), width=6*inch, height=5.2*inch)
        story.append(img)
    
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
