"""
STEP 2: Extract persons and companies from document

Usage: python step2_extract_entities.py
Reads: extracted_text.txt (from step 1)
Output: Creates entities.json with list of persons and companies
"""

import json
from openai import OpenAI


def extract_entities(text, api_key):
    """Extract persons and companies using OpenAI"""
    client = OpenAI(api_key=api_key)

    # Limit text to 15000 characters
    text_to_analyze = text[:15000]

    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {
                "role": "system",
                "content": "You are an expert at extracting entities from documents."
            },
            {
                "role": "user",
                "content": f"""Extract all persons and companies from this document.

Guidelines:
- Persons: Full names of individuals (e.g., "John Smith", "Dr. Jane Doe")
- Companies: Company names, organizations, institutions (e.g., "ABC Corporation", "Ministry of Finance")
- Be thorough - extract all entities mentioned

Document:
{text_to_analyze}"""
            }
        ],
        temperature=0.1,
        response_format={
            "type": "json_schema",
            "json_schema": {
                "name": "entities",
                "strict": True,
                "schema": {
                    "type": "object",
                    "properties": {
                        "persons": {
                            "type": "array",
                            "items": {"type": "string"}
                        },
                        "companies": {
                            "type": "array",
                            "items": {"type": "string"}
                        }
                    },
                    "required": ["persons", "companies"],
                    "additionalProperties": False
                }
            }
        }
    )

    return json.loads(response.choices[0].message.content)


def main():
    import sys

    api_key = input("Enter your OpenAI API key: ") if len(sys.argv) < 2 else sys.argv[1]

    print(f"\n=== STEP 2: EXTRACT ENTITIES ===")

    # Read extracted text from step 1
    print("Reading extracted_text.txt...")
    try:
        with open("extracted_text.txt", "r", encoding="utf-8") as f:
            text = f.read()
    except FileNotFoundError:
        print("Error: extracted_text.txt not found. Run step1_summarize.py first.")
        sys.exit(1)

    # Extract entities
    print("Extracting entities...")
    entities = extract_entities(text, api_key)

    # Save entities
    with open("entities.json", "w", encoding="utf-8") as f:
        json.dump(entities, f, indent=2)

    print("Saved: entities.json")
    print(f"\nFound {len(entities['persons'])} person(s)")
    print(f"Found {len(entities['companies'])} company/companies")

    print(f"\nPersons: {entities['persons']}")
    print(f"\nCompanies: {entities['companies']}")

    print("\n=== STEP 2 COMPLETE ===\n")


if __name__ == "__main__":
    main()
