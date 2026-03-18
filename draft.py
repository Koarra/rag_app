import os
import math
from typing import Type, TypeVar, Union, Dict, Any
from pydantic import BaseModel
from langchain_openai import AzureChatOpenAI
from langchain_core.messages import HumanMessage, SystemMessage
from azure.identity import DefaultAzureCredential, get_bearer_token_provider

T = TypeVar("T", bound=BaseModel)

AZURE_ENDPOINT = os.getenv("AZURE_ENDPOINT", "https://domino.risklab-ch.aks.azure.ubs.net/aice-openai/")

model = AzureChatOpenAI(
    model="gpt-4o",
    azure_endpoint=AZURE_ENDPOINT,
    azure_ad_token_provider=get_bearer_token_provider(
        DefaultAzureCredential(), "https://cognitiveservices.azure.com/.default"
    ),
    temperature=0,
    seed=0,
    logprobs=True,
    top_logprobs=5,
)

SYSTEM_MESSAGE = "You are a helpful assistant."


def run_compliance_check(content: str, output_schema: Type[T] | None = None):
    messages = [SystemMessage(content=SYSTEM_MESSAGE), HumanMessage(content=content)]

    if output_schema is None:
        response = model.invoke(messages)
        logprobs = response.response_metadata.get("logprobs", {}).get("content", [])
        return response.content, logprobs

    return model.with_structured_output(output_schema).invoke(messages), None


class QuantumPhysicsSummary(BaseModel):
    explanation: str


if __name__ == "__main__":
    output, logprobs = run_compliance_check("Explain quantum physics in one sentence.")
    print(output)

    for token_info in logprobs:
        print(f"{token_info['token']!r:20} {token_info['logprob']:.4f} ({math.exp(token_info['logprob']):.4f})")
