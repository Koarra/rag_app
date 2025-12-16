"""
Elbow plot visualization for performance test results.

Creates plots showing how entity and crime similarity metrics evolve over time,
helping identify trends, degradations, and improvements in model performance.
"""

import json
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from datetime import datetime
from pathlib import Path
import numpy as np
from typing import List, Dict, Tuple
import sys

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

import test_performance.config as config


def load_test_results(log_path: Path) -> List[Dict]:
    """
    Load test results from JSONL log file.

    Args:
        log_path: Path to test_results.jsonl file

    Returns:
        List of test result dictionaries sorted by timestamp
    """
    if not log_path.exists():
        print(f"No test results found at {log_path}")
        return []

    results = []
    with open(log_path, 'r', encoding='utf-8') as f:
        for line in f:
            if line.strip():
                results.append(json.loads(line))

    # Sort by timestamp
    results.sort(key=lambda x: x['timestamp'])
    return results


def extract_metrics(results: List[Dict]) -> Tuple[List, List, List]:
    """
    Extract timestamps and metrics from test results.

    Returns:
        Tuple of (timestamps, entity_similarities, crime_similarities)
    """
    timestamps = []
    entity_sims = []
    crime_sims = []

    for result in results:
        try:
            timestamp = datetime.fromisoformat(result['timestamp'])
            timestamps.append(timestamp)
            entity_sims.append(result['aggregate_metrics']['avg_entity_similarity'])
            crime_sims.append(result['aggregate_metrics']['avg_crime_similarity'])
        except (KeyError, ValueError) as e:
            print(f"Warning: Skipping invalid result entry: {e}")
            continue

    return timestamps, entity_sims, crime_sims


def calculate_elbow_points(values: List[float], threshold: float = 0.05) -> List[int]:
    """
    Identify potential elbow points where there's a significant change.

    Args:
        values: List of metric values
        threshold: Minimum change rate to be considered an elbow

    Returns:
        List of indices where elbow points occur
    """
    if len(values) < 3:
        return []

    elbow_points = []

    # Calculate rate of change
    for i in range(1, len(values) - 1):
        prev_change = abs(values[i] - values[i-1])
        next_change = abs(values[i+1] - values[i])

        # Significant change in rate
        if abs(prev_change - next_change) > threshold:
            elbow_points.append(i)

    return elbow_points


def plot_performance_trends(results: List[Dict], output_path: Path = None):
    """
    Create elbow plot showing performance trends over time.

    Args:
        results: List of test result dictionaries
        output_path: Optional path to save the plot
    """
    if not results:
        print("No results to plot!")
        return

    timestamps, entity_sims, crime_sims = extract_metrics(results)

    if not timestamps:
        print("No valid data to plot!")
        return

    # Create figure with two subplots
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 10))
    fig.suptitle('Performance Test Results: Similarity Metrics Over Time',
                 fontsize=16, fontweight='bold')

    # Plot 1: Entity Similarity
    ax1.plot(timestamps, entity_sims, marker='o', linestyle='-',
             linewidth=2, markersize=8, color='#2E86AB', label='Entity Similarity')
    ax1.axhline(y=config.ENTITY_SIMILARITY_THRESHOLD, color='red',
                linestyle='--', linewidth=2, label=f'Threshold ({config.ENTITY_SIMILARITY_THRESHOLD:.0%})')

    # Mark elbow points
    elbow_indices = calculate_elbow_points(entity_sims)
    if elbow_indices:
        elbow_times = [timestamps[i] for i in elbow_indices]
        elbow_vals = [entity_sims[i] for i in elbow_indices]
        ax1.scatter(elbow_times, elbow_vals, color='orange', s=200,
                   marker='*', zorder=5, label='Significant Changes')

    # Formatting
    ax1.set_ylabel('Entity Similarity', fontsize=12, fontweight='bold')
    ax1.set_title('Entity Detection Performance', fontsize=14)
    ax1.legend(loc='best', fontsize=10)
    ax1.grid(True, alpha=0.3)
    ax1.set_ylim([0, 1.05])

    # Format y-axis as percentage
    ax1.yaxis.set_major_formatter(plt.FuncFormatter(lambda y, _: f'{y:.0%}'))

    # Plot 2: Crime Similarity
    ax2.plot(timestamps, crime_sims, marker='s', linestyle='-',
             linewidth=2, markersize=8, color='#A23B72', label='Crime Similarity')
    ax2.axhline(y=config.CRIME_SIMILARITY_THRESHOLD, color='red',
                linestyle='--', linewidth=2, label=f'Threshold ({config.CRIME_SIMILARITY_THRESHOLD:.0%})')

    # Mark elbow points
    elbow_indices = calculate_elbow_points(crime_sims)
    if elbow_indices:
        elbow_times = [timestamps[i] for i in elbow_indices]
        elbow_vals = [crime_sims[i] for i in elbow_indices]
        ax2.scatter(elbow_times, elbow_vals, color='orange', s=200,
                   marker='*', zorder=5, label='Significant Changes')

    # Formatting
    ax2.set_xlabel('Test Run Date', fontsize=12, fontweight='bold')
    ax2.set_ylabel('Crime Similarity', fontsize=12, fontweight='bold')
    ax2.set_title('Crime Classification Performance', fontsize=14)
    ax2.legend(loc='best', fontsize=10)
    ax2.grid(True, alpha=0.3)
    ax2.set_ylim([0, 1.05])

    # Format y-axis as percentage
    ax2.yaxis.set_major_formatter(plt.FuncFormatter(lambda y, _: f'{y:.0%}'))

    # Format x-axis dates
    for ax in [ax1, ax2]:
        ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d %H:%M'))
        plt.setp(ax.xaxis.get_majorticklabels(), rotation=45, ha='right')

    plt.tight_layout()

    # Save or show
    if output_path:
        plt.savefig(output_path, dpi=300, bbox_inches='tight')
        print(f"Plot saved to: {output_path}")
    else:
        plt.show()


