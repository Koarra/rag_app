"""
STEP 4: Group similar entities together

This script identifies entities that refer to the same person or company
and groups them under a canonical name.

Examples:
- "John Smith", "Mr. Smith", "J. Smith" → "John Smith"
- "ABC Corporation", "ABC Corp", "ABC" → "ABC Corporation"
- "Microsoft Corporation", "Microsoft", "MSFT" → "Microsoft Corporation"

Usage: python step4_group_entities.py
Reads: entities.json, entity_descriptions.json (from previous steps)
Output: Creates grouped_entities.json with consolidated entity list
"""

import json
from openai import OpenAI


def load_entity_descriptions(filepath):
    """Load entity descriptions and convert to dict format"""
    with open(filepath, 'r', encoding='utf-8') as f:
        data = json.load(f)

    descriptions = {}

    # Handle array format: {"entities": [...]}
    if isinstance(data, dict) and "entities" in data:
        for entity_data in data["entities"]:
            # Support both "entity" and "name" fields
            entity_name = entity_data.get("entity") or entity_data.get("name")
            if entity_name:
                descriptions[entity_name] = entity_data
    # Handle dict format: {"entity_name": {...}}
    elif isinstance(data, dict):
        descriptions = data

    return descriptions


def group_entities(persons, companies, entity_descriptions, api_key):
    """Group similar entities together using OpenAI"""
    client = OpenAI(api_key=api_key)

    # Prepare entity list with descriptions for better matching
    persons_with_info = []
    for person in persons:
        desc = entity_descriptions.get(person, {})
        info = {
            "name": person,
            "description": desc.get("description", "")[:200]  # Truncate
        }
        persons_with_info.append(info)

    companies_with_info = []
    for company in companies:
        desc = entity_descriptions.get(company, {})
        info = {
            "name": company,
            "description": desc.get("description", "")[:200]
        }
        companies_with_info.append(info)

    # Group persons
    print("Grouping persons...")
    grouped_persons = []
    if persons_with_info:
        grouped_persons = _group_entity_type(
            client,
            persons_with_info,
            "persons"
        )

    # Group companies
    print("Grouping companies...")
    grouped_companies = []
    if companies_with_info:
        grouped_companies = _group_entity_type(
            client,
            companies_with_info,
            "companies"
        )

    return {
        "persons": grouped_persons,
        "companies": grouped_companies
    }


