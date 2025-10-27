"""
STEP 5: Analyze risks - flag entities for financial crimes

Usage: python step5_analyze_risks.py
Reads: dict_unique_grouped_entity_summary.json (from step 4) OR entity_descriptions.json (from step 3)
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


def analyze_entity(entity_name, entity_description, client):
    """Analyze a single entity for financial crimes"""

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {
                "role": "system",
                "content": f"""You are an expert in financial crime detection. Analyze if this entity is involved in any of these crimes:

{CRIME_DESCRIPTIONS}

Only flag crimes with credible evidence from the description."""
            },
            {
                "role": "user",
                "content": f"""Analyze this entity for financial crime involvement:

Entity: {entity_name}
Description: {entity_description}

Determine if there is evidence of any financial crimes."""
            }
        ],
        temperature=0.1,
        response_format={
            "type": "json_schema",
            "json_schema": {
                "name": "entity_risk",
                "strict": True,
                "schema": {
                    "type": "object",
                    "properties": {
                        "entity_name": {"type": "string"},
                        "entity_type": {"type": "string"},
                        "crimes_flagged": {
                            "type": "array",
                            "items": {"type": "string", "enum": FINANCIAL_CRIMES}
                        },
                        "risk_level": {"type": "string", "enum": ["high", "medium", "low", "none"]},
                        "confidence": {"type": "number"},
                        "evidence": {"type": "array", "items": {"type": "string"}},
                        "reasoning": {"type": "string"}
                    },
                    "required": ["entity_name", "entity_type", "crimes_flagged", "risk_level", "confidence", "evidence", "reasoning"],
                    "additionalProperties": False
                }
            }
        }
    )

    return json.loads(response.choices[0].message.content)


def main():
    import sys

    api_key = input("Enter your OpenAI API key: ") if len(sys.argv) < 2 else sys.argv[1]

    print(f"\n=== STEP 5: ANALYZE RISKS ===")
    print(f"Checking for {len(FINANCIAL_CRIMES)} financial crime types")

    # Read entity descriptions (try grouped first, fallback to original)
    data = None
    try:
        print("Reading dict_unique_grouped_entity_summary.json...")
        with open("dict_unique_grouped_entity_summary.json", "r", encoding="utf-8") as f:
            data = json.load(f)
        print("Using grouped entities")
    except FileNotFoundError:
        print("Reading entity_descriptions.json...")
        try:
            with open("entity_descriptions.json", "r", encoding="utf-8") as f:
                data = json.load(f)
            print("Using original entities")
        except FileNotFoundError:
            print("Error: entity_descriptions.json not found. Run step3_describe_entities.py first.")
            sys.exit(1)

    # Extract entities list
    entities = data.get("entities", [])
    if not entities:
        print("No entities found in input file")
        sys.exit(1)

    print(f"Analyzing {len(entities)} entities...")

    # Initialize OpenAI client
    client = OpenAI(api_key=api_key)

    # Analyze each entity and build results progressively
    flagged_entities = []
    for i, entity_data in enumerate(entities, 1):
        entity_name = entity_data.get("entity", "")
        entity_description = entity_data.get("description", "")

        print(f"  [{i}/{len(entities)}] Analyzing {entity_name}...")

        result = analyze_entity(entity_name, entity_description, client)

        # Only add to flagged list if crimes were detected
        if result.get("crimes_flagged") and result["risk_level"] != "none":
            flagged_entities.append(result)
            print(f"    -> FLAGGED: {', '.join(result['crimes_flagged'])}")

    # Save results
    risk_assessment = {"flagged_entities": flagged_entities}

    with open("risk_assessment.json", "w", encoding="utf-8") as f:
        json.dump(risk_assessment, f, indent=2)

    print(f"\nSaved: risk_assessment.json")
    print(f"Flagged Entities: {len(flagged_entities)}/{len(entities)}")

    for entity in flagged_entities:
        print(f"\n  {entity['entity_name']} ({entity['entity_type']})")
        print(f"  Risk: {entity['risk_level'].upper()}")
        print(f"  Crimes: {', '.join(entity['crimes_flagged'])}")

    print("\n=== STEP 5 COMPLETE ===\n")


if __name__ == "__main__":
    main()
