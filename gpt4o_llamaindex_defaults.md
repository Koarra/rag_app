# GPT-4o Default Parameters in LlamaIndex AzureOpenAI

## Overview

This document provides a comprehensive reference for the default parameter configuration when using GPT-4o through LlamaIndex's `AzureOpenAI` wrapper (`llama_index.llms.azure_openai.AzureOpenAI`).

## Model Configuration

**Model:** `gpt-4o`  
**Provider:** Azure OpenAI (via LlamaIndex)

## Default Parameters

When parameters are not explicitly configured, LlamaIndex applies the following defaults:

| Parameter | Default Value | Description |
|-----------|---------------|-------------|
| `temperature` | `0.1` | Controls randomness in responses (lower = more deterministic) |
| `top_p` | `1.0` | Nucleus sampling threshold |
| `max_tokens` | `None` | Maximum completion length (model/service decides) |
| `frequency_penalty` | `0.0` | Reduces likelihood of repeating tokens based on frequency |
| `presence_penalty` | `0.0` | Reduces likelihood of repeating any tokens |
| `logprobs` | `None` | Whether to return log probabilities |
| `top_logprobs` | `0` | Number of most likely tokens to return at each position |
| `n` | `1` | Number of completions to generate |
| `stream` | `False` | Whether to stream responses |
| `seed` | `None` | Random seed for deterministic generation |
| `stop` | `None` | Sequences where the API will stop generating |
| `timeout` | `None` | Request timeout duration |
| `additional_kwargs` | `{}` | Additional provider-specific parameters |

## Key Considerations

### Temperature Setting

LlamaIndex intentionally sets a **low temperature of 0.1** by default. This differs from the standard OpenAI API default (typically 1.0) and is optimized for:

- Deterministic behavior in RAG (Retrieval-Augmented Generation) applications
- Consistent responses for similar queries
- Factual accuracy over creative variation

### Parameter Inheritance

The `AzureOpenAI` class in LlamaIndex inherits its default parameters from the base OpenAI LLM wrapper. These are LlamaIndex-specific defaults, not Azure OpenAI service defaults.

### Important Note

Azure OpenAI service defaults are **not applied** when using LlamaIndex's wrapper. The framework controls parameter defaults to ensure consistent behavior across different deployment types.

## Verification Methods

To inspect the current configuration at runtime:

- Print the entire LLM object to see all configured parameters
- Access individual parameter attributes directly (e.g., `temperature`, `top_p`, `max_tokens`)

## Best Practices

1. **Explicit Configuration:** Always set critical parameters explicitly in your code to avoid ambiguity and ensure reproducibility.

2. **Document Your Settings:** Include parameter configurations in your project documentation or code comments.

3. **Test Behavior:** Verify that default parameters meet your application's requirements, especially for production deployments.

4. **Monitor Changes:** Be aware that LlamaIndex updates may modify default values. Pin library versions for critical applications.

## References

- LlamaIndex OpenAI LLM API documentation
- LlamaIndex examples and tutorials
- Azure OpenAI Service documentation

---

*Last Updated: January 2026*
