"""
STEP 3: Generate descriptions for each entity

Usage: python step3_describe_entities.py
Reads: extracted_text.txt, entities.json (from previous steps)
Output: Creates entity_descriptions.json with detailed info for each entity
"""

import json
from openai import OpenAI


def describe_entities(text, persons, companies, api_key):
    """Generate detailed descriptions for entities using OpenAI"""
    client = OpenAI(api_key=api_key)

    # Combine entities (limit to 10)
    all_entities = persons[:5] + companies[:5]

    if not all_entities:
        return {}

    entity_names = ", ".join(all_entities)
    text_to_analyze = text[:12000]

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {
                "role": "system",
                "content": "You are an expert analyst. Analyze entities based only on information in the document."
            },
            {
                "role": "user",
                "content": f"""Analyze these entities from the document: {entity_names}

For each entity provide:
1. Description based on the document
2. Their role or position
3. Key activities they're involved in
4. Related entities
5. Any financial details

Document:
{text_to_analyze}"""
            }
        ],
        temperature=0.3,
        max_tokens=2000,
        response_format={
            "type": "json_schema",
            "json_schema": {
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
                                    "name": {"type": "string"},
                                    "type": {"type": "string"},
                                    "description": {"type": "string"},
                                    "role": {"type": "string"},
                                    "key_activities": {"type": "array", "items": {"type": "string"}},
                                    "related_entities": {"type": "array", "items": {"type": "string"}},
                                    "financial_details": {"type": "string"}
                                },
                                "required": ["name", "type", "description", "role", "key_activities", "related_entities", "financial_details"],
                                "additionalProperties": False
                            }
                        }
                    },
                    "required": ["entities"],
                    "additionalProperties": False
                }
            }
        }
    )

    result = json.loads(response.choices[0].message.content)

    # Convert to dictionary
    descriptions = {}
    for entity in result.get('entities', []):
        descriptions[entity['name']] = entity

    return descriptions


def main():
    import sys

    api_key = input("Enter your OpenAI API key: ") if len(sys.argv) < 2 else sys.argv[1]

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

    # Generate descriptions
    print("Generating entity descriptions...")
    descriptions = describe_entities(text, persons, companies, api_key)

    # Save descriptions
    with open("entity_descriptions.json", "w", encoding="utf-8") as f:
        json.dump(descriptions, f, indent=2)

    print("Saved: entity_descriptions.json")
    print(f"\nGenerated descriptions for {len(descriptions)} entities")

    for name, info in descriptions.items():
        print(f"\n{name} ({info['type']}):")
        print(f"  Role: {info['role']}")
        print(f"  Description: {info['description'][:100]}...")

    print("\n=== STEP 3 COMPLETE ===\n")


if __name__ == "__main__":
    main()
