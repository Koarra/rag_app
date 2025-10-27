"""
STEP 5: Analyze risks - flag entities for financial crimes

Usage: python step5_analyze_risks.py
Reads: extracted_text.txt, grouped_entities.json OR entity_descriptions.json (from previous steps)
Output: Creates risk_assessment.json with flagged entities
"""

import json
from openai import OpenAI


# Predefined list of financial crimes (FCP & AML)
FINANCIAL_CRIMES = [
    "money_laundering",
    "sanctions_evasion",
    "terrorist_financing",
    "bribery",
    "corruption",
    "embezzlement",
    "fraud",
    "tax_evasion",
    "insider_trading",
    "market_manipulation",
    "ponzi_scheme",
    "pyramid_scheme",
    "identity_theft",
    "cybercrime",
    "human_trafficking"
]

# Crime descriptions for the prompt
CRIME_DESCRIPTIONS = """
1. Money Laundering - Concealing the origins of illegally obtained money
2. Sanctions Evasion - Circumventing international sanctions
3. Terrorist Financing - Providing financial support to terrorist organizations
4. Bribery - Offering or receiving something of value to influence actions
5. Corruption - Abuse of power for private gain
6. Embezzlement - Theft or misappropriation of funds by a person in a position of trust
7. Fraud - Intentional deception for financial gain
8. Tax Evasion - Illegal non-payment or underpayment of taxes
9. Insider Trading - Trading based on non-public material information
10. Market Manipulation - Artificially inflating or deflating security prices
11. Ponzi Scheme - Fraudulent investment operation paying returns from new investors
12. Pyramid Scheme - Unsustainable business model recruiting members via promised payments
13. Identity Theft - Unauthorized use of another person's identity for fraud
14. Cybercrime - Criminal activities carried out using computers or the internet
15. Human Trafficking - Illegal trade of people for exploitation or commercial gain
"""


def load_entity_descriptions(filepath):
    """Load entity descriptions from either format"""
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


def load_entity_descriptions_from_data(data):
    """Load entity descriptions from data object (not file)"""
    descriptions = {}

    # Handle array format: {"entities": [...]}
    if isinstance(data, dict) and "entities" in data:
        for entity_data in data["entities"]:
            entity_name = entity_data.get("entity") or entity_data.get("name")
            if entity_name:
                descriptions[entity_name] = entity_data
    # Handle dict format: {"entity_name": {...}}
    elif isinstance(data, dict):
        descriptions = data

    return descriptions


def analyze_document_risk(text, api_key):
    """Analyze document for financial crimes"""
    client = OpenAI(api_key=api_key)

    text_to_analyze = text[:15000]

    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {
                "role": "system",
                "content": f"""You are a financial crime analyst. Analyze documents for the following financial crimes:

{CRIME_DESCRIPTIONS}

Focus on evidence-based analysis. Only flag crimes with credible indicators."""
            },
            {
                "role": "user",
                "content": f"""Analyze this document for financial crime indicators.

Look for evidence of these crimes:
{CRIME_DESCRIPTIONS}

Document:
{text_to_analyze}"""
            }
        ],
        temperature=0.1,
        max_tokens=1500,
        response_format={
            "type": "json_schema",
            "json_schema": {
                "name": "document_risk",
                "strict": True,
                "schema": {
                    "type": "object",
                    "properties": {
                        "overall_risk_level": {"type": "string", "enum": ["high", "medium", "low", "none"]},
                        "crimes_detected": {
                            "type": "array",
                            "description": "List of crimes detected in the document",
                            "items": {"type": "string", "enum": FINANCIAL_CRIMES}
                        },
                        "red_flags": {"type": "array", "items": {"type": "string"}},
                        "suspicious_patterns": {"type": "array", "items": {"type": "string"}},
                        "analysis_summary": {"type": "string"}
                    },
                    "required": ["overall_risk_level", "crimes_detected", "red_flags", "suspicious_patterns", "analysis_summary"],
                    "additionalProperties": False
                }
            }
        }
    )

    return json.loads(response.choices[0].message.content)


