"""
Stage 2: Entity Extraction
Identifies persons and companies from document text using OpenAI
"""
import sys
from pathlib import Path
from typing import Dict, List, Set

sys.path.append(str(Path(__file__).parent.parent))

from src.utils import Config, OpenAIClient, FileHandler


class EntityExtractor:
    def __init__(self, api_key: str = None):
        self.openai_client = OpenAIClient(api_key)
        self.file_handler = FileHandler()

    def extract_entities(self, text: str, document_name: str) -> Dict[str, List[str]]:
        """
        Extract persons and companies from document text

        Args:
            text: Document text
            document_name: Name of the document

        Returns:
            Dictionary with 'persons' and 'companies' lists
        """
        print(f"\n{'='*60}")
        print(f"STAGE 2: ENTITY EXTRACTION")
        print(f"{'='*60}")
        print(f"Extracting entities from: {document_name}")

        # Define JSON schema for structured output
        json_schema = {
            "name": "entity_extraction",
            "strict": True,
            "schema": {
                "type": "object",
                "properties": {
                    "persons": {
                        "type": "array",
                        "description": "List of person names found in the document",
                        "items": {"type": "string"}
                    },
                    "companies": {
                        "type": "array",
                        "description": "List of company/organization names found in the document",
                        "items": {"type": "string"}
                    }
                },
                "required": ["persons", "companies"],
                "additionalProperties": False
            }
        }

        # Split text if too long
        chunks = self._chunk_text(text)
        print(f"Processing {len(chunks)} chunk(s)...")

        all_persons = set()
        all_companies = set()

        for i, chunk in enumerate(chunks, 1):
            if len(chunks) > 1:
                print(f"Extracting from chunk {i}/{len(chunks)}...")

            entities = self._extract_from_chunk(chunk, json_schema)
            all_persons.update(entities.get("persons", []))
            all_companies.update(entities.get("companies", []))

        # Normalize and deduplicate
        persons = self._normalize_entities(all_persons)
        companies = self._normalize_entities(all_companies)

        result = {
            "persons": sorted(persons),
            "companies": sorted(companies)
        }

        print(f"✓ Found {len(persons)} unique person(s)")
        print(f"✓ Found {len(companies)} unique company/organization(s)")

        return result

    def _chunk_text(self, text: str) -> List[str]:
        """Split text into chunks for processing"""
        max_size = Config.MAX_CHUNK_SIZE * 4
        overlap = Config.CHUNK_OVERLAP * 4

        if len(text) <= max_size:
            return [text]

        chunks = []
        start = 0

        while start < len(text):
            end = start + max_size
            chunk = text[start:end]

            # Try to break at paragraph boundary
            if end < len(text):
                last_newline = chunk.rfind('\n\n')
                if last_newline > max_size * 0.7:
                    end = start + last_newline

            chunks.append(text[start:end])
            start = end - overlap

        return chunks

    def _extract_from_chunk(self, text: str, json_schema: Dict) -> Dict:
        """Extract entities from a single chunk"""

        messages = [
            {
                "role": "system",
                "content": """You are an expert entity extraction system. Extract all persons and companies/organizations mentioned in the document.

Guidelines:
- Persons: Extract full names of individuals (e.g., "John Smith", "Dr. Jane Doe")
- Companies: Extract company names, organizations, institutions (e.g., "ABC Corporation", "Ministry of Finance")
- Include variations if mentioned (e.g., "John Smith" and "Mr. Smith" should be consolidated as "John Smith")
- Exclude generic titles or roles without names
- Be thorough - extract all entities mentioned"""
            },
            {
                "role": "user",
                "content": f"Extract all persons and companies from this document:\n\n{text}"
            }
        ]

        return self.openai_client.chat_completion_json(
            messages=messages,
            model=Config.ENTITY_EXTRACTION_MODEL,
            json_schema=json_schema,
            temperature=0.1  # Low temperature for consistency
        )

    def _normalize_entities(self, entities: Set[str]) -> List[str]:
        """
        Normalize entity names and remove duplicates

        Args:
            entities: Set of entity names

        Returns:
            List of normalized, deduplicated entity names
        """
        normalized = set()

        for entity in entities:
            # Clean up whitespace
            clean = ' '.join(entity.split())

            # Skip empty or very short entities
            if len(clean) < 2:
                continue

            # Skip common noise words
            noise_words = {'the', 'a', 'an', 'and', 'or', 'mr', 'mrs', 'ms', 'dr'}
            if clean.lower() in noise_words:
                continue

            normalized.add(clean)

        # Further deduplicate similar entities (simple approach)
        final_entities = []
        for entity in sorted(normalized):
            # Check if this entity is a substring of an already added entity
            is_substring = False
            for existing in final_entities:
                if entity.lower() in existing.lower() and entity.lower() != existing.lower():
                    is_substring = True
                    break

            if not is_substring:
                final_entities.append(entity)

        return final_entities

    def process(self, text: str, document_name: str, file_path: Path) -> Dict[str, List[str]]:
        """
        Complete Stage 2 processing: Extract entities

        Args:
            text: Document text
            document_name: Name of document
            file_path: Original file path

        Returns:
            Dictionary with extracted entities
        """
        entities = self.extract_entities(text, document_name)

        # Save entities
        output_filename = self.file_handler.get_output_filename(
            file_path.name, '_entities', 'json'
        )
        output_path = Config.ENTITIES_DIR / output_filename
        self.file_handler.save_json(entities, output_path)

        # Also save as readable text
        text_filename = self.file_handler.get_output_filename(
            file_path.name, '_entities', 'txt'
        )
        text_path = Config.ENTITIES_DIR / text_filename

        entity_text = f"""EXTRACTED ENTITIES
{'='*60}

PERSONS ({len(entities['persons'])})
{'-'*60}
"""
        for i, person in enumerate(entities['persons'], 1):
            entity_text += f"{i}. {person}\n"

        entity_text += f"""
COMPANIES/ORGANIZATIONS ({len(entities['companies'])})
{'-'*60}
"""
        for i, company in enumerate(entities['companies'], 1):
            entity_text += f"{i}. {company}\n"

        self.file_handler.save_text(entity_text, text_path)

        print(f"\n{'='*60}")
        print(f"✓ STAGE 2 COMPLETE")
        print(f"{'='*60}\n")

        return entities


if __name__ == "__main__":
    # Test the entity extractor
    import sys

    if len(sys.argv) < 2:
        print("Usage: python entity_extractor.py <path_to_extracted_text>")
        sys.exit(1)

    Config.ensure_directories()
    extractor = EntityExtractor()

    text_file = Path(sys.argv[1])
    if not text_file.exists():
        print(f"Error: File not found: {text_file}")
        sys.exit(1)

    with open(text_file, 'r', encoding='utf-8') as f:
        text = f.read()

    entities = extractor.process(text, text_file.name, text_file)
    print(f"\nExtracted Entities:")
    print(f"Persons: {', '.join(entities['persons'][:5])}...")
    print(f"Companies: {', '.join(entities['companies'][:5])}...")
