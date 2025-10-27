"""
STEP 3: Generate descriptions for each entity

Usage: python step3_describe_entities.py
Reads: extracted_text.txt, entities.json (from previous steps)
Output: Creates entity_descriptions.json with detailed info for each entity
"""

import json
from pydantic import BaseModel, Field
from typing import List
from azure.identity import DefaultAzureCredential, get_bearer_token_provider
from llama_index.core.program import LLMTextCompletionProgram
from llama_index.llms.azure_openai import AzureOpenAI


# Pydantic models
class EntityDescription(BaseModel):
    entity: str = Field(description="The entity name")
    description: str = Field(description="A short description of the entity based on the document")
    related_entities: List[str] = Field(description="List of related entities mentioned in the document")


class EntityDescriptions(BaseModel):
    entities: List[EntityDescription] = Field(description="List of entity descriptions")


def describe_entities(text, persons, companies, llm):
    """Generate detailed descriptions for entities using LlamaIndex"""

    # Combine entities
    all_entities = persons + companies

    if not all_entities:
        return {"entities": []}

    entity_names = ", ".join(all_entities)
    text_to_analyze = text[:12000]

    program = LLMTextCompletionProgram.from_defaults(
        output_cls=EntityDescriptions,
        llm=llm,
        prompt_template_str="""You are an expert analyst. Analyze entities based only on information in the document.

Analyze these entities from the document: {entity_names}

For each entity provide:
1. A short description based on the document
2. Related entities (other people or companies they interact with)

Document:
{document_text}
""",
        verbose=False
    )

    result = program(entity_names=entity_names, document_text=text_to_analyze)
    return result


def main():
    import sys

    print(f"\n=== STEP 3: DESCRIBE ENTITIES ===")

    # Read extracted text
    print("Reading extracted_text.txt...")
    try:
        with open("extracted_text.txt", "r", encoding="utf-8") as f:
            text = f.read()
    except FileNotFoundError:
        print("Error: extracted_text.txt not found. Run step1_summarize.py first.")
        sys.exit(1)

    # Read entities
    print("Reading entities.json...")
    try:
        with open("entities.json", "r", encoding="utf-8") as f:
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
    result = describe_entities(text, persons, companies, llm)

    # Save descriptions in the format: {"entities": [...]}
    output = result.model_dump()

    with open("entity_descriptions.json", "w", encoding="utf-8") as f:
        json.dump(output, f, indent=2)

    print("Saved: entity_descriptions.json")
    print(f"\nGenerated descriptions for {len(output['entities'])} entities")

    for entity_info in output['entities']:
        print(f"\n{entity_info['entity']}:")
        print(f"  Description: {entity_info['description'][:100]}...")

    print("\n=== STEP 3 COMPLETE ===\n")


if __name__ == "__main__":
    main()
