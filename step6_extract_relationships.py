"""
STEP 6: Extract entity relationships and create knowledge graph

Usage: python step6_extract_relationships.py
Reads: dict_unique_grouped_entity_summary.json, risk_assessment.json (from previous steps)
Output: Creates graph_elements.json with nodes and edges for visualization
"""

import json
from pydantic import BaseModel, Field
from typing import List
from azure.identity import DefaultAzureCredential, get_bearer_token_provider
from llama_index.core.program import LLMTextCompletionProgram
from llama_index.llms.azure_openai import AzureOpenAI


# Relationship types for compliance/risk assessment
RELATIONSHIP_TYPES = [
    "Owner",
    "Investor",
    "Partner",
    "Shareholder",
    "Representative",
    "Beneficiary",
    "Other relationship"
]


# Pydantic model for relationship extraction
class RelationshipExtraction(BaseModel):
    relationship: str = Field(description="Type of relationship between entities")
    reasoning: str = Field(description="Reasoning for the relationship classification")


def extract_entity_links(entities_dict):
    """Find which entities are mentioned in other entities' descriptions"""
    entity_links = {}

    for entity, description in entities_dict.items():
        linked = []
        for other_entity in entities_dict.keys():
            if other_entity != entity and other_entity in description:
                linked.append(other_entity)
        entity_links[entity] = linked

    return entity_links


def create_entity_pairs(entity_links):
    """Create unique pairs of connected entities"""
    pairs = set()

    for entity, linked_entities in entity_links.items():
        for linked in linked_entities:
            # Create sorted tuple to avoid duplicates (A,B) and (B,A)
            pair = tuple(sorted([entity, linked]))
            pairs.add(pair)

    return list(pairs)


def classify_relationship(entity1, description1, entity2, description2, llm):
    """Classify the relationship between two entities using LLM"""

    combined_description = f"{entity1}: {description1}\n{entity2}: {description2}"

    program = LLMTextCompletionProgram.from_defaults(
        output_cls=RelationshipExtraction,
        llm=llm,
        prompt_template_str="""You are a compliance assistant analyzing entity relationships.

Based on the descriptions below, identify which relationship type from {relationship_types} exists between {entity1} and {entity2}.

Relationship types:
{relationship_list}

Entity Descriptions:
{descriptions}

Classify the relationship and provide reasoning.
""",
        verbose=False
    )

    result = program(
        entity1=entity1,
        entity2=entity2,
        relationship_types=RELATIONSHIP_TYPES,
        relationship_list=", ".join(RELATIONSHIP_TYPES),
        descriptions=combined_description
    )

    return result


def main():
    import sys

    print(f"\n=== STEP 6: EXTRACT RELATIONSHIPS ===")

    # Read entity descriptions (try grouped first, fallback to original)
    entities_dict = None
    try:
        print("Reading dict_unique_grouped_entity_summary.json...")
        with open("dict_unique_grouped_entity_summary.json", "r", encoding="utf-8") as f:
            entities_dict = json.load(f)
        print("Using grouped entities")
    except FileNotFoundError:
        print("Reading entity_descriptions.json...")
        try:
            with open("entity_descriptions.json", "r", encoding="utf-8") as f:
                data = json.load(f)
            # Handle both formats
            if isinstance(data, dict) and "entities" not in data:
                entities_dict = data
            else:
                entities_dict = {e.get("entity", ""): e.get("description", "") for e in data.get("entities", [])}
            print("Using original entities")
        except FileNotFoundError:
            print("Error: No entity descriptions found. Run step3 or step4 first.")
            sys.exit(1)

    # Read flagged entities from risk assessment
    flagged_entities = set()
    try:
        print("Reading risk_assessment.json...")
        with open("risk_assessment.json", "r", encoding="utf-8") as f:
            risk_data = json.load(f)
        for entity in risk_data.get("flagged_entities", []):
            flagged_entities.add(entity["entity_name"])
        print(f"Found {len(flagged_entities)} flagged entities")
    except FileNotFoundError:
        print("Warning: risk_assessment.json not found. No entities will be flagged.")

    if not entities_dict:
        print("No entities found")
        sys.exit(1)

    print(f"Processing {len(entities_dict)} entities...")

    # Extract entity links
    print("Extracting entity links...")
    entity_links = extract_entity_links(entities_dict)

    # Create unique pairs
    entity_pairs = create_entity_pairs(entity_links)
    print(f"Found {len(entity_pairs)} entity pairs")

    # Initialize Azure OpenAI LLM
    llm = AzureOpenAI(
        engine="gpt-4o-mini",
        use_azure_ad=True,
        azure_ad_token_provider=get_bearer_token_provider(
            DefaultAzureCredential(), "https://cognitiveservices.azure.com/.default"
        )
    )

    # Classify relationships for each pair
    print("Classifying relationships...")
    relationships = []

    for i, (entity1, entity2) in enumerate(entity_pairs, 1):
        print(f"  [{i}/{len(entity_pairs)}] Analyzing {entity1} <-> {entity2}")

        try:
            result = classify_relationship(
                entity1,
                entities_dict[entity1],
                entity2,
                entities_dict[entity2],
                llm
            )

            relationship_data = {
                "entities": [entity1, entity2],
                "relationship": result.relationship,
                "reasoning": result.reasoning,
                "involves_flagged": entity1 in flagged_entities or entity2 in flagged_entities
            }

            relationships.append(relationship_data)
            print(f"    -> {result.relationship}")

        except Exception as e:
            print(f"    -> Error: {e}")

    # Save all relationships
    with open("entity_relationships.json", "w", encoding="utf-8") as f:
        json.dump(relationships, f, indent=2)
    print(f"\nSaved: entity_relationships.json")

    # Filter to keep only meaningful relationships (excluding "Other relationship")
    filtered_relationships = [r for r in relationships if r["relationship"] != "Other relationship"]

    with open("entity_relationships_filtered.json", "w", encoding="utf-8") as f:
        json.dump(filtered_relationships, f, indent=2)
    print(f"Saved: entity_relationships_filtered.json ({len(filtered_relationships)} meaningful relationships)")

    # Create graph structure
    print("\nCreating knowledge graph...")

    # Assign unique IDs to entities
    entity_to_id = {}
    current_id = 1

    for entity in entities_dict.keys():
        entity_to_id[entity] = current_id
        current_id += 1

    # Create nodes
    nodes = []
    for entity, entity_id in entity_to_id.items():
        node = {
            "data": {
                "id": entity_id,
                "label": "FLAGGED" if entity in flagged_entities else "PERSON",
                "name": entity
            }
        }
        nodes.append(node)

    # Create edges from filtered relationships
    edges = []
    for idx, rel in enumerate(filtered_relationships):
        edge = {
            "data": {
                "id": current_id + idx,
                "label": rel["relationship"],
                "source": entity_to_id[rel["entities"][0]],
                "target": entity_to_id[rel["entities"][1]]
            }
        }
        edges.append(edge)

    # Create graph elements structure
    graph_elements = {
        "nodes": nodes,
        "edges": edges
    }

    with open("graph_elements.json", "w", encoding="utf-8") as f:
        json.dump(graph_elements, f, indent=2)

    print(f"Saved: graph_elements.json")
    print(f"  Nodes: {len(nodes)}")
    print(f"  Edges: {len(edges)}")
    print(f"  Flagged entities: {len(flagged_entities)}")

    print("\n=== STEP 6 COMPLETE ===\n")


if __name__ == "__main__":
    main()
