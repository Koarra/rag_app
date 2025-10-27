import json
from pydantic import BaseModel, Field
from typing import List, Dict
from azure.identity import DefaultAzureCredential, get_bearer_token_provider
from llama_index.core.base.llms.types import ChatMessage
from llama_index.embeddings.azure_openai import AzureOpenAIEmbedding
from risklab.openai.openai import get_llm_openai
from llama_index.llms.azure_openai import AzureOpenAI

# Your Pydantic models
class EntityCrimes(BaseModel):
    crimes: List[str] = Field(description="List of crimes committed by the entity")
    evidence: str = Field(description="Supporting evidence or reasoning")

class CrimeAnalysis(BaseModel):
    entities: Dict[str, EntityCrimes] = Field(description="Mapping of entity names to their crimes and evidence")

# Your LLM setup
llm = AzureOpenAI(
    engine="gpt-4o-mini",
    use_azure_ad=True,
    azure_ad_token_provider=get_bearer_token_provider(
        DefaultAzureCredential(), "https://cognitiveservices.azure.com/.default"
    )
)

# Example input
entities = {
    "John Doe": "John Doe was arrested for insider trading in 2021.",
    "ACME Corp": "ACME Corp was fined for environmental violations but not criminally charged."
}

# Create prompt
prompt = f"""You are a legal analyst. Analyze each entity and identify any crimes they appear to have committed.
Return a JSON strictly matching this schema:

Entities:
{json.dumps(entities, indent=2)}
"""

# Use structured_predict directly - this is the simplest approach
result = llm.structured_predict(
    output_cls=CrimeAnalysis,
    prompt=prompt
)

# Print the result
print(result.model_dump_json(indent=2))

# Or access specific fields
print("\nEntities analyzed:")
for entity_name, crime_info in result.entities.items():
    print(f"\n{entity_name}:")
    print(f"  Crimes: {crime_info.crimes}")
    print(f"  Evidence: {crime_info.evidence}")
