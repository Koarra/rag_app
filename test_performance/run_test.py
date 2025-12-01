"""
Performance testing script for step5_analyze_risks.py

Compares current LLM outputs against reference outputs for test articles.
Calculates similarity metrics and logs results.
"""

import sys
import json
import subprocess
from datetime import datetime
from pathlib import Path

# Add parent directory to path to import step5
sys.path.insert(0, str(Path(__file__).parent.parent))

from test_performance.compare_outputs import compare_outputs
import test_performance.config as config


def run_step5_for_article(article_folder: Path) -> dict:
    """
    Run step5_analyze_risks.py for a specific article's output folder.

    Args:
        article_folder: Path to folder containing entity outputs

    Returns:
        Dictionary with risk assessment results
    """
    print(f"  Running step5 for {article_folder.name}...")

    # Run step5_analyze_risks.py
    result = subprocess.run(
        ["python", "step5_analyze_risks.py", str(article_folder)],
        capture_output=True,
        text=True,
        cwd=Path(__file__).parent.parent
    )

    if result.returncode != 0:
        print(f"  ERROR running step5: {result.stderr}")
        return None

    # Load the generated risk_assessment.json
    risk_file = article_folder / "risk_assessment.json"
    if not risk_file.exists():
        print(f"  ERROR: risk_assessment.json not found at {risk_file}")
        return None

    with open(risk_file, 'r', encoding='utf-8') as f:
        return json.load(f)


def run_performance_test(verbose: bool = True):
    """
    Run performance test for all test articles.

    Args:
        verbose: If True, print detailed progress

    Returns:
        Dictionary with test summary and results
    """
    timestamp = datetime.now().isoformat()
    all_results = []

    if verbose:
        print(f"\n{'='*60}")
        print(f"Starting Performance Test: {timestamp}")
        print(f"{'='*60}\n")

    for article_name in config.TEST_ARTICLES:
        if verbose:
            print(f"Processing {article_name}...")

        # Find the article's output folder in test_articles
        article_folder = config.TEST_ARTICLES_DIR / article_name / "outputs"

        if not article_folder.exists():
            print(f"  WARNING: Folder not found: {article_folder}")
            print(f"  Skipping {article_name}")
            continue

        # Run step5 to generate current output
        current_output = run_step5_for_article(article_folder)

        if current_output is None:
            print(f"  WARNING: Failed to generate output for {article_name}")
            continue

        # Load reference output
        reference_path = config.REFERENCE_OUTPUTS_DIR / f"{article_name}.json"
        if not reference_path.exists():
            print(f"  WARNING: Reference not found: {reference_path}")
            print(f"  Skipping {article_name}")
            continue

        with open(reference_path, 'r', encoding='utf-8') as f:
            reference_output = json.load(f)

        # Save current output with timestamp for debugging
        output_filename = f"{article_name}_{timestamp.replace(':', '-')}.json"
        output_path = config.DAILY_OUTPUTS_DIR / output_filename
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(current_output, f, indent=2)

        if verbose:
            print(f"  Saved current output to: {output_path}")

        # Compare outputs
        comparison = compare_outputs(reference_output, current_output)

        result_entry = {
            'article': article_name,
            'timestamp': timestamp,
            **comparison
        }
        all_results.append(result_entry)

        if verbose:
            print(f"  ✓ Entity similarity: {comparison['entity_similarity']:.2%}")
            print(f"  ✓ Crime similarity: {comparison['crime_similarity']:.2%}")
            print(f"    - Matched entities: {comparison['entity_metrics']['matched_count']}")
            print(f"    - Missing entities: {comparison['entity_metrics']['missing_count']}")
            print(f"    - Extra entities: {comparison['entity_metrics']['extra_count']}")

            if comparison['crime_details']:
                print(f"    - Crime discrepancies: {len(comparison['crime_details'])} entities")
            print()

    if not all_results:
        print("\n⚠️  No articles were successfully processed!")
        return None

    # Calculate aggregate metrics
    avg_entity = sum(r['entity_similarity'] for r in all_results) / len(all_results)
    avg_crime = sum(r['crime_similarity'] for r in all_results) / len(all_results)

    # Check if passed
    entity_passed = avg_entity >= config.ENTITY_SIMILARITY_THRESHOLD
    crime_passed = avg_crime >= config.CRIME_SIMILARITY_THRESHOLD
    overall_passed = entity_passed and crime_passed

    summary = {
        'timestamp': timestamp,
        'test_config': {
            'entity_threshold': config.ENTITY_SIMILARITY_THRESHOLD,
            'crime_threshold': config.CRIME_SIMILARITY_THRESHOLD,
            'articles_tested': len(all_results)
        },
        'aggregate_metrics': {
            'avg_entity_similarity': avg_entity,
            'avg_crime_similarity': avg_crime,
            'entity_passed': entity_passed,
            'crime_passed': crime_passed,
            'overall_passed': overall_passed
        },
        'individual_results': all_results
    }

    # Log results
    log_path = config.LOGS_DIR / "test_results.jsonl"
    with open(log_path, 'a', encoding='utf-8') as f:
        f.write(json.dumps(summary) + '\n')

    if verbose:
        print(f"{'='*60}")
        print(f"Test Summary")
        print(f"{'='*60}")
        print(f"Articles tested: {len(all_results)}")
        print(f"Average entity similarity: {avg_entity:.2%} (threshold: {config.ENTITY_SIMILARITY_THRESHOLD:.0%})")
        print(f"Average crime similarity: {avg_crime:.2%} (threshold: {config.CRIME_SIMILARITY_THRESHOLD:.0%})")
        print()

        if overall_passed:
            print("✅ TEST PASSED - All thresholds met!")
        else:
            print("❌ TEST FAILED - Below threshold!")
            if not entity_passed:
                print(f"   - Entity detection: {avg_entity:.2%} < {config.ENTITY_SIMILARITY_THRESHOLD:.0%}")
            if not crime_passed:
                print(f"   - Crime classification: {avg_crime:.2%} < {config.CRIME_SIMILARITY_THRESHOLD:.0%}")

        print(f"\nResults logged to: {log_path}")
        print(f"{'='*60}\n")

    return summary


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Run performance test for step5_analyze_risks.py")
    parser.add_argument("--quiet", "-q", action="store_true", help="Suppress detailed output")
    args = parser.parse_args()

    result = run_performance_test(verbose=not args.quiet)

    if result is None:
        sys.exit(1)
    elif not result['aggregate_metrics']['overall_passed']:
        sys.exit(1)
    else:
        sys.exit(0)
