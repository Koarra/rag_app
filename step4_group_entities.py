"""
STEP 4: Group similar entities together

Usage: python step4_group_entities.py
Reads: entity_descriptions.json (from step 3)
Output: Creates dict_unique_grouped_entity_summary.json with grouped entities
"""

import json
from pydantic import BaseModel, Field
from typing import List
from azure.identity import DefaultAzureCredential, get_bearer_token_provider
from llama_index.core.program import LLMTextCompletionProgram
from llama_index.llms.azure_openai import AzureOpenAI


# Pydantic models
class EntityGroup(BaseModel):
    canonical_name: str = Field(description="The official/preferred name for this entity")
    variations: List[str] = Field(description="All name variations that refer to this entity")


class EntityGrouping(BaseModel):
    groups: List[EntityGroup] = Field(description="Groups of entities that refer to the same person")


def group_entities(entities, llm):
    """Group similar entities together using LlamaIndex"""

    # Build entity list for the prompt
    entity_list = []
    for idx, entity_data in enumerate(entities, 1):
        entity_name = entity_data.get("entity", "")
        description = entity_data.get("description", "")[:150]
        entity_list.append(f"{idx}. {entity_name} - {description}")

    entities_formatted = "\n".join(entity_list)

    program = LLMTextCompletionProgram.from_defaults(
        output_cls=EntityGrouping,
        llm=llm,
        prompt_template_str="""You are an expert at entity resolution and deduplication.

Analyze these entities and identify which ones refer to the same person.

ENTITIES:
{entities_str}

Group together entities that clearly refer to the same person. Consider:
- Name variations (e.g., "John Smith", "Mr. Smith", "J. Smith")
- Titles and prefixes (e.g., "Dr. Jane Doe", "Jane Doe")

For each group, choose the most complete/formal name as the canonical name.
Only group entities if you're confident they're the same person. When in doubt, keep them separate.
""",
        verbose=False
    )

    result = program(entities_str=entities_formatted)
    return result.groups


def main():
    import sys

    print(f"\n=== STEP 4: GROUP ENTITIES ===")

    # Read entity descriptions
    print("Reading entity_descriptions.json...")
    try:
        with open("entity_descriptions.json", "r", encoding="utf-8") as f:
            data = json.load(f)
    except FileNotFoundError:
        print("Error: entity_descriptions.json not found. Run step3_describe_entities.py first.")
        sys.exit(1)

    # Handle both formats: dict {"entity": "desc"} or list {"entities": [...]}
    if isinstance(data, dict) and "entities" in data:
        # Old list format
        entities_dict = {e.get("entity", ""): e.get("description", "") for e in data.get("entities", [])}
    else:
        # New dict format
        entities_dict = data

    if not entities_dict:
        print("No entities found in entity_descriptions.json")
        sys.exit(1)

    print(f"Original entity count: {len(entities_dict)}")

    # Convert dict to list format for grouping algorithm
    entities = []
    for entity_name, description in entities_dict.items():
        entities.append({"entity": entity_name, "description": description})

    # Create entity lookup by name
    entity_lookup = {}
    for entity_data in entities:
        entity_name = entity_data.get("entity", "")
        entity_lookup[entity_name] = entity_data

    # Initialize Azure OpenAI LLM
    llm = AzureOpenAI(
        engine="gpt-4o-mini",
        use_azure_ad=True,
        azure_ad_token_provider=get_bearer_token_provider(
            DefaultAzureCredential(), "https://cognitiveservices.azure.com/.default"
        )
    )

    # Group entities
    print("Grouping entities...")
    groups = group_entities(entities, llm)

    # Build unique grouped entities as dict
    grouped_entities = {}
    processed_names = set()

    for group in groups:
        canonical_name = group.canonical_name
        variations = group.variations

        # Find the best description from all variations
        best_entity = None
        for variation in variations:
            if variation in entity_lookup:
                entity_data = entity_lookup[variation]
                if best_entity is None or len(entity_data.get("description", "")) > len(best_entity.get("description", "")):
                    best_entity = entity_data
                processed_names.add(variation)

        if best_entity:
            # Add to dict: entity_name -> description
            grouped_entities[canonical_name] = best_entity.get("description", "")

    # Add entities that weren't grouped
    for entity_data in entities:
        entity_name = entity_data.get("entity", "")
        if entity_name not in processed_names:
            grouped_entities[entity_name] = entity_data.get("description", "")

    # Save output as simple dict: {"entity1": "description1", ...}
    with open("dict_unique_grouped_entity_summary.json", "w", encoding="utf-8") as f:
        json.dump(grouped_entities, f, indent=2)

    print(f"Saved: dict_unique_grouped_entity_summary.json")
    print(f"Original count: {len(entities)}")
    print(f"Grouped count: {len(grouped_entities)}")
    print(f"Duplicates removed: {len(entities) - len(grouped_entities)}")

    print("\n=== STEP 4 COMPLETE ===\n")


if __name__ == "__main__":
    main()
