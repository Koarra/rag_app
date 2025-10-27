import json
from pydantic import BaseModel, Field
from typing import List, Dict
from azure.identity import DefaultAzureCredential, get_bearer_token_provider
from llama_index.core.program import LLMTextCompletionProgram
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

# Create the program
program = LLMTextCompletionProgram.from_defaults(
    output_cls=CrimeAnalysis,
    llm=llm,
    prompt_template_str="""You are a legal analyst. Analyze each entity and identify any crimes they appear to have committed.
Return a JSON strictly matching this schema:

Entities:
{entities_str}
""",
    verbose=True
)

# Call the program
result = program(entities_str=json.dumps(entities, indent=2))

# Print the result
print(result.model_dump_json(indent=2))
