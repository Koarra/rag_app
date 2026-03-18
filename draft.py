from pydantic import BaseModel
from typing import Type, TypeVar, Union, Dict, Any, Optional
from langchain_openai import AzureChatOpenAI
from langchain_core.messages import HumanMessage, SystemMessage
from openai import AzureOpenAI
import os
import math
from azure.identity import DefaultAzureCredential, get_bearer_token_provider

T = TypeVar("T", bound=BaseModel)

AZURE_ENDPOINT = os.getenv("AZURE_ENDPOINT", "https://domino.risklab-ch.aks.azure.ubs.net/aice-openai/")
token_provider = get_bearer_token_provider(DefaultAzureCredential(), "https://cognitiveservices.azure.com/.default")

model = AzureChatOpenAI(
    model="gpt-4o",
    azure_endpoint=AZURE_ENDPOINT,
    azure_ad_token_provider=token_provider,
    temperature=0,
    seed=0,
    logprobs=True,
    top_logprobs=5,
)

raw_client = AzureOpenAI(
    azure_endpoint=AZURE_ENDPOINT,
    azure_ad_token_provider=token_provider,
    api_version="2024-02-01",
)

SYSTEM_MESSAGE = "You are a helpful assistant."


def run_compliance_check(document_content: str, output_schema: Optional[Type[T]] = None):
    messages = [SystemMessage(content=SYSTEM_MESSAGE), HumanMessage(content=document_content)]

    if output_schema is None:
        response = model.invoke(messages)
        logprobs = response.response_metadata.get("logprobs", {}).get("content", [])
        return response.content, logprobs

    return model.with_structured_output(output_schema).invoke(messages), None


def get_prompt_logprobs(document_content: str, model_name: str = "gpt-35-turbo-instruct"):
    prompt = f"{SYSTEM_MESSAGE}\n\nUser: {document_content}\nAssistant:"
    response = raw_client.completions.create(
        model=model_name, prompt=prompt, max_tokens=0, echo=True, logprobs=5
    )
    return response.choices[0].logprobs


def print_logprobs(logprobs, is_prompt=False):
    label = "Prompt" if is_prompt else "Completion"
    print(f"\n[{label} logprobs]")

    tokens = logprobs.tokens if is_prompt else [t["token"] for t in logprobs]
    lps = logprobs.token_logprobs if is_prompt else [t["logprob"] for t in logprobs]
    tops = logprobs.top_logprobs if is_prompt else [t.get("top_logprobs", {}) for t in logprobs]

    for token, lp, top in zip(tokens, lps, tops):
        if lp is None:
            continue
        print(f"  {token!r:20} logprob: {lp:.4f}  prob: {math.exp(lp):.4f}")
        for alt, alt_lp in (top.items() if is_prompt else [(t["token"], t["logprob"]) for t in top]):
            print(f"    {alt!r:20} logprob: {alt_lp:.4f}  prob: {math.exp(alt_lp):.4f}")


class QuantumPhysicsSummary(BaseModel):
    explanation: str


if __name__ == "__main__":
    document_content = "Explain quantum physics in one sentence."

    output, logprobs = run_compliance_check(document_content)
    print("Response:", output)
    print_logprobs(logprobs)

    # NOTE: prompt logprobs require gpt-35-turbo-instruct, not gpt-4o
    prompt_logprobs = get_prompt_logprobs(document_content)
    print_logprobs(prompt_logprobs, is_prompt=True)

    output, _ = run_compliance_check(document_content, QuantumPhysicsSummary)
    print("\n[Structured output]")
    print(output.model_dump_json(indent=2))
