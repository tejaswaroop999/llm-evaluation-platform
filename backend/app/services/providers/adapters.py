"""Small provider boundary; the echo adapter is an explicitly synthetic demo."""
from dataclasses import dataclass
from typing import Protocol
import httpx


@dataclass(frozen=True)
class ModelOutput:
    text: str
    input_tokens: int | None = None
    output_tokens: int | None = None


class Provider(Protocol):
    name: str
    model: str

    def generate(self, prompt: str) -> ModelOutput: ...


class EchoProvider:
    name = "echo"
    model = "echo-v1"

    def generate(self, prompt: str) -> ModelOutput:
        return ModelOutput(text=prompt)


class ProviderError(Exception):
    """Safe failure description that excludes provider bodies and credentials."""


class AnthropicProvider:
    name = "anthropic"

    def __init__(self, api_key: str, model: str, transport=None):
        self.api_key = api_key
        self.model = model
        self.transport = transport

    def generate(self, prompt: str) -> ModelOutput:
        try:
            with httpx.Client(timeout=25.0, transport=self.transport) as client:
                response = client.post(
                    "https://api.anthropic.com/v1/messages",
                    headers={"x-api-key": self.api_key, "anthropic-version": "2023-06-01"},
                    json={"model": self.model, "max_tokens": 900,
                          "messages": [{"role": "user", "content": prompt}]},
                )
                response.raise_for_status()
                data = response.json()
                blocks = data.get("content", [])
                if not isinstance(blocks, list):
                    raise ValueError("Invalid blocks")
                text = "\n".join(block["text"] for block in blocks
                                 if isinstance(block, dict) and block.get("type") == "text"
                                 and isinstance(block.get("text"), str)).strip()
                if not text:
                    raise ProviderError("Provider returned empty text")
                usage = data.get("usage", {})
                def tokens(key):
                    value = usage.get(key) if isinstance(usage, dict) else None
                    return value if type(value) is int and value >= 0 else None
                return ModelOutput(text, tokens("input_tokens"), tokens("output_tokens"))
        except httpx.TimeoutException as exc:
            raise ProviderError("Provider timed out") from exc
        except httpx.HTTPStatusError as exc:
            raise ProviderError(f"Provider HTTP {exc.response.status_code}") from exc
        except httpx.RequestError as exc:
            raise ProviderError("Provider network failure") from exc
        except (ValueError, TypeError, AttributeError, KeyError) as exc:
            raise ProviderError("Invalid provider response") from exc
