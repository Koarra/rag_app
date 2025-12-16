"""
Analyze test results to recommend optimal thresholds.
Uses statistical analysis to justify threshold values for KPIs.
"""

import json
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).parent.parent))
import test_performance.config as config

# Load test results
log_path = config.LOGS_DIR / "test_results.json"

if not log_path.exists():
    print(f"No test results found at {log_path}")
    print("Run: python test_performance/create_sample_data.py")
    sys.exit(1)

# Read data
entity_scores = []
crime_scores = []

with open(log_path, 'r') as f:
    for line in f:
        if line.strip():
            result = json.loads(line)
            entity_scores.append(result['aggregate_metrics']['avg_entity_similarity'])
            crime_scores.append(result['aggregate_metrics']['avg_crime_similarity'])

if not entity_scores:
    print("No data to analyze!")
    sys.exit(1)

# Calculate statistics
def analyze_metric(scores, name, current_threshold):
    mean = sum(scores) / len(scores)
    variance = sum((x - mean) ** 2 for x in scores) / len(scores)
    std_dev = variance ** 0.5

    sorted_scores = sorted(scores)
    n = len(sorted_scores)

    # Percentiles
    p10 = sorted_scores[int(n * 0.10)]
    p25 = sorted_scores[int(n * 0.25)]
    p50 = sorted_scores[int(n * 0.50)]  # Median
    p75 = sorted_scores[int(n * 0.75)]
    p90 = sorted_scores[int(n * 0.90)]

    min_score = min(scores)
    max_score = max(scores)

    print(f"\n{'='*60}")
    print(f"{name.upper()}")
    print(f"{'='*60}")
    print(f"Sample size: {n} test runs")
    print()

    print("DESCRIPTIVE STATISTICS:")
    print(f"  Mean:              {mean:.1%}")
    print(f"  Median (P50):      {p50:.1%}")
    print(f"  Std Deviation:     {std_dev:.1%}")
    print(f"  Min:               {min_score:.1%}")
    print(f"  Max:               {max_score:.1%}")
    print()

    print("PERCENTILES:")
    print(f"  P10 (10th %ile):   {p10:.1%}")
    print(f"  P25 (25th %ile):   {p25:.1%}")
    print(f"  P50 (median):      {p50:.1%}")
    print(f"  P75 (75th %ile):   {p75:.1%}")
    print(f"  P90 (90th %ile):   {p90:.1%}")
    print()

    print("THRESHOLD RECOMMENDATIONS:")
    print()

    # Conservative (catches most issues but may have false alarms)
    conservative = mean - std_dev
    print(f"  Conservative (mean - 1σ): {conservative:.1%}")
    print(f"    → Use if you want to catch most performance degradations")
    print(f"    → Accepts ~84% of historical runs")
    print()

    # Moderate (balanced approach)
    moderate = p25
    print(f"  Moderate (25th percentile): {moderate:.1%}")
    print(f"    → Use for balanced sensitivity")
    print(f"    → Accepts ~75% of historical runs")
    print()

    # Lenient (only flags major issues)
    lenient = p10
    print(f"  Lenient (10th percentile): {lenient:.1%}")
    print(f"    → Use if you only want to catch major regressions")
    print(f"    → Accepts ~90% of historical runs")
    print()

    print(f"CURRENT THRESHOLD: {current_threshold:.1%}")

    # Analysis
    passes = sum(1 for s in scores if s >= current_threshold)
    pass_rate = passes / len(scores)

    print(f"  Pass rate with current threshold: {passes}/{n} ({pass_rate:.0%})")

    if current_threshold > p90:
        print(f"  ⚠️  Very strict - only {pass_rate:.0%} of runs pass")
        print(f"  💡 Consider lowering to ~{p75:.1%} for more realistic expectations")
    elif current_threshold > p75:
        print(f"  ✅ Moderately strict - good balance")
    elif current_threshold > p50:
        print(f"  ✅ Moderate - most runs pass")
    elif current_threshold > p25:
        print(f"  ⚠️  Lenient - may miss some regressions")
        print(f"  💡 Consider raising to ~{p50:.1%} for better detection")
    else:
        print(f"  ⚠️  Very lenient - will miss many regressions")
        print(f"  💡 Consider raising to ~{p50:.1%} or {p75:.1%}")

    return {
        'mean': mean,
        'std_dev': std_dev,
        'median': p50,
        'p10': p10,
        'p25': p25,
        'p75': p75,
        'p90': p90,
        'conservative': conservative,
        'moderate': moderate,
        'lenient': lenient
    }

# Analyze both metrics
entity_stats = analyze_metric(entity_scores, "Entity Detection",
                               config.ENTITY_SIMILARITY_THRESHOLD)
crime_stats = analyze_metric(crime_scores, "Crime Classification",
                              config.CRIME_SIMILARITY_THRESHOLD)

# Overall recommendation
print(f"\n{'='*60}")
print("RECOMMENDATION SUMMARY")
print(f"{'='*60}")
print()
print("To update thresholds, edit test_performance/config.py:")
print()
print("# Suggested values based on statistical analysis:")
print(f"ENTITY_SIMILARITY_THRESHOLD = {entity_stats['moderate']:.2f}  # Moderate (P25)")
print(f"CRIME_SIMILARITY_THRESHOLD = {crime_stats['moderate']:.2f}   # Moderate (P25)")
print()
print("Or for more conservative thresholds:")
print(f"ENTITY_SIMILARITY_THRESHOLD = {entity_stats['conservative']:.2f}  # Conservative (mean - 1σ)")
print(f"CRIME_SIMILARITY_THRESHOLD = {crime_stats['conservative']:.2f}   # Conservative (mean - 1σ)")
print()
print("Or for lenient thresholds (catch only major issues):")
print(f"ENTITY_SIMILARITY_THRESHOLD = {entity_stats['lenient']:.2f}  # Lenient (P10)")
print(f"CRIME_SIMILARITY_THRESHOLD = {crime_stats['lenient']:.2f}   # Lenient (P10)")
print(f"\n{'='*60}\n")
