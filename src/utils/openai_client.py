"""
Centralized OpenAI API client with error handling and retry logic
"""
import time
import json
from typing import Dict, List, Optional, Any
from openai import OpenAI, APIError, RateLimitError, APIConnectionError
from .config import Config


class OpenAIClient:
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or Config.OPENAI_API_KEY
        self.client = OpenAI(api_key=self.api_key)

    def _call_with_retry(self, func, *args, **kwargs) -> Any:
        """Execute OpenAI API call with exponential backoff retry"""
        for attempt in range(Config.MAX_RETRIES):
            try:
                return func(*args, **kwargs)
            except RateLimitError as e:
                if attempt == Config.MAX_RETRIES - 1:
                    raise
                wait_time = Config.RETRY_DELAY * (2 ** attempt)
                print(f"Rate limit hit. Waiting {wait_time}s before retry...")
                time.sleep(wait_time)
            except APIConnectionError as e:
                if attempt == Config.MAX_RETRIES - 1:
                    raise
                wait_time = Config.RETRY_DELAY * (2 ** attempt)
                print(f"Connection error. Waiting {wait_time}s before retry...")
                time.sleep(wait_time)
            except APIError as e:
                print(f"API Error: {e}")
                raise

    def chat_completion(
        self,
        messages: List[Dict[str, str]],
        model: str,
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
        response_format: Optional[Dict] = None
    ) -> str:
        """
        Make a chat completion request

        Args:
            messages: List of message dicts with 'role' and 'content'
            model: Model name (e.g., 'gpt-4', 'gpt-3.5-turbo')
            temperature: Sampling temperature (0-2)
            max_tokens: Maximum tokens in response
            response_format: Optional response format for structured outputs

        Returns:
            Response content as string
        """
        def _make_request():
            kwargs = {
                "model": model,
                "messages": messages,
                "temperature": temperature,
            }

            if max_tokens:
                kwargs["max_tokens"] = max_tokens

            if response_format:
                kwargs["response_format"] = response_format

            response = self.client.chat.completions.create(**kwargs)
            return response.choices[0].message.content

        return self._call_with_retry(_make_request)

    def chat_completion_json(
        self,
        messages: List[Dict[str, str]],
        model: str,
        json_schema: Dict,
        temperature: float = 0.7,
        max_tokens: Optional[int] = None
    ) -> Dict:
        """
        Make a chat completion request with structured JSON output

        Args:
            messages: List of message dicts
            model: Model name
            json_schema: JSON schema for structured output
            temperature: Sampling temperature
            max_tokens: Maximum tokens

        Returns:
            Parsed JSON response as dict
        """
        response_format = {
            "type": "json_schema",
            "json_schema": json_schema
        }

        response_text = self.chat_completion(
            messages=messages,
            model=model,
            temperature=temperature,
            max_tokens=max_tokens,
            response_format=response_format
        )

        return json.loads(response_text)

    def estimate_tokens(self, text: str) -> int:
        """
        Rough estimation of tokens (actual tokenization may differ)
        Rule of thumb: ~4 characters per token for English
        """
        return len(text) // 4