def plot_combined_metrics(results: List[Dict], output_path: Path = None):
    """
    Create a single plot with both metrics for comparison.

    Args:
        results: List of test result dictionaries
        output_path: Optional path to save the plot
    """
    if not results:
        print("No results to plot!")
        return

    timestamps, entity_sims, crime_sims = extract_metrics(results)

    if not timestamps:
        print("No valid data to plot!")
        return

    # Create figure
    fig, ax = plt.subplots(figsize=(14, 8))

    # Plot both metrics
    ax.plot(timestamps, entity_sims, marker='o', linestyle='-',
            linewidth=2, markersize=8, color='#2E86AB', label='Entity Similarity')
    ax.plot(timestamps, crime_sims, marker='s', linestyle='-',
            linewidth=2, markersize=8, color='#A23B72', label='Crime Similarity')

    # Threshold lines
    ax.axhline(y=config.ENTITY_SIMILARITY_THRESHOLD, color='#2E86AB',
               linestyle='--', linewidth=1.5, alpha=0.7,
               label=f'Entity Threshold ({config.ENTITY_SIMILARITY_THRESHOLD:.0%})')
    ax.axhline(y=config.CRIME_SIMILARITY_THRESHOLD, color='#A23B72',
               linestyle='--', linewidth=1.5, alpha=0.7,
               label=f'Crime Threshold ({config.CRIME_SIMILARITY_THRESHOLD:.0%})')

    # Formatting
    ax.set_xlabel('Test Run Date', fontsize=12, fontweight='bold')
    ax.set_ylabel('Similarity Score', fontsize=12, fontweight='bold')
    ax.set_title('Performance Test Results: Entity vs Crime Similarity Over Time',
                 fontsize=16, fontweight='bold')
    ax.legend(loc='best', fontsize=11)
    ax.grid(True, alpha=0.3)
    ax.set_ylim([0, 1.05])

    # Format axes
    ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda y, _: f'{y:.0%}'))
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d %H:%M'))
    plt.setp(ax.xaxis.get_majorticklabels(), rotation=45, ha='right')

    plt.tight_layout()

    # Save or show
    if output_path:
        plt.savefig(output_path, dpi=300, bbox_inches='tight')
        print(f"Combined plot saved to: {output_path}")
    else:
        plt.show()


def plot_article_breakdown(results: List[Dict], output_path: Path = None):
    """
    Create a plot showing per-article performance over time.

    Args:
        results: List of test result dictionaries
        output_path: Optional path to save the plot
    """
    if not results:
        print("No results to plot!")
        return

    # Extract per-article data
    article_data = {}

    for result in results:
        timestamp = datetime.fromisoformat(result['timestamp'])
        for article_result in result.get('individual_results', []):
            article_name = article_result['article']

            if article_name not in article_data:
                article_data[article_name] = {
                    'timestamps': [],
                    'entity_sims': [],
                    'crime_sims': []
                }

            article_data[article_name]['timestamps'].append(timestamp)
            article_data[article_name]['entity_sims'].append(article_result['entity_similarity'])
            article_data[article_name]['crime_sims'].append(article_result['crime_similarity'])

    if not article_data:
        print("No article data to plot!")
        return

    # Create figure with subplots for each article
    n_articles = len(article_data)
    fig, axes = plt.subplots(n_articles, 1, figsize=(14, 4 * n_articles))

    if n_articles == 1:
        axes = [axes]

    fig.suptitle('Per-Article Performance Over Time', fontsize=16, fontweight='bold')

    for idx, (article_name, data) in enumerate(sorted(article_data.items())):
        ax = axes[idx]

        # Plot metrics
        ax.plot(data['timestamps'], data['entity_sims'],
               marker='o', linestyle='-', linewidth=2, markersize=6,
               color='#2E86AB', label='Entity Similarity')
        ax.plot(data['timestamps'], data['crime_sims'],
               marker='s', linestyle='-', linewidth=2, markersize=6,
               color='#A23B72', label='Crime Similarity')

        # Thresholds
        ax.axhline(y=config.ENTITY_SIMILARITY_THRESHOLD, color='#2E86AB',
                  linestyle='--', linewidth=1, alpha=0.5)
        ax.axhline(y=config.CRIME_SIMILARITY_THRESHOLD, color='#A23B72',
                  linestyle='--', linewidth=1, alpha=0.5)

        # Formatting
        ax.set_title(f'{article_name}', fontsize=12, fontweight='bold')
        ax.set_ylabel('Similarity', fontsize=10)
        ax.legend(loc='best', fontsize=9)
        ax.grid(True, alpha=0.3)
        ax.set_ylim([0, 1.05])
        ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda y, _: f'{y:.0%}'))

        if idx == len(article_data) - 1:
            ax.set_xlabel('Test Run Date', fontsize=10, fontweight='bold')

        ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d %H:%M'))
        plt.setp(ax.xaxis.get_majorticklabels(), rotation=45, ha='right')

    plt.tight_layout()

    # Save or show
    if output_path:
        plt.savefig(output_path, dpi=300, bbox_inches='tight')
        print(f"Article breakdown plot saved to: {output_path}")
    else:
        plt.show()


