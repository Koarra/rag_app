"""
STEP 3: Generate descriptions for each entity

Usage: python step3_describe_entities.py
Reads: extracted_text.txt, entities.json (from previous steps)
Output: Creates entity_descriptions.json with detailed info for each entity
"""

import json
import sys
from pathlib import Path
from pydantic import BaseModel, Field
from typing import Dict
from azure.identity import DefaultAzureCredential, get_bearer_token_provider
from llama_index.core.program import LLMTextCompletionProgram
from llama_index.llms.azure_openai import AzureOpenAI


# Pydantic model
class EntityDescriptions(BaseModel):
    entities: Dict[str, str] = Field(description="Dictionary mapping entity names to their descriptions")


def describe_entities(text, persons, companies, llm):
    """Generate detailed descriptions for entities using LlamaIndex"""

    # Combine entities
    all_entities = persons + companies

    if not all_entities:
        return {}

    entity_names = ", ".join(all_entities)
    text_to_analyze = text[:12000]

    program = LLMTextCompletionProgram.from_defaults(
        output_cls=EntityDescriptions,
        llm=llm,
        prompt_template_str="""You are an expert analyst. Analyze entities based only on information in the document.

Analyze these entities from the document: {entity_names}

For each entity provide a short description based on the document.

Document:
{document_text}
""",
        verbose=False
    )

    result = program(entity_names=entity_names, document_text=text_to_analyze)
    return result.entities


def main():
    if len(sys.argv) < 2:
        print("Usage: python step3_describe_entities.py <output_folder>")
        sys.exit(1)

    output_folder = Path(sys.argv[1])

    # Check if output_folder is a file instead of a directory
    if output_folder.exists() and output_folder.is_file():
        print(f"Error: {output_folder} is a file, not a directory!")
        print("Please provide a directory path for output_folder")
        sys.exit(1)

    output_folder.mkdir(parents=True, exist_ok=True)

    print(f"\n=== STEP 3: DESCRIBE ENTITIES ===")
    print(f"Output folder: {output_folder}")

    # Read extracted text
    print("Reading extracted_text.txt...")
    try:
        with open(output_folder / "extracted_text.txt", "r", encoding="utf-8") as f:
            text = f.read()
    except FileNotFoundError:
        print("Error: extracted_text.txt not found. Run step1_summarize.py first.")
        sys.exit(1)

    # Read entities
    print("Reading entities.json...")
    try:
        with open(output_folder / "entities.json", "r", encoding="utf-8") as f:
            entities = json.load(f)
    except FileNotFoundError:
        print("Error: entities.json not found. Run step2_extract_entities.py first.")
        sys.exit(1)

    persons = entities.get('persons', [])
    companies = entities.get('companies', [])

    # Initialize Azure OpenAI LLM
    llm = AzureOpenAI(
        engine="gpt-4o-mini",
        use_azure_ad=True,
        azure_ad_token_provider=get_bearer_token_provider(
            DefaultAzureCredential(), "https://cognitiveservices.azure.com/.default"
        )
    )

    # Generate descriptions
    print("Generating entity descriptions...")
    descriptions_dict = describe_entities(text, persons, companies, llm)

    # Save descriptions in simple dict format: {"entity": "description"}
    with open(output_folder / "entity_descriptions.json", "w", encoding="utf-8") as f:
        json.dump(descriptions_dict, f, indent=2)

    print(f"Saved: {output_folder}/entity_descriptions.json")
    print(f"\nGenerated descriptions for {len(descriptions_dict)} entities")

    for entity_name, description in descriptions_dict.items():
        print(f"\n{entity_name}:")
        print(f"  Description: {description[:100]}...")

    print("\n=== STEP 3 COMPLETE ===\n")


if __name__ == "__main__":
    main()
