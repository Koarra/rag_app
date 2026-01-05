# GPT-4o Default Parameters in LlamaIndex AzureOpenAI

## Overview

This document provides a comprehensive reference for the default parameter configuration when using GPT-4o through LlamaIndex's `AzureOpenAI` wrapper (`llama_index.llms.azure_openai.AzureOpenAI`).

## Why This Model Fits Our Requirements

### Application Context

Our application is a RAG (Retrieval-Augmented Generation) system designed to analyze PDF and DOCX documents for criminal entity detection. The pipeline performs multiple sequential operations:

- Document summarization
- Entity extraction from unstructured text
- Entity description and characterization
- Criminal entity flagging based on contextual analysis
- Relationship mapping between identified entities

### Model Selection Rationale

**GPT-4o via Azure OpenAI** is the optimal choice for this use case for several critical reasons:

1. **Deterministic Behavior for Legal/Compliance Applications**
   - The default temperature of 0.1 ensures consistent, reproducible results across document analyses
   - Critical for criminal entity detection where consistency and reliability are paramount
   - Reduces variability in entity extraction and classification decisions

2. **Strong Structured Extraction Capabilities**
   - GPT-4o excels at identifying and extracting named entities (persons, organizations, locations) from complex documents
   - Capable of understanding nuanced legal and criminal terminology
   - Maintains high accuracy in multi-step reasoning tasks required for relationship mapping

3. **RAG-Optimized Configuration**
   - LlamaIndex's default parameters are specifically tuned for retrieval-augmented generation workflows
   - Low temperature prioritizes factual accuracy over creative interpretation
   - Ideal for fact-based analysis where precision matters more than variety

4. **Enterprise Reliability via Azure**
   - Azure OpenAI provides enterprise-grade SLA, security, and compliance features
   - Essential for handling sensitive legal and criminal investigation documents
   - Offers data residency and privacy controls required for confidential information

5. **Multi-Step Pipeline Efficiency**
   - Single model handles all pipeline stages (summarization → extraction → flagging → relationships)
   - Consistent reasoning and context understanding across steps
   - Reduces complexity compared to managing multiple specialized models

6. **Contextual Understanding for Criminal Flagging**
   - GPT-4o's advanced reasoning capabilities can identify implicit criminal indicators
   - Understands relationships and patterns that rule-based systems would miss
   - Can distinguish between legitimate business activities and suspicious behavior based on context

### Why Not Alternatives?

- **Smaller models (GPT-3.5, GPT-4o-mini)**: Insufficient reasoning capability for complex entity relationship analysis
- **Higher temperature settings**: Would introduce unwanted variability in critical legal determinations
- **Open-source LLMs**: Lack the consistent accuracy and reliability needed for criminal detection applications
- **Domain-specific models**: Generally less capable at multi-task pipelines and nuanced reasoning

### Alignment with Default Parameters

The LlamaIndex default configuration perfectly matches our requirements:

- **Temperature 0.1**: Ensures factual, consistent entity extraction and classification
- **Max tokens = None**: Allows comprehensive analysis of lengthy legal documents
- **Single completion (n=1)**: Appropriate for deterministic decision-making
- **No streaming**: Better for processing complete documents and maintaining context
- **No random seed**: Acceptable since low temperature already provides consistency

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
