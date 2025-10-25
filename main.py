#!/usr/bin/env python3
"""
Main Orchestrator for Document Processing Pipeline
Processes documents through 4 stages:
1. Document Extraction & Summarization
2. Entity Extraction
3. Entity Description Generation
4. Risk Analysis & Crime Flagging
"""
import sys
import argparse
from pathlib import Path
from typing import Optional
import time

from src.utils import Config
from src.document_processor import DocumentProcessor
from src.entity_extractor import EntityExtractor
from src.entity_analyzer import EntityAnalyzer
from src.risk_analyzer import RiskAnalyzer


class DocumentPipeline:
    """Complete document processing pipeline"""

    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key
        self.doc_processor = DocumentProcessor(api_key)
        self.entity_extractor = EntityExtractor(api_key)
        self.entity_analyzer = EntityAnalyzer(api_key)
        self.risk_analyzer = RiskAnalyzer(api_key)

    def process_document(
        self,
        file_path: Path,
        skip_stages: list = None
    ) -> dict:
        """
        Process a single document through all stages

        Args:
            file_path: Path to the document file
            skip_stages: Optional list of stage numbers to skip (1-4)

        Returns:
            Dictionary with all processing results
        """
        skip_stages = skip_stages or []

        print(f"\n{'#'*60}")
        print(f"# PROCESSING DOCUMENT: {file_path.name}")
        print(f"{'#'*60}\n")

        start_time = time.time()
        results = {
            'document_name': file_path.name,
            'file_path': str(file_path)
        }

        # Stage 1: Document Extraction & Summarization
        if 1 not in skip_stages:
            try:
                text, summaries = self.doc_processor.process(file_path)
                results['text'] = text
                results['summaries'] = summaries
            except Exception as e:
                print(f"ERROR in Stage 1: {e}")
                return results
        else:
            print("Skipping Stage 1 - loading from previous run...")
            # Try to load from previous run
            text_file = Config.EXTRACTED_TEXT_DIR / f"{file_path.stem}_extracted.txt"
            if text_file.exists():
                with open(text_file, 'r', encoding='utf-8') as f:
                    results['text'] = f.read()
                text = results['text']
            else:
                print("ERROR: Cannot skip Stage 1 - no previous extraction found")
                return results

        # Stage 2: Entity Extraction
        if 2 not in skip_stages:
            try:
                entities = self.entity_extractor.process(
                    results['text'],
                    file_path.name,
                    file_path
                )
                results['entities'] = entities
            except Exception as e:
                print(f"ERROR in Stage 2: {e}")
                return results
        else:
            print("Skipping Stage 2 - loading from previous run...")
            entities_file = Config.ENTITIES_DIR / f"{file_path.stem}_entities.json"
            if entities_file.exists():
                import json
                with open(entities_file, 'r') as f:
                    results['entities'] = json.load(f)
            else:
                print("ERROR: Cannot skip Stage 2 - no previous extraction found")
                return results

        # Stage 3: Entity Analysis
        if 3 not in skip_stages:
            try:
                entity_descriptions = self.entity_analyzer.process(
                    results['entities'],
                    results['text'],
                    file_path.name,
                    file_path
                )
                results['entity_descriptions'] = entity_descriptions
            except Exception as e:
                print(f"ERROR in Stage 3: {e}")
                return results
        else:
            print("Skipping Stage 3 - loading from previous run...")
            desc_file = Config.DESCRIPTIONS_DIR / f"{file_path.stem}_entity_descriptions.json"
            if desc_file.exists():
                import json
                with open(desc_file, 'r') as f:
                    results['entity_descriptions'] = json.load(f)
            else:
                print("ERROR: Cannot skip Stage 3 - no previous descriptions found")
                return results

        # Stage 4: Risk Analysis
        if 4 not in skip_stages:
            try:
                risk_report = self.risk_analyzer.process(
                    results['text'],
                    results['entities'],
                    results['entity_descriptions'],
                    file_path.name,
                    file_path
                )
                results['risk_report'] = risk_report
            except Exception as e:
                print(f"ERROR in Stage 4: {e}")
                return results

        elapsed_time = time.time() - start_time

        print(f"\n{'#'*60}")
        print(f"# PROCESSING COMPLETE")
        print(f"# Total time: {elapsed_time:.2f} seconds")
        print(f"{'#'*60}\n")

        self._print_summary(results)

        return results

    def process_multiple_documents(
        self,
        file_paths: list,
        skip_stages: list = None
    ) -> list:
        """
        Process multiple documents

        Args:
            file_paths: List of file paths
            skip_stages: Optional list of stage numbers to skip

        Returns:
            List of results dictionaries
        """
        all_results = []

        for i, file_path in enumerate(file_paths, 1):
            print(f"\n{'='*60}")
            print(f"Processing document {i}/{len(file_paths)}")
            print(f"{'='*60}")

            result = self.process_document(Path(file_path), skip_stages)
            all_results.append(result)

        return all_results

    def _print_summary(self, results: dict):
        """Print processing summary"""
        print("\n" + "="*60)
        print("PROCESSING SUMMARY")
        print("="*60)

        if 'summaries' in results:
            print(f"\n📄 Executive Summary:")
            print(f"{results['summaries'].get('executive_summary', 'N/A')}")

        if 'entities' in results:
            print(f"\n👤 Entities Found:")
            print(f"  Persons: {len(results['entities'].get('persons', []))}")
            print(f"  Companies: {len(results['entities'].get('companies', []))}")

        if 'risk_report' in results:
            risk = results['risk_report']
            doc_risk = risk.get('document_risk_assessment', {})
            summary = risk.get('entity_risk_summary', {})

            print(f"\n⚠️  Risk Assessment:")
            print(f"  Overall Risk: {doc_risk.get('overall_risk_level', 'N/A').upper()}")
            print(f"  Money Laundering Risk: {doc_risk.get('money_laundering_risk', 'N/A').upper()}")
            print(f"  Sanctions Evasion Risk: {doc_risk.get('sanctions_evasion_risk', 'N/A').upper()}")
            print(f"  Flagged Entities: {summary.get('total_flagged', 0)}")

        print("\n" + "="*60 + "\n")


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(
        description='Process documents through 4-stage analysis pipeline',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Process a single document through all stages
  python main.py document.pdf

  # Process multiple documents
  python main.py doc1.pdf doc2.docx doc3.pdf

  # Skip certain stages (use previous results)
  python main.py document.pdf --skip-stages 1 2

  # Set custom API key
  python main.py document.pdf --api-key sk-...

Stages:
  1. Document Extraction & Summarization
  2. Entity Extraction (persons & companies)
  3. Entity Description Generation
  4. Risk Analysis (money laundering, sanctions evasion)

Output:
  All results are saved in the outputs/ directory:
  - outputs/extracted_text/     - Extracted document text
  - outputs/summaries/           - Document summaries
  - outputs/entities/            - Extracted entities
  - outputs/entity_descriptions/ - Entity descriptions
  - outputs/risk_flags/          - Risk assessment reports
        """
    )

    parser.add_argument(
        'files',
        nargs='+',
        help='One or more document files to process (PDF or DOCX)'
    )

    parser.add_argument(
        '--api-key',
        help='OpenAI API key (or set OPENAI_API_KEY environment variable)'
    )

    parser.add_argument(
        '--skip-stages',
        nargs='+',
        type=int,
        choices=[1, 2, 3, 4],
        help='Stage numbers to skip (will use previous results)'
    )

    parser.add_argument(
        '--stage-only',
        type=int,
        choices=[1, 2, 3, 4],
        help='Run only a specific stage (requires previous stages completed)'
    )

    args = parser.parse_args()

    # Ensure output directories exist
    Config.ensure_directories()

    # Validate files exist
    file_paths = []
    for file_path in args.files:
        path = Path(file_path)
        if not path.exists():
            print(f"ERROR: File not found: {file_path}")
            sys.exit(1)
        if path.suffix.lower() not in ['.pdf', '.docx']:
            print(f"WARNING: Unsupported file type: {file_path} (supported: .pdf, .docx)")
            continue
        file_paths.append(path)

    if not file_paths:
        print("ERROR: No valid files to process")
        sys.exit(1)

    # Determine which stages to skip
    skip_stages = args.skip_stages or []

    if args.stage_only:
        # Run only specific stage
        all_stages = [1, 2, 3, 4]
        skip_stages = [s for s in all_stages if s != args.stage_only]

    # Create pipeline
    pipeline = DocumentPipeline(api_key=args.api_key)

    # Process documents
    try:
        if len(file_paths) == 1:
            pipeline.process_document(file_paths[0], skip_stages)
        else:
            pipeline.process_multiple_documents(file_paths, skip_stages)

        print("\n✅ All documents processed successfully!")
        print(f"📁 Results saved in: {Config.OUTPUTS_DIR}")

    except KeyboardInterrupt:
        print("\n\nProcessing interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
