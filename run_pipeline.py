"""
MAIN SCRIPT - Run all steps in sequence

Usage: python run_pipeline.py <input_document.pdf> [--skip-grouping]

This script runs all 5 steps automatically:
1. Extract text and summarize
2. Extract entities (persons & companies)
3. Describe each entity
4. Group similar entities (deduplication)
5. Analyze risks (money laundering & sanctions evasion)

Use --skip-grouping to skip step 4 (entity grouping)
"""

import sys
import subprocess
from pathlib import Path


def run_step(script_name, args):
    """Run a step script"""
    print(f"\n{'='*60}")
    print(f"Running {script_name}...")
    print(f"{'='*60}\n")

    cmd = ["python", script_name] + args
    result = subprocess.run(cmd, capture_output=False, text=True)

    if result.returncode != 0:
        print(f"\n❌ Error in {script_name}")
        sys.exit(1)

    print(f"\n✓ {script_name} completed successfully")


def main():
    if len(sys.argv) < 2:
        print("Usage: python run_pipeline.py <input_document.pdf> [--skip-grouping]")
        print("\nExample: python run_pipeline.py contract.pdf")
        print("Example: python run_pipeline.py contract.pdf --skip-grouping")
        sys.exit(1)

    input_file = sys.argv[1]
    skip_grouping = "--skip-grouping" in sys.argv

    # Check file exists
    if not Path(input_file).exists():
        print(f"Error: File not found: {input_file}")
        sys.exit(1)

    # Get API key
    api_key = input("Enter your OpenAI API key: ")

    print("\n" + "="*60)
    print("DOCUMENT PROCESSING PIPELINE")
    print("="*60)
    print(f"Input file: {input_file}")

    if skip_grouping:
        print(f"\nThis will run 4 steps (skipping entity grouping):")
        print("1. Extract text and summarize")
        print("2. Extract entities (persons & companies)")
        print("3. Describe each entity")
        print("4. [SKIPPED] Group similar entities")
        print("5. Analyze risks (money laundering & sanctions evasion)")
    else:
        print(f"\nThis will run 5 steps:")
        print("1. Extract text and summarize")
        print("2. Extract entities (persons & companies)")
        print("3. Describe each entity")
        print("4. Group similar entities (deduplication)")
        print("5. Analyze risks (money laundering & sanctions evasion)")

    print("="*60)

    # Run all steps
    run_step("step1_summarize.py", [input_file, api_key])
    run_step("step2_extract_entities.py", [api_key])
    run_step("step3_describe_entities.py", [api_key])

    if not skip_grouping:
        run_step("step4_group_entities.py", [api_key])

    run_step("step5_analyze_risks.py", [api_key])

    # Show final results
    print("\n" + "="*60)
    print("ALL STEPS COMPLETE!")
    print("="*60)
    print("\nGenerated files:")
    print("  - extracted_text.txt        (raw document text)")
    print("  - summary.json              (document summary)")
    print("  - entities.json             (persons & companies)")
    print("  - entity_descriptions.json  (detailed entity info)")

    if not skip_grouping:
        print("  - grouped_entities.json     (deduplicated entities)")

    print("  - risk_assessment.json      (risk analysis)")

    print("\n" + "="*60 + "\n")


if __name__ == "__main__":
    main()
