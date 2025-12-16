"""
Create sample test data for demonstrating the elbow plot functionality.
"""

import json
from datetime import datetime, timedelta
from pathlib import Path
import random
import sys

sys.path.insert(0, str(Path(__file__).parent.parent))
import test_performance.config as config


def generate_sample_results(num_runs: int = 10) -> None:
    """
    Generate sample test results with realistic performance variations.

    Args:
        num_runs: Number of test runs to simulate
    """
    # Ensure logs directory exists
    config.LOGS_DIR.mkdir(parents=True, exist_ok=True)

    log_path = config.LOGS_DIR / "test_results.jsonl"

    # Start from 10 days ago
    start_time = datetime.now() - timedelta(days=10)

    # Simulate a performance degradation around run 5, then recovery
    base_entity_sim = 0.88
    base_crime_sim = 0.85

    print(f"Generating {num_runs} sample test results...")
    print(f"Output: {log_path}\n")

    for run_idx in range(num_runs):
        # Time progression (roughly one per day with some variation)
        timestamp = start_time + timedelta(
            days=run_idx,
            hours=random.randint(0, 23),
            minutes=random.randint(0, 59)
        )

        # Simulate performance changes
        if run_idx < 4:
            # Good performance initially
            entity_sim = base_entity_sim + random.uniform(-0.02, 0.03)
            crime_sim = base_crime_sim + random.uniform(-0.02, 0.03)
        elif run_idx < 7:
            # Performance drop (elbow point around run 4-5)
            entity_sim = base_entity_sim - 0.10 + random.uniform(-0.03, 0.02)
            crime_sim = base_crime_sim - 0.08 + random.uniform(-0.03, 0.02)
        else:
            # Recovery
            entity_sim = base_entity_sim - 0.02 + random.uniform(-0.02, 0.04)
            crime_sim = base_crime_sim - 0.01 + random.uniform(-0.02, 0.04)

        # Clamp values
        entity_sim = max(0.0, min(1.0, entity_sim))
        crime_sim = max(0.0, min(1.0, crime_sim))

        # Generate individual article results
        individual_results = []
        for article_idx, article_name in enumerate(config.TEST_ARTICLES):
            # Add some per-article variation
            article_entity_sim = entity_sim + random.uniform(-0.05, 0.05)
            article_crime_sim = crime_sim + random.uniform(-0.05, 0.05)

            # Clamp
            article_entity_sim = max(0.0, min(1.0, article_entity_sim))
            article_crime_sim = max(0.0, min(1.0, article_crime_sim))

            individual_results.append({
                'article': article_name,
                'timestamp': timestamp.isoformat(),
                'entity_similarity': article_entity_sim,
                'crime_similarity': article_crime_sim,
                'entity_metrics': {
                    'matched_count': random.randint(15, 20),
                    'missing_count': random.randint(0, 3),
                    'extra_count': random.randint(0, 2),
                    'reference_total': random.randint(17, 21),
                    'current_total': random.randint(16, 22),
                    'missing_entities': [],
                    'extra_entities': []
                },
                'crime_details': []
            })

        # Create summary entry
        summary = {
            'timestamp': timestamp.isoformat(),
            'test_config': {
                'entity_threshold': config.ENTITY_SIMILARITY_THRESHOLD,
                'crime_threshold': config.CRIME_SIMILARITY_THRESHOLD,
                'articles_tested': len(config.TEST_ARTICLES)
            },
            'aggregate_metrics': {
                'avg_entity_similarity': entity_sim,
                'avg_crime_similarity': crime_sim,
                'entity_passed': entity_sim >= config.ENTITY_SIMILARITY_THRESHOLD,
                'crime_passed': crime_sim >= config.CRIME_SIMILARITY_THRESHOLD,
                'overall_passed': (
                    entity_sim >= config.ENTITY_SIMILARITY_THRESHOLD and
                    crime_sim >= config.CRIME_SIMILARITY_THRESHOLD
                )
            },
            'individual_results': individual_results
        }

        # Write to log
        with open(log_path, 'a', encoding='utf-8') as f:
            f.write(json.dumps(summary) + '\n')

        status = "✅ PASS" if summary['aggregate_metrics']['overall_passed'] else "❌ FAIL"
        print(f"Run {run_idx + 1:2d} ({timestamp.strftime('%Y-%m-%d')}): "
              f"Entity: {entity_sim:.2%}, Crime: {crime_sim:.2%} - {status}")

    print(f"\n✅ Sample data created: {log_path}")
    print(f"\nNow run: python test_performance/plot_elbow.py")


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Generate sample test data")
    parser.add_argument(
        '--runs', '-n',
        type=int,
        default=10,
        help='Number of test runs to generate (default: 10)'
    )
    parser.add_argument(
        '--clear',
        action='store_true',
        help='Clear existing log file before generating'
    )

    args = parser.parse_args()

    # Clear log if requested
    if args.clear:
        log_path = config.LOGS_DIR / "test_results.jsonl"
        if log_path.exists():
            log_path.unlink()
            print(f"Cleared existing log file: {log_path}\n")

    generate_sample_results(args.runs)