def _group_entity_type(client, entities_with_info, entity_type):
    """Group a specific type of entity (persons or companies)"""

    # Build entity context for the prompt
    entity_list = []
    for idx, entity in enumerate(entities_with_info):
        desc = entity.get('description', '')
        if desc:
            entity_list.append(f"{idx + 1}. {entity['name']} - {desc[:100]}")
        else:
            entity_list.append(f"{idx + 1}. {entity['name']}")

    entity_text = "\n".join(entity_list)

    prompt = f"""Analyze these {entity_type} and identify which ones refer to the same entity.

{entity_type.upper()}:
{entity_text}

Group together entities that clearly refer to the same person/company. Consider:
- Name variations (e.g., "John Smith", "Mr. Smith", "J. Smith")
- Abbreviations (e.g., "ABC Corporation", "ABC Corp", "ABC")
- Titles and prefixes (e.g., "Dr. Jane Doe", "Jane Doe")

For each group, choose the most complete/formal name as the canonical name.
Only group entities if you're confident they're the same. When in doubt, keep them separate.
"""

    response = client.chat.completions.create(
        model="gpt-4o",
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
        max_tokens=2000,
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
                            "description": "Groups of entities that refer to the same thing",
                            "items": {
                                "type": "object",
                                "properties": {
                                    "canonical_name": {
                                        "type": "string",
                                        "description": "The official/preferred name for this entity"
                                    },
                                    "variations": {
                                        "type": "array",
                                        "description": "All name variations that refer to this entity",
                                        "items": {"type": "string"}
                                    },
                                    "reasoning": {
                                        "type": "string",
                                        "description": "Why these variations were grouped together"
                                    }
                                },
                                "required": ["canonical_name", "variations", "reasoning"],
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
    return result.get('groups', [])


def merge_entity_descriptions(grouped_entities, entity_descriptions):
    """Merge descriptions for grouped entities"""
    merged_descriptions = {}

    # Process persons
    for group in grouped_entities.get('persons', []):
        canonical_name = group['canonical_name']
        variations = group['variations']

        # Get descriptions for all variations
        all_descriptions = []
        for variation in variations:
            if variation in entity_descriptions:
                all_descriptions.append(entity_descriptions[variation])

        # Use the most complete description (or first available)
        if all_descriptions:
            # Pick description with most information
            best_desc = max(
                all_descriptions,
                key=lambda d: len(d.get('description', ''))
            )

            # Build merged description in consistent format
            merged_descriptions[canonical_name] = {
                "entity": canonical_name,
                "description": best_desc.get('description', ''),
                "related_entities": best_desc.get('related_entities', []),
                "also_known_as": [v for v in variations if v != canonical_name],
                "merged_from": len(variations)
            }

    # Process companies
    for group in grouped_entities.get('companies', []):
        canonical_name = group['canonical_name']
        variations = group['variations']

        all_descriptions = []
        for variation in variations:
            if variation in entity_descriptions:
                all_descriptions.append(entity_descriptions[variation])

        if all_descriptions:
            best_desc = max(
                all_descriptions,
                key=lambda d: len(d.get('description', ''))
            )

            merged_descriptions[canonical_name] = {
                "entity": canonical_name,
                "description": best_desc.get('description', ''),
                "related_entities": best_desc.get('related_entities', []),
                "also_known_as": [v for v in variations if v != canonical_name],
                "merged_from": len(variations)
            }

    return merged_descriptions


def main():
    import sys

    api_key = input("Enter your OpenAI API key: ") if len(sys.argv) < 2 else sys.argv[1]

    print(f"\n=== STEP 4: GROUP ENTITIES ===")

    # Read entities
    print("Reading entities.json...")
    try:
        with open("entities.json", "r", encoding="utf-8") as f:
            entities = json.load(f)
    except FileNotFoundError:
        print("Error: entities.json not found. Run step2_extract_entities.py first.")
        sys.exit(1)

    # Read entity descriptions
    print("Reading entity_descriptions.json...")
    try:
        entity_descriptions = load_entity_descriptions("entity_descriptions.json")
    except FileNotFoundError:
        print("Error: entity_descriptions.json not found. Run step3_describe_entities.py first.")
        sys.exit(1)

    persons = entities.get('persons', [])
    companies = entities.get('companies', [])

    print(f"\nOriginal counts:")
    print(f"  Persons: {len(persons)}")
    print(f"  Companies: {len(companies)}")

    # Group entities
    grouped = group_entities(persons, companies, entity_descriptions, api_key)

    # Calculate unique entities
    unique_persons = len(grouped['persons'])
    unique_companies = len(grouped['companies'])

    print(f"\nGrouped counts:")
    print(f"  Unique persons: {unique_persons}")
    print(f"  Unique companies: {unique_companies}")

    # Show groupings
    if grouped['persons']:
        print(f"\nPerson groups:")
        for group in grouped['persons']:
            if len(group['variations']) > 1:
                print(f"  {group['canonical_name']}:")
                print(f"    Variations: {', '.join(group['variations'])}")

    if grouped['companies']:
        print(f"\nCompany groups:")
        for group in grouped['companies']:
            if len(group['variations']) > 1:
                print(f"  {group['canonical_name']}:")
                print(f"    Variations: {', '.join(group['variations'])}")

    # Merge descriptions for grouped entities
    print("\nMerging entity descriptions...")
    merged_descriptions = merge_entity_descriptions(grouped, entity_descriptions)

    # Create output in array format (matching user's format)
    entities_array = []
    for entity_name, data in merged_descriptions.items():
        entities_array.append(data)

    # Create output
    output = {
        "groupings": grouped,
        "unique_entity_count": {
            "persons": unique_persons,
            "companies": unique_companies,
            "total": unique_persons + unique_companies
        },
        "original_entity_count": {
            "persons": len(persons),
            "companies": len(companies),
            "total": len(persons) + len(companies)
        },
        "merged_descriptions": {
            "entities": entities_array
        }
    }

    # Save grouped entities
    with open("grouped_entities.json", "w", encoding="utf-8") as f:
        json.dump(output, f, indent=2)

    print("Saved: grouped_entities.json")

    # Calculate merge stats
    persons_merged = sum(len(g['variations']) for g in grouped['persons']) - unique_persons
    companies_merged = sum(len(g['variations']) for g in grouped['companies']) - unique_companies

    print(f"\nMerge statistics:")
    print(f"  Persons merged: {persons_merged}")
    print(f"  Companies merged: {companies_merged}")
    print(f"  Total duplicates removed: {persons_merged + companies_merged}")

    print("\n=== STEP 4 COMPLETE ===\n")


if __name__ == "__main__":
    main()
