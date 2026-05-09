# Copyright (c) 2026 Vlady
# SPDX-License-Identifier: AGPL-3.0-only

"""Конфигурация сервера — загружается из .env / переменных окружения."""

import os
from dataclasses import dataclass, field
from typing import Optional

from dotenv import load_dotenv

load_dotenv()


@dataclass
class SNConfig:
    """ServiceNow instance settings."""
    url: str = os.getenv("SNOW_INSTANCE_URL", "https://dev362840.service-now.com")
    username: str = os.getenv("SNOW_USERNAME", "admin")
    password: str = os.getenv("SNOW_PASSWORD", "")
    timeout: int = 30


@dataclass
class MCPConfig:
    """MCP server settings."""
    name: str = os.getenv("MCP_SERVER_NAME", "ServiceNow Universal MCP")
    port: int = int(os.getenv("MCP_SERVER_PORT", "8000"))
    log_level: str = os.getenv("MCP_LOG_LEVEL", "INFO")


@dataclass
class LLMConfig:
    """LLM provider configuration — выбирает первого доступного."""
    provider: str = ""           # openai | anthropic | deepseek | ollama | openrouter
    model: str = ""
    api_key: str = ""
    base_url: Optional[str] = None

    @classmethod
    def from_env(cls) -> "LLMConfig":
        """Авто-обнаружение доступного провайдера из переменных окружения."""
        providers = [
            ("openai", "OPENAI_API_KEY", "OPENAI_MODEL", "gpt-4o", None),
            ("anthropic", "ANTHROPIC_API_KEY", "ANTHROPIC_MODEL", "claude-sonnet-4", None),
            ("deepseek", "DEEPSEEK_API_KEY", "DEEPSEEK_MODEL", "deepseek-chat", "https://api.deepseek.com"),
            ("ollama", "OLLAMA_HOST", "OLLAMA_MODEL", "llama3", "http://localhost:11434/v1"),
            ("openrouter", "OPENROUTER_API_KEY", "OPENROUTER_MODEL", "anthropic/claude-sonnet-4", "https://openrouter.ai/api/v1"),
        ]

        for provider, key_env, model_env, default_model, base_url in providers:
            if provider == "ollama":
                host = os.getenv(key_env, "")
                if host:
                    return cls(
                        provider="ollama",
                        api_key="ollama",
                        model=os.getenv(model_env, default_model),
                        base_url=f"{host.rstrip('/')}/v1" if "/v1" not in host else host,
                    )
            else:
                key = os.getenv(key_env, "")
                if key:
                    return cls(
                        provider=provider,
                        api_key=key,
                        model=os.getenv(model_env, default_model),
                        base_url=base_url,
                    )

        raise ValueError(
            "LLM provider not configured. Set one of:\n"
            "  OPENAI_API_KEY, ANTHROPIC_API_KEY, DEEPSEEK_API_KEY,\n"
            "  OLLAMA_HOST, OPENROUTER_API_KEY.\n"
            "  Copy .env.example → .env and fill in the blanks."
        )


@dataclass
class Config:
    sn: SNConfig = field(default_factory=SNConfig)
    mcp: MCPConfig = field(default_factory=MCPConfig)
    llm: LLMConfig = field(default_factory=LLMConfig.from_env)
