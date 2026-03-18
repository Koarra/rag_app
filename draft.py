from pydantic import BaseModel
from typing import Type, TypeVar, Union, Dict, Any, Optional, Tuple
from langchain_openai import AzureChatOpenAI
from langchain_core.messages import HumanMessage, SystemMessage
import os
import math
from azure.identity import DefaultAzureCredential, get_bearer_token_provider

# Define a generic type for Pydantic models
T = TypeVar("T", bound=BaseModel)

# Azure OpenAI Configuration
AZURE_ENDPOINT = os.getenv(
    "AZURE_ENDPOINT",
    "https://domino.risklab-ch.aks.azure.ubs.net/aice-openai/"
)

AZURE_OPENAI_LLM_CONFIG: Dict[str, Any] = {
    "model": "gpt-4o",
    "azure_endpoint": AZURE_ENDPOINT,
    "azure_ad_token_provider": get_bearer_token_provider(
        DefaultAzureCredential(), "https://cognitiveservices.azure.com/.default"
    ),
    "temperature": 0,
    "seed": 0,
    "logprobs": True,
    "top_logprobs": 5,
}

model = AzureChatOpenAI(**AZURE_OPENAI_LLM_CONFIG)

# Define a system message for compliance checks
GENERAL_SYSTEM_MESSAGE = "You are a helpful assistant."

# Define the compliance check function
def run_compliance_check(
    document_content: str,
    output_schema: Type[T] | None = None
) -> Tuple[Union[T, str], Optional[list]]:
    messages = [
        SystemMessage(content=GENERAL_SYSTEM_MESSAGE),
        HumanMessage(content=document_content)
    ]
    if output_schema is None:
        response = model.invoke(messages)
        content = response.content
        logprobs = response.response_metadata.get("logprobs", {}).get("content", [])
        return content, logprobs

    # Note: logprobs are not available with structured output
    structured_model = model.with_structured_output(output_schema)
    return structured_model.invoke(messages), None

# Define the Pydantic schema for structured output
class QuantumPhysicsSummary(BaseModel):
    explanation: str

# Example use case
if __name__ == "__main__":
    # Input for the assistant
    document_content = "Explain quantum physics in one sentence."

    # --- Example 1: Raw text output with logprobs ---
    print("=== Raw Text Output ===")
    try:
        output, logprobs = run_compliance_check(document_content)
        print("Response:", output)

        if logprobs:
            print("\nLogprobs:")
            for token_info in logprobs:
                prob = math.exp(token_info["logprob"])
                print(
                    f"  Token: {token_info['token']!r:20} "
                    f"logprob: {token_info['logprob']:.4f}  "
                    f"prob: {prob:.4f}"
                )

                # Optional: print top alternative tokens
                if token_info.get("top_logprobs"):
                    for alt in token_info["top_logprobs"]:
                        alt_prob = math.exp(alt["logprob"])
                        print(
                            f"    alt: {alt['token']!r:20} "
                            f"logprob: {alt['logprob']:.4f}  "
                            f"prob: {alt_prob:.4f}"
                        )

    except Exception as e:
        print(f"Error: {e}")

    # --- Example 2: Structured output (no logprobs) ---
    print("\n=== Structured Output ===")
    try:
        output, logprobs = run_compliance_check(document_content, QuantumPhysicsSummary)

        if isinstance(output, QuantumPhysicsSummary):
            print(output.model_dump_json(indent=2))
        else:
            print(output)

        if logprobs is None:
            print("(logprobs not available with structured output)")

    except Exception as e:
        print(f"Error: {e}")
