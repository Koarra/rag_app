"""
Stage 1: Document Processing and Summarization
Extracts text from PDF/DOCX and generates summaries using OpenAI
"""
import sys
from pathlib import Path
from typing import Dict, Tuple

# Add parent directory to path for imports
sys.path.append(str(Path(__file__).parent.parent))

from pdf_docx_extractor import DocumentProcessor as DocExtractor
from src.utils import Config, OpenAIClient, FileHandler


class DocumentProcessor:
    def __init__(self, api_key: str = None):
        self.doc_extractor = DocExtractor(use_ocr=True)
        self.openai_client = OpenAIClient(api_key)
        self.file_handler = FileHandler()

    def extract_text(self, file_path: Path) -> str:
        """
        Extract text from PDF or DOCX file

        Args:
            file_path: Path to the document

        Returns:
            Extracted text content
        """
        print(f"\n{'='*60}")
        print(f"STAGE 1: DOCUMENT EXTRACTION")
        print(f"{'='*60}")
        print(f"Processing: {file_path.name}")

        text = self.doc_extractor.process_file(str(file_path))

        if text.startswith("Error"):
            raise ValueError(f"Failed to extract text: {text}")

        print(f"✓ Extracted {len(text)} characters")
        return text

    def _chunk_text(self, text: str, max_size: int = None) -> list:
        """
        Split text into chunks for processing large documents

        Args:
            text: Full text content
            max_size: Maximum chunk size in characters (approx 4 chars per token)

        Returns:
            List of text chunks
        """
        max_size = max_size or (Config.MAX_CHUNK_SIZE * 4)
        overlap = Config.CHUNK_OVERLAP * 4

        if len(text) <= max_size:
            return [text]

        chunks = []
        start = 0

        while start < len(text):
            end = start + max_size
            chunk = text[start:end]

            # Try to break at sentence boundary
            if end < len(text):
                last_period = chunk.rfind('. ')
                if last_period > max_size * 0.7:  # At least 70% of max size
                    end = start + last_period + 2

            chunks.append(text[start:end])
            start = end - overlap

        return chunks

    def summarize_text(
        self,
        text: str,
        document_name: str,
        summary_type: str = "comprehensive"
    ) -> Dict[str, str]:
        """
        Generate summary of the document using OpenAI

        Args:
            text: Document text
            document_name: Name of the document
            summary_type: Type of summary ('executive' or 'comprehensive')

        Returns:
            Dictionary with summary types and content
        """
        print(f"\nGenerating {summary_type} summary...")

        chunks = self._chunk_text(text)
        print(f"Document split into {len(chunks)} chunk(s)")

        if len(chunks) == 1:
            # Single chunk - direct summarization
            summary = self._summarize_chunk(chunks[0], summary_type)
        else:
            # Multiple chunks - summarize each then combine
            chunk_summaries = []
            for i, chunk in enumerate(chunks, 1):
                print(f"Summarizing chunk {i}/{len(chunks)}...")
                chunk_summary = self._summarize_chunk(chunk, "comprehensive")
                chunk_summaries.append(chunk_summary)

            # Combine chunk summaries
            combined = "\n\n".join(chunk_summaries)
            summary = self._summarize_chunk(combined, summary_type)

        summaries = {
            "executive_summary": self._generate_executive_summary(summary),
            "comprehensive_summary": summary
        }

        print(f"✓ Summary generated ({len(summary)} characters)")
        return summaries

    def _summarize_chunk(self, text: str, summary_type: str) -> str:
        """Summarize a single chunk of text"""

        if summary_type == "executive":
            prompt = """Provide a concise executive summary of this document in 3-5 bullet points.
Focus on the most critical information, key decisions, and main stakeholders."""
            max_tokens = 300
        else:
            prompt = """Provide a comprehensive summary of this document.
Include:
- Main purpose and context
- Key parties involved
- Important dates and amounts
- Critical actions or decisions
- Relevant details and background

Be thorough but concise."""
            max_tokens = 1000

        messages = [
            {
                "role": "system",
                "content": "You are an expert document analyst. Summarize documents clearly and accurately."
            },
            {
                "role": "user",
                "content": f"{prompt}\n\nDocument:\n{text}"
            }
        ]

        return self.openai_client.chat_completion(
            messages=messages,
            model=Config.SUMMARIZATION_MODEL,
            temperature=0.3,
            max_tokens=max_tokens
        )

    def _generate_executive_summary(self, comprehensive_summary: str) -> str:
        """Generate executive summary from comprehensive summary"""

        messages = [
            {
                "role": "system",
                "content": "You are an executive briefing specialist. Create concise, high-level summaries."
            },
            {
                "role": "user",
                "content": f"""Create a brief executive summary (3-5 bullet points) from this comprehensive summary.
Focus only on the most critical points.

Comprehensive Summary:
{comprehensive_summary}"""
            }
        ]

        return self.openai_client.chat_completion(
            messages=messages,
            model=Config.SUMMARIZATION_MODEL,
            temperature=0.3,
            max_tokens=300
        )

    def process(self, file_path: Path) -> Tuple[str, Dict[str, str]]:
        """
        Complete Stage 1 processing: Extract and summarize

        Args:
            file_path: Path to document

        Returns:
            Tuple of (extracted_text, summaries_dict)
        """
        # Extract text
        text = self.extract_text(file_path)

        # Save extracted text
        output_filename = self.file_handler.get_output_filename(
            file_path.name, '_extracted', 'txt'
        )
        output_path = Config.EXTRACTED_TEXT_DIR / output_filename
        self.file_handler.save_text(text, output_path)

        # Generate summaries
        summaries = self.summarize_text(text, file_path.name)

        # Save summaries
        summary_filename = self.file_handler.get_output_filename(
            file_path.name, '_summary', 'json'
        )
        summary_path = Config.SUMMARIES_DIR / summary_filename
        self.file_handler.save_json(summaries, summary_path)

        # Also save as text for easy reading
        summary_text_filename = self.file_handler.get_output_filename(
            file_path.name, '_summary', 'txt'
        )
        summary_text_path = Config.SUMMARIES_DIR / summary_text_filename
        summary_text = f"""EXECUTIVE SUMMARY
{'='*60}
{summaries['executive_summary']}

COMPREHENSIVE SUMMARY
{'='*60}
{summaries['comprehensive_summary']}
"""
        self.file_handler.save_text(summary_text, summary_text_path)

        print(f"\n{'='*60}")
        print(f"✓ STAGE 1 COMPLETE")
        print(f"{'='*60}\n")

        return text, summaries


if __name__ == "__main__":
    # Test the document processor
    import sys

    if len(sys.argv) < 2:
        print("Usage: python document_processor.py <path_to_document>")
        sys.exit(1)

    Config.ensure_directories()
    processor = DocumentProcessor()

    file_path = Path(sys.argv[1])
    if not file_path.exists():
        print(f"Error: File not found: {file_path}")
        sys.exit(1)

    text, summaries = processor.process(file_path)
    print(f"\nExtracted {len(text)} characters")
    print(f"\nExecutive Summary:\n{summaries['executive_summary']}")
