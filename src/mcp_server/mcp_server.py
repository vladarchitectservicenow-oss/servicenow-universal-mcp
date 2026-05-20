# Copyright (c) 2026 Vlady
# SPDX-License-Identifier: AGPL-3.0-only

"""Универсальный MCP-сервер — ядро проекта.

Реализует Model Context Protocol (MCP) для интеграции любой LLM с ServiceNow.

Поддерживает два режима:
- **STDIO** (для Claude Desktop и других MCP-клиентов)
- **HTTP** (JSON-RPC через HTTP — для веб-клиентов и Open WebUI)

Архитектура:
  ┌─────────────────────────────────────────────┐
  │  LLM (OpenAI / Claude / DeepSeek / Ollama)  │
  │  ↓ tool call: incident_create("...")        │
  ├─────────────────────────────────────────────┤
  │  UniversalMCPServer                         │
  │  ├── MCP Protocol (tools/list, tools/call)  │
  │  ├── ToolHandlers.dispatch()                │
  │  └── ServiceNowClient → REST API            │
  ├─────────────────────────────────────────────┤
  │  ServiceNow Instance                        │
  └─────────────────────────────────────────────┘
"""

from __future__ import annotations

import asyncio
import json
import logging
import sys
from typing import Any

from .client import ServiceNowClient
from .config import Config
from .modules import ToolHandlers
from .tools import TOOLS

log = logging.getLogger(__name__)


