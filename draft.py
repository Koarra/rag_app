from pydantic import BaseModel, Field
from typing import List, Dict

class EntityCrimes(BaseModel):
    crimes: List[str] = Field(description="List of crimes committed by the entity")
    evidence: str = Field(description="Supporting evidence or reasoning")

class CrimeAnalysis(BaseModel):
    entities: Dict[str, EntityCrimes] = Field(description="Mapping of entity names to their crimes and evidence")
