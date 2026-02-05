"""
Plot utility functions for KMPI reports
Generates charts and graphs for PDF reports
"""
try:
    import matplotlib.pyplot as plt
    import matplotlib
    matplotlib.use('Agg')  # Non-interactive backend
except ImportError:
    print("ERROR: matplotlib not installed")
    print("Run: pip install matplotlib --break-system-packages")
    raise


def create_quarterly_trend_plot(months, entity_vals, crime_vals, output_path, threshold=0.85):
    """
    Create trend plot for entity and crime recall (quarterly KMPI report)
    
    Args:
        months: List of month strings (e.g., ['2025-01', '2025-02', '2025-03'])
        entity_vals: List of entity similarity values (0-1)
        crime_vals: List of crime similarity values (0-1)
        output_path: Path to save the plot
        threshold: Threshold value (default 0.85 for 85%)
    """
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(8, 6))
    
    # Entity recall plot
    ax1.plot(months, [v*100 for v in entity_vals], marker='o', linewidth=2, 
             markersize=8, label='Entity Recall', color='steelblue')
    ax1.axhline(y=threshold*100, color='r', linestyle='--', linewidth=1, 
                label=f'{threshold:.0%} Threshold')
    ax1.set_ylabel('Entity Recall (%)', fontsize=10)
    ax1.set_title('KMPI #1: Entity Recall Trend', fontsize=12, fontweight='bold')
    ax1.grid(True, alpha=0.3)
    ax1.legend()
    ax1.set_ylim([75, 100])
    
    # Crime recall plot
    ax2.plot(months, [v*100 for v in crime_vals], marker='s', linewidth=2, 
             markersize=8, color='green', label='Crime Recall')
    ax2.axhline(y=threshold*100, color='r', linestyle='--', linewidth=1, 
                label=f'{threshold:.0%} Threshold')
    ax2.set_xlabel('Month', fontsize=10)
    ax2.set_ylabel('Crime Recall (%)', fontsize=10)
    ax2.set_title('KMPI #2: Crime Recall Trend', fontsize=12, fontweight='bold')
    ax2.grid(True, alpha=0.3)
    ax2.legend()
    ax2.set_ylim([75, 100])
    
    plt.tight_layout()
    plt.savefig(output_path, dpi=150, bbox_inches='tight')
    plt.close()


def create_productivity_plots(months, values, baseline, max_allowed, output_path):
    """
    Create productivity trend and increase percentage plots (bi-annual report)
    
    Args:
        months: List of month strings (e.g., ['2025-01', '2025-02', ...])
        values: List of articles per person values
        baseline: Baseline value (e.g., 200)
        max_allowed: Maximum allowed value (e.g., 400)
        output_path: Path to save the plot
    """
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(8, 7))
    
    # Productivity trend plot
    ax1.plot(months, values, marker='o', linewidth=2, markersize=8, 
             color='steelblue', label='Articles/Person')
    ax1.axhline(y=baseline, color='green', linestyle='--', linewidth=1.5, 
                label=f'Baseline ({baseline})')
    ax1.axhline(y=max_allowed, color='red', linestyle='--', linewidth=1.5, 
                label=f'Max Allowed ({max_allowed})')
    ax1.fill_between(range(len(months)), baseline, max_allowed, alpha=0.1, color='yellow')
    ax1.set_ylabel('Articles per Person', fontsize=10)
    ax1.set_title('KMPI #4: Article Processing Productivity Trend', fontsize=12, fontweight='bold')
    ax1.grid(True, alpha=0.3)
    ax1.legend(loc='upper left')
    ax1.set_xticks(range(len(months)))
    ax1.set_xticklabels(months, rotation=45, ha='right')
    
    # Increase percentage plot
    increases = [((v - baseline) / baseline) * 100 for v in values]
    colors_list = ['red' if v > max_allowed else 'green' for v in values]
    
    bars = ax2.bar(range(len(months)), increases, color=colors_list, alpha=0.7, edgecolor='black')
    ax2.axhline(y=100, color='red', linestyle='--', linewidth=1.5, label='100% Limit')
    ax2.set_xlabel('Month', fontsize=10)
    ax2.set_ylabel('% Increase vs Baseline', fontsize=10)
    ax2.set_title('Productivity Increase Percentage', fontsize=12, fontweight='bold')
    ax2.grid(True, alpha=0.3, axis='y')
    ax2.legend()
    ax2.set_xticks(range(len(months)))
    ax2.set_xticklabels(months, rotation=45, ha='right')
    
    # Add value labels on bars
    for i, (bar, val) in enumerate(zip(bars, increases)):
        height = bar.get_height()
        ax2.text(bar.get_x() + bar.get_width()/2., height,
                f'{val:.1f}%', ha='center', va='bottom', fontsize=8)
    
    plt.tight_layout()
    plt.savefig(output_path, dpi=150, bbox_inches='tight')
    plt.close()


def create_historical_comparison_plot(quarters, entity_avgs, crime_avgs, output_path, threshold=0.85):
    """
    Create historical comparison plot showing trends across quarters (optional)
    
    Args:
        quarters: List of quarter strings (e.g., ['2024_Q4', '2025_Q1', '2025_Q2'])
        entity_avgs: List of average entity similarity values per quarter
        crime_avgs: List of average crime similarity values per quarter
        output_path: Path to save the plot
        threshold: Threshold value (default 0.85)
    """
    fig, ax = plt.subplots(figsize=(10, 5))
    
    x = range(len(quarters))
    
    ax.plot(x, [v*100 for v in entity_avgs], marker='o', linewidth=2, 
            markersize=8, label='Entity Recall', color='steelblue')
    ax.plot(x, [v*100 for v in crime_avgs], marker='s', linewidth=2, 
            markersize=8, label='Crime Recall', color='green')
    ax.axhline(y=threshold*100, color='r', linestyle='--', linewidth=1, 
               label=f'{threshold:.0%} Threshold')
    
    ax.set_xlabel('Quarter', fontsize=11)
    ax.set_ylabel('Recall (%)', fontsize=11)
    ax.set_title('Historical KMPI Performance', fontsize=13, fontweight='bold')
    ax.grid(True, alpha=0.3)
    ax.legend()
    ax.set_xticks(x)
    ax.set_xticklabels(quarters, rotation=45, ha='right')
    ax.set_ylim([75, 100])
    
    plt.tight_layout()
    plt.savefig(output_path, dpi=150, bbox_inches='tight')
    plt.close()
