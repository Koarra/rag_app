"""
STEP 4: Analyze risks - flag entities for money laundering and sanctions evasion

Usage: python step4_analyze_risks.py
Reads: extracted_text.txt, entity_descriptions.json (from previous steps)
Output: Creates risk_assessment.json with flagged entities
"""

import json
from openai import OpenAI


def analyze_document_risk(text, api_key):
    """Analyze document for money laundering and sanctions evasion"""
    client = OpenAI(api_key=api_key)

    text_to_analyze = text[:15000]

    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {
                "role": "system",
                "content": "You are a financial crime analyst. Analyze documents for money laundering and sanctions evasion."
            },
            {
                "role": "user",
                "content": f"""Analyze this document for money laundering and sanctions evasion indicators.

MONEY LAUNDERING INDICATORS:
• Unusual transaction patterns
• Shell companies or front companies
• Layering activities
• Structuring/Smurfing
• High-risk jurisdictions
• Rapid movement of funds

SANCTIONS EVASION INDICATORS:
• Transactions with sanctioned countries
• Use of front companies
• Re-routing through third countries
• False documentation
• Sanctioned individuals/entities
• Prohibited goods

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
                        "money_laundering_risk": {"type": "string", "enum": ["high", "medium", "low", "none"]},
                        "sanctions_evasion_risk": {"type": "string", "enum": ["high", "medium", "low", "none"]},
                        "red_flags": {"type": "array", "items": {"type": "string"}},
                        "suspicious_patterns": {"type": "array", "items": {"type": "string"}},
                        "analysis_summary": {"type": "string"}
                    },
                    "required": ["overall_risk_level", "money_laundering_risk", "sanctions_evasion_risk", "red_flags", "suspicious_patterns", "analysis_summary"],
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
    for name, info in list(entity_descriptions.items())[:10]:
        context = f"""Entity: {name}
Type: {info.get('type', 'unknown')}
Role: {info.get('role', 'unknown')}
Description: {info.get('description', 'No description')}
Activities: {', '.join(info.get('key_activities', []))}"""
        entity_contexts.append(context)

    all_contexts = "\n\n".join(entity_contexts)

    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {
                "role": "system",
                "content": "You are an expert in financial crime detection. Only flag entities with credible evidence."
            },
            {
                "role": "user",
                "content": f"""Analyze these entities for involvement in money laundering or sanctions evasion.
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
                                    "crimes_flagged": {"type": "array", "items": {"type": "string", "enum": ["money_laundering", "sanctions_evasion"]}},
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

    print(f"\n=== STEP 4: ANALYZE RISKS ===")

    # Read extracted text
    print("Reading extracted_text.txt...")
    try:
        with open("extracted_text.txt", "r", encoding="utf-8") as f:
            text = f.read()
    except FileNotFoundError:
        print("Error: extracted_text.txt not found. Run step1_summarize.py first.")
        sys.exit(1)

    # Read entity descriptions
    print("Reading entity_descriptions.json...")
    try:
        with open("entity_descriptions.json", "r", encoding="utf-8") as f:
            entity_descriptions = json.load(f)
    except FileNotFoundError:
        print("Error: entity_descriptions.json not found. Run step3_describe_entities.py first.")
        sys.exit(1)

    # Analyze document risk
    print("Analyzing document risks...")
    document_risk = analyze_document_risk(text, api_key)

    # Analyze entity risks
    print("Analyzing entity risks...")
    flagged_entities = analyze_entity_risks(entity_descriptions, api_key)

    # Combine results
    risk_assessment = {
        "document_risk": document_risk,
        "flagged_entities": flagged_entities
    }

    # Save risk assessment
    with open("risk_assessment.json", "w", encoding="utf-8") as f:
        json.dump(risk_assessment, f, indent=2)

    print("Saved: risk_assessment.json")

    print(f"\nDocument Risk: {document_risk['overall_risk_level'].upper()}")
    print(f"Money Laundering Risk: {document_risk['money_laundering_risk'].upper()}")
    print(f"Sanctions Evasion Risk: {document_risk['sanctions_evasion_risk'].upper()}")
    print(f"\nFlagged Entities: {len(flagged_entities)}")

    for entity in flagged_entities:
        print(f"\n  {entity['entity_name']} ({entity['entity_type']})")
        print(f"  Risk: {entity['risk_level'].upper()}")
        print(f"  Crimes: {', '.join(entity['crimes_flagged'])}")

    print("\n=== STEP 4 COMPLETE ===\n")


if __name__ == "__main__":
    main()
