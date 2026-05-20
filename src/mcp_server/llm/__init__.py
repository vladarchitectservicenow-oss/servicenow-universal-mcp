# Copyright (c) 2026 Vlady
# SPDX-License-Identifier: AGPL-3.0-only

"""LLM abstraction — единый интерфейс для всех провайдеров.

Поддерживает: OpenAI, Anthropic, DeepSeek, Ollama, OpenRouter.
Все используют OpenAI-совместимый API, кроме Anthropic (свой SDK).
"""

from __future__ import annotations

import json
from typing import Any

from .config import LLMConfig


class LLMProvider:
    """Abstract LLM provider — фабрика для конкретных реализаций."""

    def __init__(self, config: LLMConfig):
        self.config = config
        self._client = self._build_client()

    def _build_client(self):
        provider = self.config.provider

        if provider == "anthropic":
            return AnthropicAdapter(self.config)
        else:
            # OpenAI-совместимый (OpenAI, DeepSeek, Ollama, OpenRouter)
            return OpenAIAdapter(self.config)

    async def chat(self, messages: list[dict], tools: list[dict] | None = None) -> dict:
        """Send chat completion request. Returns OpenAI-format response."""
        return await self._client.chat(messages, tools)

    def extract_tool_calls(self, response: dict) -> list[dict]:
        """Extract tool calls from response."""
        return self._client.extract_tool_calls(response)

    def extract_text(self, response: dict) -> str:
        """Extract text content from response."""
        return self._client.extract_text(response)

    @property
    def model(self) -> str:
        return self.config.model


class OpenAIAdapter:
    """Adapter for OpenAI-совместимых API (OpenAI, DeepSeek, Ollama, OpenRouter)."""

    def __init__(self, config: LLMConfig):
        import openai

        self.model = config.model
        self.client = openai.AsyncOpenAI(
            api_key=config.api_key,
            base_url=config.base_url,
        )

    async def chat(self, messages: list[dict], tools: list[dict] | None = None) -> dict:
        kwargs: dict[str, Any] = {
            "model": self.model,
            "messages": messages,
            "temperature": 0.1,
        }
        if tools:
            # Преобразуем в OpenAI tool format
            openai_tools = [{"type": "function", "function": t} for t in tools]
            kwargs["tools"] = openai_tools
            kwargs["tool_choice"] = "auto"

        resp = await self.client.chat.completions.create(**kwargs)
        return resp.model_dump()

    def extract_tool_calls(self, response: dict) -> list[dict]:
        choice = response["choices"][0]["message"]
        raw = choice.get("tool_calls", [])
        return [
            {
                "id": tc["id"],
                "name": tc["function"]["name"],
                "arguments": json.loads(tc["function"]["arguments"]),
            }
            for tc in raw
        ]

    def extract_text(self, response: dict) -> str:
        return response["choices"][0]["message"].get("content", "") or ""


class AnthropicAdapter:
    """Adapter for Anthropic Claude native API."""

    def __init__(self, config: LLMConfig):
        import anthropic

        self.model = config.model
        self.client = anthropic.AsyncAnthropic(api_key=config.api_key)

    async def chat(self, messages: list[dict], tools: list[dict] | None = None) -> dict:
        # Anthropic expects system message separately
        system = ""
        user_messages = []
        for m in messages:
            if m["role"] == "system":
                system = m["content"]
            else:
                user_messages.append(m)

        kwargs: dict[str, Any] = {
            "model": self.model,
            "messages": user_messages,
            "max_tokens": 4096,
        }
        if system:
            kwargs["system"] = system
        if tools:
            kwargs["tools"] = tools

        resp = await self.client.messages.create(**kwargs)
        return self._to_openai_format(resp)

    def _to_openai_format(self, resp) -> dict:
        """Convert Anthropic response → OpenAI format."""
        tool_calls = []
        text = ""
        for block in resp.content:
            if block.type == "text":
                text += block.text
            elif block.type == "tool_use":
                tool_calls.append(
                    {
                        "id": block.id,
                        "type": "function",
                        "function": {
                            "name": block.name,
                            "arguments": json.dumps(block.input),
                        },
                    }
                )

        return {
            "choices": [
                {
                    "message": {
                        "role": "assistant",
                        "content": text,
                        "tool_calls": tool_calls if tool_calls else None,
                    }
                }
            ]
        }

    def extract_tool_calls(self, response: dict) -> list[dict]:
        raw = response["choices"][0]["message"].get("tool_calls") or []
        return [
            {
                "id": tc["id"],
                "name": tc["function"]["name"],
                "arguments": json.loads(tc["function"]["arguments"]),
            }
            for tc in raw
        ]

    def extract_text(self, response: dict) -> str:
        return response["choices"][0]["message"].get("content", "") or ""
