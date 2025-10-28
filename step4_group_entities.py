"""
STEP 4: Group similar entities together

Usage: python step4_group_entities.py
Reads: entity_descriptions.json (from step 3)
Output: Creates dict_unique_grouped_entity_summary.json with grouped entities
"""

import json
import sys
from pathlib import Path
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
    if len(sys.argv) < 2:
        print("Usage: python step4_group_entities.py <output_folder>")
        sys.exit(1)

    output_folder = Path(sys.argv[1])
    output_folder.mkdir(parents=True, exist_ok=True)

    print(f"\n=== STEP 4: GROUP ENTITIES ===")
    print(f"Output folder: {output_folder}")

    # Read entity descriptions
    print("Reading entity_descriptions.json...")
    try:
        with open(output_folder / "entity_descriptions.json", "r", encoding="utf-8") as f:
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

    # Build output: start with all original entities
    grouped_entities = entities_dict.copy()

    # Process groups and merge duplicates
    for group in groups:
        canonical_name = group.canonical_name
        variations = group.variations

        # Find the best (longest) description from all variations
        best_description = ""
        for variation in variations:
            if variation in entities_dict:
                desc = entities_dict[variation]
                if len(desc) > len(best_description):
                    best_description = desc

        # Keep only the canonical name, remove variations
        grouped_entities[canonical_name] = best_description
        for variation in variations:
            if variation != canonical_name and variation in grouped_entities:
                del grouped_entities[variation]

    # Save output as simple dict: {"entity1": "description1", ...}
    with open(output_folder / "dict_unique_grouped_entity_summary.json", "w", encoding="utf-8") as f:
        json.dump(grouped_entities, f, indent=2)

    print(f"Saved: {output_folder}/dict_unique_grouped_entity_summary.json")
    print(f"Original count: {len(entities_dict)}")
    print(f"Grouped count: {len(grouped_entities)}")
    print(f"Duplicates removed: {len(entities_dict) - len(grouped_entities)}")

    print("\n=== STEP 4 COMPLETE ===\n")


if __name__ == "__main__":
    main()
