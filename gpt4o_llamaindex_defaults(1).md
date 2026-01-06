You can verify these values through the following official channels:

    LlamaIndex GitHub Source Code: The definitive source is the __init__ constructor of the AzureOpenAI class.

        File: llama_index/llms/azure_openai/base.py

        Evidence: Line definitions such as temperature: float = 0.1 and max_tokens: Optional[int] = None are hardcoded in the class arguments.

    LlamaIndex API Reference: The documentation for the LLM module explicitly lists these defaults for the OpenAI and AzureOpenAI providers.

        Link: LlamaIndex LLM API Reference - Azure OpenAI
