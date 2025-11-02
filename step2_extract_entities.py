"""
STEP 2: Extract persons and companies from document

Usage: python step2_extract_entities.py
Reads: extracted_text.txt (from step 1)
Output: Creates entities.json with list of persons and companies
"""

import json
import sys
from pathlib import Path
from pydantic import BaseModel, Field
from typing import List
from azure.identity import DefaultAzureCredential, get_bearer_token_provider
from llama_index.core.program import LLMTextCompletionProgram
from llama_index.llms.azure_openai import AzureOpenAI


# Pydantic model
class Entities(BaseModel):
    persons: List[str] = Field(description="List of person names found in the document")
    companies: List[str] = Field(description="List of company/organization names found in the document")


def extract_entities(text, llm):
    """Extract persons and companies using LlamaIndex"""

    # Limit text to 15000 characters
    text_to_analyze = text[:15000]

    program = LLMTextCompletionProgram.from_defaults(
        output_cls=Entities,
        llm=llm,
        prompt_template_str="""You are an expert at extracting entities from documents.

Extract all persons and companies from this document.

Guidelines:
- Persons: Full names of individuals (e.g., "John Smith", "Dr. Jane Doe")
- Companies: Company names, organizations, institutions (e.g., "ABC Corporation", "Ministry of Finance")
- Be thorough - extract all entities mentioned

Document:
{document_text}
""",
        verbose=False
    )

    result = program(document_text=text_to_analyze)
    return result


def main():
    if len(sys.argv) < 2:
        print("Usage: python step2_extract_entities.py <output_folder>")
        sys.exit(1)

    output_folder = Path(sys.argv[1])

    # Check if output_folder is a file instead of a directory
    if output_folder.exists() and output_folder.is_file():
        print(f"Error: {output_folder} is a file, not a directory!")
        print("Please provide a directory path for output_folder")
        sys.exit(1)

    output_folder.mkdir(parents=True, exist_ok=True)

    print(f"\n=== STEP 2: EXTRACT ENTITIES ===")
    print(f"Output folder: {output_folder}")

    # Read extracted text from step 1
    print("Reading extracted_text.txt...")
    try:
        with open(output_folder / "extracted_text.txt", "r", encoding="utf-8") as f:
            text = f.read()
    except FileNotFoundError:
        print("Error: extracted_text.txt not found. Run step1_summarize.py first.")
        sys.exit(1)

    # Initialize Azure OpenAI LLM
    llm = AzureOpenAI(
        engine="gpt-4o",
        use_azure_ad=True,
        azure_ad_token_provider=get_bearer_token_provider(
            DefaultAzureCredential(), "https://cognitiveservices.azure.com/.default"
        )
    )

    # Extract entities
    print("Extracting entities...")
    result = extract_entities(text, llm)

    # Save entities
    output = result.model_dump()

    with open(output_folder / "entities.json", "w", encoding="utf-8") as f:
        json.dump(output, f, indent=2)

    print(f"Saved: {output_folder}/entities.json")
    print(f"\nFound {len(output['persons'])} person(s)")
    print(f"Found {len(output['companies'])} company/companies")

    print(f"\nPersons: {output['persons']}")
    print(f"\nCompanies: {output['companies']}")

    print("\n=== STEP 2 COMPLETE ===\n")


if __name__ == "__main__":
    main()
