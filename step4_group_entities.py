"""
STEP 4: Group similar entities together

Usage: python step4_group_entities.py
Reads: entity_descriptions.json (from step 3)
Output: Creates dict_unique_grouped_entity_summary.json with grouped entities
"""

import json
from openai import OpenAI


def group_entities(entities, client):
    """Group similar entities together using OpenAI"""

    # Build entity list for the prompt
    entity_list = []
    for idx, entity_data in enumerate(entities, 1):
        entity_name = entity_data.get("entity", "")
        description = entity_data.get("description", "")[:150]
        entity_list.append(f"{idx}. {entity_name} - {description}")

    entity_text = "\n".join(entity_list)

    prompt = f"""Analyze these entities and identify which ones refer to the same person.

ENTITIES:
{entity_text}

Group together entities that clearly refer to the same person. Consider:
- Name variations (e.g., "John Smith", "Mr. Smith", "J. Smith")
- Titles and prefixes (e.g., "Dr. Jane Doe", "Jane Doe")

For each group, choose the most complete/formal name as the canonical name.
Only group entities if you're confident they're the same person. When in doubt, keep them separate.
"""

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {
                "role": "system",
                "content": "You are an expert at entity resolution and deduplication."
            },
            {
                "role": "user",
                "content": prompt
            }
        ],
        temperature=0.1,
        response_format={
            "type": "json_schema",
            "json_schema": {
                "name": "entity_grouping",
                "strict": True,
                "schema": {
                    "type": "object",
                    "properties": {
                        "groups": {
                            "type": "array",
                            "items": {
                                "type": "object",
                                "properties": {
                                    "canonical_name": {"type": "string"},
                                    "variations": {
                                        "type": "array",
                                        "items": {"type": "string"}
                                    }
                                },
                                "required": ["canonical_name", "variations"],
                                "additionalProperties": False
                            }
                        }
                    },
                    "required": ["groups"],
                    "additionalProperties": False
                }
            }
        }
    )

    result = json.loads(response.choices[0].message.content)
    return result.get("groups", [])


def main():
    import sys

    api_key = input("Enter your OpenAI API key: ") if len(sys.argv) < 2 else sys.argv[1]

    print(f"\n=== STEP 4: GROUP ENTITIES ===")

    # Read entity descriptions
    print("Reading entity_descriptions.json...")
    try:
        with open("entity_descriptions.json", "r", encoding="utf-8") as f:
            data = json.load(f)
    except FileNotFoundError:
        print("Error: entity_descriptions.json not found. Run step3_describe_entities.py first.")
        sys.exit(1)

    entities = data.get("entities", [])
    if not entities:
        print("No entities found in entity_descriptions.json")
        sys.exit(1)

    print(f"Original entity count: {len(entities)}")

    # Create entity lookup by name
    entity_lookup = {}
    for entity_data in entities:
        entity_name = entity_data.get("entity", "")
        entity_lookup[entity_name] = entity_data

    # Group entities
    print("Grouping entities...")
    client = OpenAI(api_key=api_key)
    groups = group_entities(entities, client)

    # Build unique grouped entities
    grouped_entities = []
    processed_names = set()

    for group in groups:
        canonical_name = group["canonical_name"]
        variations = group["variations"]

        # Find the best description from all variations
        best_entity = None
        for variation in variations:
            if variation in entity_lookup:
                entity_data = entity_lookup[variation]
                if best_entity is None or len(entity_data.get("description", "")) > len(best_entity.get("description", "")):
                    best_entity = entity_data
                processed_names.add(variation)

        if best_entity:
            # Create merged entity
            merged_entity = {
                "entity": canonical_name,
                "description": best_entity.get("description", ""),
                "related_entities": best_entity.get("related_entities", [])
            }
            if len(variations) > 1:
                merged_entity["also_known_as"] = [v for v in variations if v != canonical_name]

            grouped_entities.append(merged_entity)

    # Add entities that weren't grouped
    for entity_data in entities:
        entity_name = entity_data.get("entity", "")
        if entity_name not in processed_names:
            grouped_entities.append(entity_data)

    # Save output in same format as entity_descriptions.json
    output = {"entities": grouped_entities}

    with open("dict_unique_grouped_entity_summary.json", "w", encoding="utf-8") as f:
        json.dump(output, f, indent=2)

    print(f"Saved: dict_unique_grouped_entity_summary.json")
    print(f"Original count: {len(entities)}")
    print(f"Grouped count: {len(grouped_entities)}")
    print(f"Duplicates removed: {len(entities) - len(grouped_entities)}")

    print("\n=== STEP 4 COMPLETE ===\n")


if __name__ == "__main__":
    main()
