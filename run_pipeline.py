"""
MAIN SCRIPT - Run all steps in sequence

Usage: python run_pipeline.py <input_document.pdf> [--group-entities]

This script runs all steps automatically:
1. Extract text and summarize
2. Extract entities (persons & companies)
3. Describe each entity
4. Analyze risks (money laundering & sanctions evasion)
5. Group similar entities (optional, use --group-entities flag)
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
        print("Usage: python run_pipeline.py <input_document.pdf> [--group-entities]")
        print("\nExample: python run_pipeline.py contract.pdf")
        print("Example: python run_pipeline.py contract.pdf --group-entities")
        sys.exit(1)

    input_file = sys.argv[1]
    group_entities = "--group-entities" in sys.argv

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

    if group_entities:
        print(f"\nThis will run 5 steps:")
        print("1. Extract text and summarize")
        print("2. Extract entities (persons & companies)")
        print("3. Describe each entity")
        print("4. Analyze risks (money laundering & sanctions evasion)")
        print("5. Group similar entities together")
    else:
        print(f"\nThis will run 4 steps:")
        print("1. Extract text and summarize")
        print("2. Extract entities (persons & companies)")
        print("3. Describe each entity")
        print("4. Analyze risks (money laundering & sanctions evasion)")
        print("\nTip: Use --group-entities flag to merge duplicate entities")

    print("="*60)

    # Run all steps
    run_step("step1_summarize.py", [input_file, api_key])
    run_step("step2_extract_entities.py", [api_key])
    run_step("step3_describe_entities.py", [api_key])
    run_step("step4_analyze_risks.py", [api_key])

    if group_entities:
        run_step("step5_group_entities.py", [api_key])

    # Show final results
    print("\n" + "="*60)
    print("ALL STEPS COMPLETE!")
    print("="*60)
    print("\nGenerated files:")
    print("  - extracted_text.txt        (raw document text)")
    print("  - summary.json              (document summary)")
    print("  - entities.json             (persons & companies)")
    print("  - entity_descriptions.json  (detailed entity info)")
    print("  - risk_assessment.json      (risk analysis)")

    if group_entities:
        print("  - grouped_entities.json     (deduplicated entities)")

    print("\n" + "="*60 + "\n")


if __name__ == "__main__":
    main()
