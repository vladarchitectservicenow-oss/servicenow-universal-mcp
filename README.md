# ServiceNow Universal MCP

> **Connect any LLM to ServiceNow. No Claude lock-in. No OpenAI lock-in. One protocol — any provider.**

[![License: AGPL-3.0](https://img.shields.io/badge/License-AGPL--3.0-blue.svg)](LICENSE)
[![Python 3.10+](https://img.shields.io/badge/Python-3.10%2B-green.svg)](https://www.python.org/)
[![MCP Compatible](https://img.shields.io/badge/MCP-Compatible-purple.svg)](https://modelcontextprotocol.io/)

A universal MCP server that turns **ServiceNow** into a conversational interface for **any LLM**: OpenAI GPT-4o, Anthropic Claude, DeepSeek, Ollama (local models), OpenRouter, and any OpenAI-compatible API.

---

## 🤔 Why this exists

In May 2026, a LinkedIn post went viral showing an MCP integration: Claude → ServiceNow. Beautiful idea: *"The future isn't better UI. It's no UI."*

Problem: that solution is **locked to Claude Desktop**.

**ServiceNow Universal MCP** does the same thing — but for any provider:

| | Claude MCP | Universal MCP |
|---|---|---|
| Claude (Anthropic) | ✅ | ✅ |
| OpenAI GPT-4o | ❌ | ✅ |
| DeepSeek | ❌ | ✅ |
| Ollama (local) | ❌ | ✅ |
| OpenRouter (150+ models) | ❌ | ✅ |
| Any OpenAI-compatible API | ❌ | ✅ |
| STDIO mode | ✅ | ✅ |
| HTTP/SSE mode | ❌ | ✅ |
| ServiceNow modules covered | ~5 | **11** |

---

## 📦 Capabilities (11 ServiceNow modules, 26 tools)

| Module | What you can do |
|--------|------------------|
| **Incident Management** | Create, search, update, stats (5 tools) |
| **Change Management** | Create CRs, approve/reject, filter by type (3 tools) |
| **Problem Management** | Create problems, link incidents, root cause (3 tools) |
| **Service Catalog** | Browse catalog, create requests, check status (4 tools) |
| **CMDB** | Search CIs, show dependencies, health check (3 tools) |
| **Knowledge Base** | Search published articles (1 tool) |
| **Reporting & Analytics** | SLA breaches, MTTR, group load, overdue trend |
| **Workflows** | List published workflows/flows (1 tool) |
| **Integrations** | List REST integrations with endpoints (1 tool) |
| **Business Rules** | Audit business rules per table (1 tool) |
| **Users & Groups** | Look up users, list group members (2 tools) |

---

## 🚀 Quick Start

### 1. Install

```bash
git clone https://github.com/vladarchitectservicenow-oss/servicenow-universal-mcp.git
cd servicenow-universal-mcp
pip install -e ".[all]"
```

### 2. Configure

```bash
cp .env.example .env
# Fill in .env:
#   - ServiceNow credentials (SNOW_INSTANCE_URL, SNOW_USERNAME, SNOW_PASSWORD)
#   - Any ONE LLM provider key:
#       OpenAI: OPENAI_API_KEY
#       Anthropic: ANTHROPIC_API_KEY
#       DeepSeek: DEEPSEEK_API_KEY
#       Ollama: OLLAMA_HOST=http://localhost:11434
#       OpenRouter: OPENROUTER_API_KEY
```

The server **auto-discovers** which provider is available. Set one, skip the rest.

### 3. Run

```bash
# STDIO mode (Claude Desktop, Continue, Cline, any MCP client)
sn-mcp --stdio

# HTTP mode (web clients, Open WebUI, custom frontends)
sn-mcp --sse --port 8000
```

### 4. Use

Once running, any LLM with MCP support can control ServiceNow:

> *"Create a P1 incident for the production DB being down, assign to DBA team"*
>
> *"Show all change requests planned for this weekend with their approval status"*
>
> *"Which team has the most overdue incidents this month?"*
>
> *"Find all servers in Production running Windows Server 2019"*

---

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────┐
│  LLM (OpenAI / Claude / DeepSeek / Ollama / OpenRouter) │
│                         ↓ tool call                      │
├─────────────────────────────────────────────────────────┤
│                UniversalMCPServer                        │
│  ┌──────────────┐  ┌──────────────┐  ┌───────────────┐  │
│  │ MCP Protocol │  │ LLM Adapter  │  │ SN REST Client│  │
│  │ (STDIO/SSE)  │  │ (abstraction)│  │ (httpx+retry) │  │
│  └──────────────┘  └──────────────┘  └───────────────┘  │
│                         ↓                                │
│  ┌──────────────────────────────────────────────────┐   │
│  │              ToolHandlers (dispatcher)            │   │
│  │  incident_create | change_approve | cmdb_search  │   │
│  │  problem_link    | catalog_list   | kb_search    │   │
│  │  ... + 20 more tools                             │   │
│  └──────────────────────────────────────────────────┘   │
├─────────────────────────────────────────────────────────┤
│               ServiceNow Instance                        │
│         /api/now/table/*    /api/now/stats/*             │
└─────────────────────────────────────────────────────────┘
```

---

## 📡 CLI

```bash
sn-mcp --help

# Run modes
sn-mcp --stdio              # STDIO — Claude Desktop, Continue, Cline
sn-mcp --sse                # HTTP SSE on port 8000
sn-mcp --sse --port 9090    # Custom port
sn-mcp --stdio --verbose    # Debug mode

# Direct chat (bypass MCP protocol)
python -c "
import asyncio
from mcp_server.config import Config
from mcp_server.client import ServiceNowClient
from mcp_server.mcp_server import UniversalMCPServer

async def main():
    cfg = Config()
    server = UniversalMCPServer(ServiceNowClient(cfg.sn), cfg)
    answer = await server.chat('How many open incidents right now?')
    print(answer)

asyncio.run(main())
"
```

---

## 🔧 Supported LLM Providers

| Provider | Models | Env Variable |
|----------|--------|--------------|
| **OpenAI** | GPT-4o, GPT-4-turbo, GPT-3.5 | `OPENAI_API_KEY` |
| **Anthropic** | Claude Opus, Sonnet, Haiku | `ANTHROPIC_API_KEY` |
| **DeepSeek** | deepseek-chat, deepseek-reasoner | `DEEPSEEK_API_KEY` |
| **Ollama** | Llama 3, Qwen 2.5, Mistral, Gemma | `OLLAMA_HOST` |
| **OpenRouter** | 150+ models | `OPENROUTER_API_KEY` |
| **Custom** | Any OpenAI-compatible API | `base_url` + `api_key` in code |

---

## 📂 Project Structure

```
servicenow-universal-mcp/
├── src/mcp_server/
│   ├── __init__.py          # Version, metadata
│   ├── config.py            # Configuration (auto .env loading)
│   ├── client.py            # ServiceNow REST API client
│   ├── mcp_server.py        # Core: MCP protocol + STDIO/SSE
│   ├── tools.py             # 26 MCP tools (schemas)
│   ├── cli.py               # CLI entry point
│   ├── modules/
│   │   └── __init__.py      # ToolHandlers — tool implementations
│   └── llm/
│       └── __init__.py      # LLM adapters (OpenAI/Anthropic/Ollama)
├── docs/modules/            # Per-module documentation (English)
├── examples/                # Usage examples
├── tests/                   # Tests
├── marketing/               # LinkedIn post, promotional materials
├── pyproject.toml           # Dependencies & build
├── LICENSE                  # AGPL-3.0 + commercial clause
├── .env.example             # Configuration template
└── README.md                # This file
```

---

## 🧪 Tested on a real instance

Verified against a ServiceNow PDI:
- **197 catalog items** (147 active)
- **6 workflows**
- **11 integrations** (Azure AD, Slack, Jira, Okta, AWS, SAP, Datadog...)
- **Australia release** (AI Agent Studio, Now Assist skills, Generative AI Controller)

---

## 📄 License

**AGPL-3.0** — free use with one condition: if you modify the code and provide it as a service (SaaS), you must open-source your changes.

**Commercial license** — for embedding in proprietary products without AGPL-3.0 obligations.
Contact: open an issue in the repository.

---

## 🤝 Contributing

1. Fork the repo
2. Create a branch: `git checkout -b feature/module-name`
3. Add a new module: schema in `tools.py` + handler in `modules/__init__.py`
4. Push and open a Pull Request

**Add a new ServiceNow module in 15 minutes:**
```python
# 1. tools.py — add schema
{"name": "my_module_action", "description": "...", "inputSchema": {...}},

# 2. modules/__init__.py — add handler
async def handle_my_module_action(self, a: dict) -> str:
    result = await self.client.list("my_table", ...)
    return _ok(data=result)
```

---

⭐ **If this project is useful — star it on GitHub. It helps others discover it.**

Built by [Vlady](https://github.com/vladarchitectservicenow-oss) with [Hermes Agent](https://github.com/NousResearch/hermes-agent).
