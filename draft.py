from pydantic import BaseModel
from typing import Type, TypeVar, Union, Dict, Any, Optional, Tuple
from langchain_openai import AzureChatOpenAI
from langchain_core.messages import HumanMessage, SystemMessage
from openai import AzureOpenAI
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

token_provider = get_bearer_token_provider(
    DefaultAzureCredential(), "https://cognitiveservices.azure.com/.default"
)

AZURE_OPENAI_LLM_CONFIG: Dict[str, Any] = {
    "model": "gpt-4o",
    "azure_endpoint": AZURE_ENDPOINT,
    "azure_ad_token_provider": token_provider,
    "temperature": 0,
    "seed": 0,
    "logprobs": True,
    "top_logprobs": 5,
}

model = AzureChatOpenAI(**AZURE_OPENAI_LLM_CONFIG)

# Raw AzureOpenAI client for prompt logprobs (legacy completions endpoint)
raw_client = AzureOpenAI(
    azure_endpoint=AZURE_ENDPOINT,
    azure_ad_token_provider=token_provider,
    api_version="2024-02-01",
)

# Define a system message for compliance checks
GENERAL_SYSTEM_MESSAGE = "You are a helpful assistant."


def get_prompt_logprobs(prompt: str, model_name: str = "gpt-4o") -> list:
    """
    Get logprobs for the prompt tokens using the legacy completions endpoint with echo=True.
    Note: Only works with models that support the completions endpoint (e.g. gpt-35-turbo-instruct).
          For gpt-4o, this will raise an error — see note below.
    """
    response = raw_client.completions.create(
        model=model_name,
        prompt=prompt,
        max_tokens=0,       # we don't want any new tokens generated
        echo=True,          # echo back the prompt with logprobs
        logprobs=5,         # top N logprobs per token
    )
    return response.choices[0].logprobs


def format_prompt(document_content: str) -> str:
    """Format the system + user message as a plain string for the completions endpoint."""
    return f"{GENERAL_SYSTEM_MESSAGE}\n\nUser: {document_content}\nAssistant:"


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

    # Note: logprobs not available with structured output
    structured_model = model.with_structured_output(output_schema)
    return structured_model.invoke(messages), None


def print_completion_logprobs(logprobs: list) -> None:
    """Pretty print completion logprobs."""
    print("\n[Completion Logprobs]")
    for token_info in logprobs:
        prob = math.exp(token_info["logprob"])
        print(
            f"  Token: {token_info['token']!r:20} "
            f"logprob: {token_info['logprob']:.4f}  "
            f"prob: {prob:.4f}"
        )
        if token_info.get("top_logprobs"):
            for alt in token_info["top_logprobs"]:
                alt_prob = math.exp(alt["logprob"])
                print(
                    f"    alt: {alt['token']!r:20} "
                    f"logprob: {alt['logprob']:.4f}  "
                    f"prob: {alt_prob:.4f}"
                )


def print_prompt_logprobs(prompt_logprobs) -> None:
    """Pretty print prompt logprobs from the completions endpoint."""
    print("\n[Prompt Logprobs]")
    for token, logprob, top_lps in zip(
        prompt_logprobs.tokens,
        prompt_logprobs.token_logprobs,
        prompt_logprobs.top_logprobs,
    ):
        if logprob is None:
            continue  # first token has no logprob
        prob = math.exp(logprob)
        print(
            f"  Token: {token!r:20} "
            f"logprob: {logprob:.4f}  "
            f"prob: {prob:.4f}"
        )
        if top_lps:
            for alt_token, alt_logprob in top_lps.items():
                alt_prob = math.exp(alt_logprob)
                print(
                    f"    alt: {alt_token!r:20} "
                    f"logprob: {alt_logprob:.4f}  "
                    f"prob: {alt_prob:.4f}"
                )


# Define the Pydantic schema for structured output
class QuantumPhysicsSummary(BaseModel):
    explanation: str


# Example use case
if __name__ == "__main__":
    document_content = "Explain quantum physics in one sentence."

    # --- Completion logprobs (Chat Completions API) ---
    print("=== Raw Text Output + Completion Logprobs ===")
    try:
        output, logprobs = run_compliance_check(document_content)
        print("Response:", output)
        if logprobs:
            print_completion_logprobs(logprobs)
    except Exception as e:
        print(f"Error: {e}")

    # --- Prompt logprobs (Legacy Completions API with echo=True) ---
    # NOTE: This requires a model that supports the completions endpoint,
    #       e.g. "gpt-35-turbo-instruct". GPT-4o does NOT support it.
    #       Change the model_name below accordingly.
    print("\n=== Prompt Logprobs ===")
    try:
        prompt = format_prompt(document_content)
        prompt_logprobs = get_prompt_logprobs(prompt, model_name="gpt-35-turbo-instruct")
        print_prompt_logprobs(prompt_logprobs)
    except Exception as e:
        print(f"Error (prompt logprobs): {e}")

    # --- Structured output (no logprobs) ---
    print("\n=== Structured Output ===")
    try:
        output, _ = run_compliance_check(document_content, QuantumPhysicsSummary)
        if isinstance(output, QuantumPhysicsSummary):
            print(output.model_dump_json(indent=2))
        print("(logprobs not available with structured output)")
    except Exception as e:
        print(f"Error: {e}")