def print_summary(results: List[Dict]):
    """Print a summary of test results."""
    if not results:
        print("No results to summarize!")
        return

    timestamps, entity_sims, crime_sims = extract_metrics(results)

    print(f"\n{'='*60}")
    print(f"Performance Test Summary")
    print(f"{'='*60}")
    print(f"Total test runs: {len(results)}")
    print(f"Date range: {timestamps[0].strftime('%Y-%m-%d %H:%M')} to {timestamps[-1].strftime('%Y-%m-%d %H:%M')}")
    print()

    print("Entity Similarity:")
    print(f"  Average: {np.mean(entity_sims):.2%}")
    print(f"  Min: {np.min(entity_sims):.2%}")
    print(f"  Max: {np.max(entity_sims):.2%}")
    print(f"  Std Dev: {np.std(entity_sims):.2%}")
    print()

    print("Crime Similarity:")
    print(f"  Average: {np.mean(crime_sims):.2%}")
    print(f"  Min: {np.min(crime_sims):.2%}")
    print(f"  Max: {np.max(crime_sims):.2%}")
    print(f"  Std Dev: {np.std(crime_sims):.2%}")
    print()

    # Count passes/failures
    entity_passes = sum(1 for s in entity_sims if s >= config.ENTITY_SIMILARITY_THRESHOLD)
    crime_passes = sum(1 for s in crime_sims if s >= config.CRIME_SIMILARITY_THRESHOLD)

    print(f"Pass Rate:")
    print(f"  Entity: {entity_passes}/{len(entity_sims)} ({entity_passes/len(entity_sims):.0%})")
    print(f"  Crime: {crime_passes}/{len(crime_sims)} ({crime_passes/len(crime_sims):.0%})")
    print(f"{'='*60}\n")


def main():
    """Main function to generate elbow plots."""
    import argparse

    parser = argparse.ArgumentParser(
        description="Generate elbow plots for performance test results"
    )
    parser.add_argument(
        '--output-dir', '-o',
        type=Path,
        default=config.DAILY_OUTPUTS_DIR,
        help='Directory to save plots (default: daily_outputs/)'
    )
    parser.add_argument(
        '--type', '-t',
        choices=['separate', 'combined', 'articles', 'all'],
        default='all',
        help='Type of plot to generate (default: all)'
    )
    parser.add_argument(
        '--show',
        action='store_true',
        help='Show plots interactively instead of saving'
    )

    args = parser.parse_args()

    # Load test results
    log_path = config.LOGS_DIR / "test_results.jsonl"
    results = load_test_results(log_path)

    if not results:
        print(f"\n⚠️  No test results found at {log_path}")
        print("Run performance tests first: python test_performance/run_test.py")
        return

    # Print summary
    print_summary(results)

    # Prepare output directory
    if not args.show:
        args.output_dir.mkdir(parents=True, exist_ok=True)
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')

    # Generate plots
    if args.type in ['separate', 'all']:
        output_path = None if args.show else args.output_dir / f'performance_trends_{timestamp}.png'
        plot_performance_trends(results, output_path)

    if args.type in ['combined', 'all']:
        output_path = None if args.show else args.output_dir / f'combined_metrics_{timestamp}.png'
        plot_combined_metrics(results, output_path)

    if args.type in ['articles', 'all']:
        output_path = None if args.show else args.output_dir / f'article_breakdown_{timestamp}.png'
        plot_article_breakdown(results, output_path)

    if not args.show:
        print(f"\n✅ Plots saved to: {args.output_dir}")


if __name__ == "__main__":
    main()
