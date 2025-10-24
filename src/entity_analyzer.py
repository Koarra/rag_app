"""
Stage 3: Entity Analysis and Description Generation
Creates detailed descriptions for each extracted entity based on document context
"""
import sys
from pathlib import Path
from typing import Dict, List

sys.path.append(str(Path(__file__).parent.parent))

from src.utils import Config, OpenAIClient, FileHandler


class EntityAnalyzer:
    def __init__(self, api_key: str = None):
        self.openai_client = OpenAIClient(api_key)
        self.file_handler = FileHandler()

    def analyze_entities(
        self,
        entities: Dict[str, List[str]],
        document_text: str,
        document_name: str
    ) -> Dict[str, Dict]:
        """
        Generate descriptions for all entities based on document context

        Args:
            entities: Dictionary with 'persons' and 'companies' lists
            document_text: Full document text for context
            document_name: Name of the document

        Returns:
            Dictionary mapping entity names to their descriptions
        """
        print(f"\n{'='*60}")
        print(f"STAGE 3: ENTITY ANALYSIS")
        print(f"{'='*60}")
        print(f"Analyzing entities from: {document_name}")

        all_entities = []
        for person in entities.get('persons', []):
            all_entities.append({"name": person, "type": "person"})
        for company in entities.get('companies', []):
            all_entities.append({"name": company, "type": "company"})

        print(f"Generating descriptions for {len(all_entities)} entities...")

        entity_descriptions = {}

        # Process in batches to optimize API calls
        batch_size = 5
        for i in range(0, len(all_entities), batch_size):
            batch = all_entities[i:i+batch_size]
            batch_descriptions = self._analyze_batch(batch, document_text)
            entity_descriptions.update(batch_descriptions)

            print(f"✓ Processed {min(i+batch_size, len(all_entities))}/{len(all_entities)} entities")

        return entity_descriptions

    def _analyze_batch(
        self,
        entities_batch: List[Dict],
        document_text: str
    ) -> Dict[str, Dict]:
        """
        Analyze a batch of entities in a single API call

        Args:
            entities_batch: List of entity dicts with 'name' and 'type'
            document_text: Full document text

        Returns:
            Dictionary of entity descriptions
        """
        # Create list of entity names
        entity_names = [e['name'] for e in entities_batch]

        # Define JSON schema
        json_schema = {
            "name": "entity_descriptions",
            "strict": True,
            "schema": {
                "type": "object",
                "properties": {
                    "entities": {
                        "type": "array",
                        "items": {
                            "type": "object",
                            "properties": {
                                "name": {
                                    "type": "string",
                                    "description": "Entity name"
                                },
                                "type": {
                                    "type": "string",
                                    "description": "Entity type (person or company)"
                                },
                                "description": {
                                    "type": "string",
                                    "description": "Detailed description based on document context"
                                },
                                "role": {
                                    "type": "string",
                                    "description": "Role or position in the document context"
                                },
                                "key_activities": {
                                    "type": "array",
                                    "description": "List of key activities or actions mentioned",
                                    "items": {"type": "string"}
                                },
                                "related_entities": {
                                    "type": "array",
                                    "description": "Other entities they are connected to",
                                    "items": {"type": "string"}
                                },
                                "financial_details": {
                                    "type": "string",
                                    "description": "Any financial amounts or transactions mentioned"
                                }
                            },
                            "required": [
                                "name",
                                "type",
                                "description",
                                "role",
                                "key_activities",
                                "related_entities",
                                "financial_details"
                            ],
                            "additionalProperties": False
                        }
                    }
                },
                "required": ["entities"],
                "additionalProperties": False
            }
        }

        # Truncate document if too long (keep relevant portions)
        max_doc_length = 12000
        truncated_text = self._get_relevant_context(document_text, entity_names, max_doc_length)

        messages = [
            {
                "role": "system",
                "content": """You are an expert analyst specializing in entity profiling from documents.
For each entity, provide:
1. A comprehensive description based ONLY on information in the document
2. Their role or position
3. Key activities or actions they're involved in
4. Related entities they interact with
5. Any financial details (amounts, transactions, etc.)

Be factual and precise. Only include information explicitly stated or clearly implied in the document."""
            },
            {
                "role": "user",
                "content": f"""Analyze these entities based on the document context:

Entities to analyze: {', '.join(entity_names)}

Document:
{truncated_text}

Provide detailed analysis for each entity."""
            }
        ]

        response = self.openai_client.chat_completion_json(
            messages=messages,
            model=Config.DESCRIPTION_MODEL,
            json_schema=json_schema,
            temperature=0.3,
            max_tokens=2000
        )

        # Convert to dictionary format
        result = {}
        for entity_data in response.get('entities', []):
            name = entity_data['name']
            result[name] = {
                "type": entity_data['type'],
                "description": entity_data['description'],
                "role": entity_data['role'],
                "key_activities": entity_data['key_activities'],
                "related_entities": entity_data['related_entities'],
                "financial_details": entity_data['financial_details'],
                "mention_count": document_text.count(name)
            }

        return result

    def _get_relevant_context(
        self,
        document_text: str,
        entity_names: List[str],
        max_length: int
    ) -> str:
        """
        Extract relevant portions of document mentioning the entities

        Args:
            document_text: Full document text
            entity_names: List of entity names to find
            max_length: Maximum length of context

        Returns:
            Relevant text portions
        """
        if len(document_text) <= max_length:
            return document_text

        # Find paragraphs mentioning any of the entities
        paragraphs = document_text.split('\n\n')
        relevant_paragraphs = []

        for para in paragraphs:
            for entity in entity_names:
                if entity.lower() in para.lower():
                    relevant_paragraphs.append(para)
                    break

        # If relevant paragraphs are too long, truncate
        relevant_text = '\n\n'.join(relevant_paragraphs)

        if len(relevant_text) > max_length:
            # Take beginning and end
            half = max_length // 2
            relevant_text = relevant_text[:half] + "\n\n[...]\n\n" + relevant_text[-half:]

        return relevant_text if relevant_text else document_text[:max_length]

    def process(
        self,
        entities: Dict[str, List[str]],
        document_text: str,
        document_name: str,
        file_path: Path
    ) -> Dict[str, Dict]:
        """
        Complete Stage 3 processing: Analyze entities

        Args:
            entities: Extracted entities from Stage 2
            document_text: Full document text
            document_name: Name of document
            file_path: Original file path

        Returns:
            Dictionary with entity descriptions
        """
        descriptions = self.analyze_entities(entities, document_text, document_name)

        # Save descriptions
        output_filename = self.file_handler.get_output_filename(
            file_path.name, '_entity_descriptions', 'json'
        )
        output_path = Config.DESCRIPTIONS_DIR / output_filename
        self.file_handler.save_json(descriptions, output_path)

        # Also save as readable text
        text_filename = self.file_handler.get_output_filename(
            file_path.name, '_entity_descriptions', 'txt'
        )
        text_path = Config.DESCRIPTIONS_DIR / text_filename

        desc_text = f"""ENTITY DESCRIPTIONS
{'='*60}

Total Entities: {len(descriptions)}
"""

        for entity_name, info in descriptions.items():
            desc_text += f"""
{'-'*60}
Entity: {entity_name}
Type: {info['type'].upper()}
Mentions: {info['mention_count']}

Role:
{info['role']}

Description:
{info['description']}

Key Activities:
"""
            for activity in info['key_activities']:
                desc_text += f"  • {activity}\n"

            desc_text += f"""
Related Entities:
{', '.join(info['related_entities']) if info['related_entities'] else 'None identified'}

Financial Details:
{info['financial_details'] if info['financial_details'] else 'None mentioned'}
"""

        self.file_handler.save_text(desc_text, text_path)

        print(f"\n{'='*60}")
        print(f"✓ STAGE 3 COMPLETE - Generated {len(descriptions)} entity descriptions")
        print(f"{'='*60}\n")

        return descriptions


if __name__ == "__main__":
    # Test the entity analyzer
    import json

    if len(sys.argv) < 3:
        print("Usage: python entity_analyzer.py <entities_json> <extracted_text>")
        sys.exit(1)

    Config.ensure_directories()
    analyzer = EntityAnalyzer()

    entities_file = Path(sys.argv[1])
    text_file = Path(sys.argv[2])

    with open(entities_file, 'r') as f:
        entities = json.load(f)

    with open(text_file, 'r', encoding='utf-8') as f:
        text = f.read()

    descriptions = analyzer.process(entities, text, text_file.name, text_file)
    print(f"\nGenerated descriptions for {len(descriptions)} entities")
