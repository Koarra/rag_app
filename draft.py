from llama_index.llms.openai import OpenAI
from pydantic import BaseModel, Field
from typing import List, Dict

# 1️⃣ Define schema
class EntityCrimes(BaseModel):
    crimes: List[str] = Field(description="List of crimes committed by the entity")
    evidence: str = Field(description="Supporting evidence or reasoning")

class CrimeAnalysis(BaseModel):
    entities: Dict[str, EntityCrimes] = Field(description="Mapping of entity names to their crimes and evidence")

# 2️⃣ Create LLM and structured wrapper
llm = OpenAI(model="gpt-4o-mini")
structured_llm = llm.as_structured_llm(output_cls=CrimeAnalysis)

# 3️⃣ Example input
entities = {
    "John Doe": "John Doe was arrested for insider trading in 2021.",
    "ACME Corp": "ACME Corp was fined for environmental violations but not criminally charged."
}

prompt = f"""
You are a legal analyst. Analyze each entity and identify any crimes they appear to have committed.
Return a JSON strictly matching this schema:

{CrimeAnalysis.model_json_schema()}

Entities:
{entities}
"""

# 4️⃣ Get structured output
result = structured_llm.complete(prompt)

print(result)
print(result.entities["John Doe"].crimes)
print(result.entities["John Doe"].evidence)
