"""
MAIN SCRIPT - Run all steps in sequence

Usage: python run_pipeline.py <input_document.pdf> [output_folder] [--skip-grouping]

This script runs all 6 steps automatically:
1. Extract text and summarize
2. Extract entities (persons & companies)
3. Describe each entity
4. Group similar entities (deduplication)
5. Analyze risks (financial crimes)
6. Extract relationships and create knowledge graph

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
        print("Usage: python run_pipeline.py <input_document.pdf> [output_folder] [--skip-grouping]")
        print("\nExample: python run_pipeline.py contract.pdf")
        print("Example: python run_pipeline.py contract.pdf ./outputs")
        print("Example: python run_pipeline.py contract.pdf ./outputs --skip-grouping")
        sys.exit(1)

    input_file = sys.argv[1]

    # Determine output folder and skip_grouping flag
    skip_grouping = "--skip-grouping" in sys.argv
    output_folder = None

    for arg in sys.argv[2:]:
        if arg != "--skip-grouping":
            output_folder = Path(arg)
            break

    if output_folder is None:
        # Default output folder based on input filename
        output_folder = Path("outputs") / Path(input_file).stem

    output_folder.mkdir(parents=True, exist_ok=True)

    # Check file exists
    if not Path(input_file).exists():
        print(f"Error: File not found: {input_file}")
        sys.exit(1)

    print("\n" + "="*60)
    print("DOCUMENT PROCESSING PIPELINE")
    print("="*60)
    print(f"Input file: {input_file}")
    print(f"Output folder: {output_folder}")
    print("Using Azure OpenAI with DefaultAzureCredential")

    if skip_grouping:
        print(f"\nThis will run 5 steps (skipping entity grouping):")
        print("1. Extract text and summarize")
        print("2. Extract entities (persons & companies)")
        print("3. Describe each entity")
        print("4. [SKIPPED] Group similar entities")
        print("5. Analyze risks (financial crimes)")
        print("6. Extract relationships and create knowledge graph")
    else:
        print(f"\nThis will run 6 steps:")
        print("1. Extract text and summarize")
        print("2. Extract entities (persons & companies)")
        print("3. Describe each entity")
        print("4. Group similar entities (deduplication)")
        print("5. Analyze risks (financial crimes)")
        print("6. Extract relationships and create knowledge graph")

    print("="*60)

    # Run all steps
    run_step("step1_summarize.py", [input_file, str(output_folder)])
    run_step("step2_extract_entities.py", [str(output_folder)])
    run_step("step3_describe_entities.py", [str(output_folder)])

    if not skip_grouping:
        run_step("step4_group_entities.py", [str(output_folder)])

    run_step("step5_analyze_risks.py", [str(output_folder)])
    run_step("step6_extract_relationships.py", [str(output_folder)])

    # Show final results
    print("\n" + "="*60)
    print("ALL STEPS COMPLETE!")
    print("="*60)
    print("\nGenerated files:")
    print("  - extracted_text.txt                       (raw document text)")
    print("  - summary.json                             (document summary)")
    print("  - entities.json                            (persons & companies)")
    print("  - entity_descriptions.json                 (detailed entity info)")

    if not skip_grouping:
        print("  - dict_unique_grouped_entity_summary.json (deduplicated entities)")

    print("  - risk_assessment.json                     (risk analysis)")
    print("  - entity_relationships.json                (all entity relationships)")
    print("  - entity_relationships_filtered.json       (meaningful relationships only)")
    print("  - graph_elements.json                      (knowledge graph for visualization)")

    print("\n" + "="*60 + "\n")


if __name__ == "__main__":
    main()
