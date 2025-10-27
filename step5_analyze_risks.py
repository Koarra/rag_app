"""
STEP 5: Analyze risks - flag entities for financial crimes

Usage: python step5_analyze_risks.py
Reads: dict_unique_grouped_entity_summary.json (from step 4) OR entity_descriptions.json (from step 3)
Output: Creates risk_assessment.json with flagged entities
"""

import json
from pydantic import BaseModel, Field
from typing import List
from azure.identity import DefaultAzureCredential, get_bearer_token_provider
from llama_index.core.program import LLMTextCompletionProgram
from llama_index.llms.azure_openai import AzureOpenAI


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


# Pydantic models
class EntityRisk(BaseModel):
    entity_name: str = Field(description="The entity name")
    entity_type: str = Field(description="Type of entity (person or company)")
    crimes_flagged: List[str] = Field(description="List of crimes this entity is involved in")
    risk_level: str = Field(description="Risk level: high, medium, low, or none")
    confidence: float = Field(description="Confidence score between 0 and 1")
    evidence: List[str] = Field(description="Evidence supporting the flagged crimes")
    reasoning: str = Field(description="Reasoning for the assessment")


def analyze_entity(entity_name, entity_description, llm):
    """Analyze a single entity for financial crimes"""

    program = LLMTextCompletionProgram.from_defaults(
        output_cls=EntityRisk,
        llm=llm,
        prompt_template_str=f"""You are an expert in financial crime detection. Analyze if this entity is involved in any of these crimes:

{CRIME_DESCRIPTIONS}

Only flag crimes with credible evidence from the description.

Entity: {{entity_name}}
Description: {{entity_description}}

Determine if there is evidence of any financial crimes. Only use crimes from this list: {', '.join(FINANCIAL_CRIMES)}
""",
        verbose=False
    )

    result = program(entity_name=entity_name, entity_description=entity_description)
    return result


def main():
    import sys

    output_folder = Path(sys.argv[1]) if len(sys.argv) > 1 else Path(".")
    output_folder.mkdir(parents=True, exist_ok=True)

    print(f"\n=== STEP 5: ANALYZE RISKS ===")
    print(f"Output folder: {output_folder}")
    print(f"Checking for {len(FINANCIAL_CRIMES)} financial crime types")

    # Read entity descriptions (try grouped first, fallback to original)
    entities_dict = None
    try:
        print("Reading dict_unique_grouped_entity_summary.json...")
        with open(output_folder / "dict_unique_grouped_entity_summary.json", "r", encoding="utf-8") as f:
            data = json.load(f)
        # Check if it's the new dict format {"entity1": "desc1", ...}
        if isinstance(data, dict) and "entities" not in data:
            entities_dict = data
            print("Using grouped entities (dict format)")
        else:
            # Old format with "entities" list
            entities_dict = {e.get("entity", ""): e.get("description", "") for e in data.get("entities", [])}
            print("Using grouped entities (list format)")
    except FileNotFoundError:
        print("Reading entity_descriptions.json...")
        try:
            with open(output_folder / "entity_descriptions.json", "r", encoding="utf-8") as f:
                data = json.load(f)
            # Handle both formats: dict {"entity": "desc"} or list {"entities": [...]}
            if isinstance(data, dict) and "entities" in data:
                # Old list format
                entities_dict = {e.get("entity", ""): e.get("description", "") for e in data.get("entities", [])}
            else:
                # New dict format
                entities_dict = data
            print("Using original entities")
        except FileNotFoundError:
            print("Error: entity_descriptions.json not found. Run step3_describe_entities.py first.")
            sys.exit(1)

    if not entities_dict:
        print("No entities found in input file")
        sys.exit(1)

    print(f"Analyzing {len(entities_dict)} entities...")

    # Initialize Azure OpenAI LLM
    llm = AzureOpenAI(
        engine="gpt-4o-mini",
        use_azure_ad=True,
        azure_ad_token_provider=get_bearer_token_provider(
            DefaultAzureCredential(), "https://cognitiveservices.azure.com/.default"
        )
    )

    # Analyze each entity and build results progressively
    flagged_entities = []
    for i, (entity_name, entity_description) in enumerate(entities_dict.items(), 1):
        print(f"  [{i}/{len(entities_dict)}] Analyzing {entity_name}...")

        result = analyze_entity(entity_name, entity_description, llm)

        # Only add to flagged list if crimes were detected
        if result.crimes_flagged and result.risk_level != "none":
            flagged_entities.append(result.model_dump())
            print(f"    -> FLAGGED: {', '.join(result.crimes_flagged)}")

    # Save results
    risk_assessment = {"flagged_entities": flagged_entities}

    with open(output_folder / "risk_assessment.json", "w", encoding="utf-8") as f:
        json.dump(risk_assessment, f, indent=2)

    print(f"\nSaved: {output_folder}/risk_assessment.json")
    print(f"Flagged Entities: {len(flagged_entities)}/{len(entities)}")

    for entity in flagged_entities:
        print(f"\n  {entity['entity_name']} ({entity['entity_type']})")
        print(f"  Risk: {entity['risk_level'].upper()}")
        print(f"  Crimes: {', '.join(entity['crimes_flagged'])}")

    print("\n=== STEP 5 COMPLETE ===\n")


if __name__ == "__main__":
    main()