class UniversalMCPServer:
    """MCP Server, совместимый с любой LLM через стандартный MCP протокол."""

    PROTOCOL_VERSION = "0.1.0"

    def __init__(self, sn_client: ServiceNowClient, config: Config):
        self.sn = sn_client
        self.config = config
        self.handlers = ToolHandlers(sn_client)

    # ══════════════════════════════════════════════════════════════════════
    # MCP Protocol Methods
    # ══════════════════════════════════════════════════════════════════════

    async def handle_request(self, method: str, params: dict | None = None) -> dict:
        """Route MCP JSON-RPC requests."""
        params = params or {}

        if method == "initialize":
            return self._initialize(params)
        elif method == "tools/list":
            return self._tools_list()
        elif method == "tools/call":
            return await self._tools_call(params)
        elif method == "ping":
            return {}
        else:
            return {"error": f"Unknown method: {method}"}

    def _initialize(self, params: dict) -> dict:
        return {
            "protocolVersion": self.PROTOCOL_VERSION,
            "serverInfo": {
                "name": self.config.mcp.name,
                "version": "1.0.0",
            },
            "capabilities": {
                "tools": {},
            },
        }

    def _tools_list(self) -> dict:
        return {"tools": TOOLS}

    async def _tools_call(self, params: dict) -> dict:
        name = params.get("name", "")
        arguments = params.get("arguments", {})
        result_json = await self.handlers.dispatch(name, arguments)
        return {"content": [{"type": "text", "text": result_json}]}

    # ══════════════════════════════════════════════════════════════════════
    # STDIO Mode (Claude Desktop, другие MCP-клиенты)
    # ══════════════════════════════════════════════════════════════════════

    def run_stdio(self):
        """Run in STDIO mode — JSON-RPC через stdin/stdout."""
        log.info("Starting MCP server in STDIO mode...")
        asyncio.run(self._stdio_loop())

    async def _stdio_loop(self):
        """Читаем JSON-RPC запросы из stdin, отвечаем в stdout."""
        reader = asyncio.StreamReader()
        protocol = asyncio.StreamReaderProtocol(reader)
        await asyncio.get_event_loop().connect_read_pipe(lambda: protocol, sys.stdin)

        while True:
            try:
                line = await reader.readline()
                if not line:
                    break

                line = line.strip()
                if not line:
                    continue

                request = json.loads(line)
                request_id = request.get("id")
                method = request.get("method", "")
                params = request.get("params", {})

                response = await self.handle_request(method, params)
                response["id"] = request_id

                # Write to stdout
                sys.stdout.write(json.dumps(response, ensure_ascii=False) + "\n")
                sys.stdout.flush()

            except json.JSONDecodeError:
                error_response = {
                    "jsonrpc": "2.0",
                    "id": None,
                    "error": {"code": -32700, "message": "Parse error"},
                }
                sys.stdout.write(json.dumps(error_response) + "\n")
                sys.stdout.flush()
            except Exception as e:
                log.exception("Error handling request")
                error_response = {
                    "jsonrpc": "2.0",
                    "id": None,
                    "error": {"code": -32603, "message": str(e)},
                }
                sys.stdout.write(json.dumps(error_response) + "\n")
                sys.stdout.flush()

    # ══════════════════════════════════════════════════════════════════════
    # HTTP Mode (JSON-RPC через HTTP — для веб-клиентов)
    # ══════════════════════════════════════════════════════════════════════

    def run_http(self, port: int = 8000):
        """Run in HTTP mode — для веб-клиентов и Open WebUI."""
        log.info(f"Starting MCP server in HTTP mode on http://localhost:{port}...")
        asyncio.run(self._http_serve(port))

    async def _http_serve(self, port: int):
        """Простой HTTP-сервер с поддержкой JSON-RPC через POST."""
        import asyncio

        async def handle_client(reader, writer):
            try:
                raw = await asyncio.wait_for(reader.read(65536), timeout=30)
                if not raw:
                    writer.close()
                    return

                request_text = raw.decode("utf-8", errors="replace")

                # Parse HTTP request (упрощённо)
                body = ""
                if "\r\n\r\n" in request_text:
                    _, body = request_text.split("\r\n\r\n", 1)

                if not body.strip():
                    writer.write(
                        b"HTTP/1.1 400 Bad Request\r\nContent-Type: application/json\r\n\r\n"
                        b'{"error": "Empty body"}'
                    )
                    await writer.drain()
                    writer.close()
                    return

                request = json.loads(body)
                request_id = request.get("id")
                method = request.get("method", "")
                params = request.get("params", {})

                response = await self.handle_request(method, params)
                response["id"] = request_id
                response["jsonrpc"] = "2.0"

                response_text = json.dumps(response, ensure_ascii=False)
                writer.write(
                    f"HTTP/1.1 200 OK\r\n"
                    f"Content-Type: application/json\r\n"
                    f"Content-Length: {len(response_text.encode('utf-8'))}\r\n"
                    f"Access-Control-Allow-Origin: *\r\n"
                    f"Connection: close\r\n\r\n"
                    f"{response_text}".encode("utf-8")
                )
                await writer.drain()
            except asyncio.TimeoutError:
                pass
            except Exception as e:
                log.exception("HTTP handler error")
                error_response = json.dumps(
                    {
                        "jsonrpc": "2.0",
                        "id": None,
                        "error": {"code": -32603, "message": str(e)},
                    }
                )
                writer.write(
                    f"HTTP/1.1 500 Internal Server Error\r\n"
                    f"Content-Type: application/json\r\n"
                    f"Content-Length: {len(error_response)}\r\n\r\n"
                    f"{error_response}".encode("utf-8")
                )
                await writer.drain()
            finally:
                writer.close()

        server = await asyncio.start_server(handle_client, "0.0.0.0", port)
        log.info(f"MCP HTTP server listening on http://0.0.0.0:{port}")
        async with server:
            await server.serve_forever()

    # ══════════════════════════════════════════════════════════════════════
    # LLM Conversation Mode
    # ══════════════════════════════════════════════════════════════════════

    async def chat(self, user_message: str) -> str:
        """Отправить сообщение LLM с ServiceNow tools и вернуть ответ.

        Вызывается напрямую (не через MCP) — для простого чат-интерфейса.
        """
        from .llm import LLMProvider

        llm = LLMProvider(self.config.llm)
        messages: list[dict[str, Any]] = [
            {
                "role": "system",
                "content": self._system_prompt(),
            },
            {"role": "user", "content": user_message},
        ]

        for _ in range(10):  # Max 10 tool-call раундов
            response = await llm.chat(messages, TOOLS)
            tool_calls = llm.extract_tool_calls(response)

            if not tool_calls:
                # Текстовый ответ — возвращаем
                return llm.extract_text(response)

            # Выполняем tool calls
            for tc in tool_calls:
                result_json = await self.handlers.dispatch(tc["name"], tc["arguments"])
                messages.append(
                    {
                        "role": "assistant",
                        "content": None,
                        "tool_calls": [
                            {
                                "id": tc["id"],
                                "type": "function",
                                "function": {
                                    "name": tc["name"],
                                    "arguments": json.dumps(tc["arguments"]),
                                },
                            }
                        ],
                    }
                )
                messages.append(
                    {
                        "role": "tool",
                        "tool_call_id": tc["id"],
                        "content": result_json,
                    }
                )

        return "Превышен лимит tool-call итераций."

    def _system_prompt(self) -> str:
        return """Ты — AI-ассистент, подключённый к ServiceNow через универсальный MCP-протокол.

Твои возможности (используй tool calling):
- **Incident Management**: создание, поиск, обновление, статистика инцидентов
- **Change Management**: создание, просмотр, утверждение запросов на изменения
- **Problem Management**: создание проблем, связывание инцидентов
- **Service Catalog**: просмотр каталога услуг, создание запросов, проверка статуса
- **CMDB**: поиск конфигурационных единиц, зависимости, здоровье CMDB
- **Knowledge Base**: поиск статей по ключевым словам
- **Reporting**: SLA-отчёты, MTTR, загрузка групп, просроченные задачи
- **Workflows**: просмотр рабочих процессов и флоу
- **Integrations**: список внешних интеграций
- **Business Rules**: просмотр бизнес-правил на таблицах
- **Users & Groups**: информация о пользователях, состав групп

Отвечай на русском языке. Все операции выполняй через tool calls.
Данные получай из ServiceNow в реальном времени."""