def analyze_entity_risks(entity_descriptions, api_key):
    """Analyze individual entities for criminal involvement"""
    if not entity_descriptions:
        return []

    client = OpenAI(api_key=api_key)

    # Build entity context
    entity_contexts = []
    for name, info in list(entity_descriptions.items())[:10]:  # Limit to 10
        desc = info.get('description', 'No description')
        entity_contexts.append(f"Entity: {name}\nDescription: {desc}")

    all_contexts = "\n\n".join(entity_contexts)

    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {
                "role": "system",
                "content": f"""You are an expert in financial crime detection. Analyze entities for involvement in these crimes:

{CRIME_DESCRIPTIONS}

Only flag entities with credible evidence from their descriptions."""
            },
            {
                "role": "user",
                "content": f"""Analyze these entities for involvement in financial crimes.

Crimes to check for:
{CRIME_DESCRIPTIONS}

Only flag entities with credible evidence.

{all_contexts}"""
            }
        ],
        temperature=0.1,
        max_tokens=2000,
        response_format={
            "type": "json_schema",
            "json_schema": {
                "name": "entity_risks",
                "strict": True,
                "schema": {
                    "type": "object",
                    "properties": {
                        "flagged_entities": {
                            "type": "array",
                            "items": {
                                "type": "object",
                                "properties": {
                                    "entity_name": {"type": "string"},
                                    "entity_type": {"type": "string"},
                                    "crimes_flagged": {
                                        "type": "array",
                                        "description": "List of crimes this entity is involved in",
                                        "items": {"type": "string", "enum": FINANCIAL_CRIMES}
                                    },
                                    "risk_level": {"type": "string", "enum": ["high", "medium", "low"]},
                                    "confidence": {"type": "number"},
                                    "evidence": {"type": "array", "items": {"type": "string"}},
                                    "reasoning": {"type": "string"}
                                },
                                "required": ["entity_name", "entity_type", "crimes_flagged", "risk_level", "confidence", "evidence", "reasoning"],
                                "additionalProperties": False
                            }
                        }
                    },
                    "required": ["flagged_entities"],
                    "additionalProperties": False
                }
            }
        }
    )

    result = json.loads(response.choices[0].message.content)
    return result.get('flagged_entities', [])


def main():
    import sys

    api_key = input("Enter your OpenAI API key: ") if len(sys.argv) < 2 else sys.argv[1]

    print(f"\n=== STEP 5: ANALYZE RISKS ===")
    print(f"Checking for {len(FINANCIAL_CRIMES)} financial crime types")

    # Read extracted text
    print("Reading extracted_text.txt...")
    try:
        with open("extracted_text.txt", "r", encoding="utf-8") as f:
            text = f.read()
    except FileNotFoundError:
        print("Error: extracted_text.txt not found. Run step1_summarize.py first.")
        sys.exit(1)

    # Read entity descriptions (try grouped first, fallback to original)
    entity_descriptions = None

    # Try grouped entities first (if step 4 was run)
    try:
        print("Reading grouped_entities.json...")
        with open("grouped_entities.json", "r", encoding="utf-8") as f:
            grouped_data = json.load(f)
            # Extract merged_descriptions
            merged = grouped_data.get("merged_descriptions", {})
            entity_descriptions = load_entity_descriptions_from_data(merged)
            print("Using grouped/deduplicated entities")
    except FileNotFoundError:
        # Fallback to original entity descriptions
        print("Reading entity_descriptions.json...")
        try:
            entity_descriptions = load_entity_descriptions("entity_descriptions.json")
            print("Using original entity descriptions")
        except FileNotFoundError:
            print("Error: entity_descriptions.json not found. Run step3_describe_entities.py first.")
            sys.exit(1)

    # Analyze document risk
    print("Analyzing document for financial crimes...")
    document_risk = analyze_document_risk(text, api_key)

    # Analyze entity risks
    print("Analyzing entity risks...")
    flagged_entities = analyze_entity_risks(entity_descriptions, api_key)

    # Combine results
    risk_assessment = {
        "document_risk": document_risk,
        "flagged_entities": flagged_entities,
        "crime_definitions": {crime: desc for crime, desc in zip(
            FINANCIAL_CRIMES,
            [line.split(' - ', 1)[1] if ' - ' in line else line
             for line in CRIME_DESCRIPTIONS.strip().split('\n') if line.strip() and not line.startswith('Look')]
        )}
    }

    # Save risk assessment
    with open("risk_assessment.json", "w", encoding="utf-8") as f:
        json.dump(risk_assessment, f, indent=2)

    print("Saved: risk_assessment.json")

    print(f"\nDocument Risk: {document_risk['overall_risk_level'].upper()}")
    print(f"Crimes Detected in Document: {', '.join(document_risk['crimes_detected']) if document_risk['crimes_detected'] else 'None'}")
    print(f"\nFlagged Entities: {len(flagged_entities)}")

    for entity in flagged_entities:
        print(f"\n  {entity['entity_name']} ({entity['entity_type']})")
        print(f"  Risk: {entity['risk_level'].upper()}")
        print(f"  Crimes: {', '.join(entity['crimes_flagged'])}")

    print("\n=== STEP 5 COMPLETE ===\n")


if __name__ == "__main__":
    main()
