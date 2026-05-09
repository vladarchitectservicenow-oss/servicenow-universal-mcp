# ServiceNow Universal MCP

> **Подключи любую LLM к ServiceNow. Без привязки к Claude. Без привязки к OpenAI. Один протокол — любой провайдер.**

[![License: AGPL-3.0](https://img.shields.io/badge/License-AGPL--3.0-blue.svg)](LICENSE)
[![Python 3.10+](https://img.shields.io/badge/Python-3.10%2B-green.svg)](https://www.python.org/)
[![MCP Compatible](https://img.shields.io/badge/MCP-Compatible-purple.svg)](https://modelcontextprotocol.io/)

Универсальный MCP-сервер, который превращает **ServiceNow** в conversational-интерфейс для **любой LLM**: OpenAI GPT-4o, Anthropic Claude, DeepSeek, Ollama (локальные модели), OpenRouter и любые OpenAI-совместимые API.

---

## 🤔 Зачем это нужно?

Оригинальный пост LinkedIn (май 2026) показал MCP-интеграцию Claude → ServiceNow. Проблема: решение **привязано к Claude Desktop**. 

**ServiceNow Universal MCP** делает то же самое, но:

| | Claude MCP | Universal MCP |
|---|---|---|
| Claude (Anthropic) | ✅ | ✅ |
| OpenAI GPT-4o | ❌ | ✅ |
| DeepSeek | ❌ | ✅ |
| Ollama (локально) | ❌ | ✅ |
| OpenRouter | ❌ | ✅ |
| Любой OpenAI-API | ❌ | ✅ |
| STDIO mode | ✅ | ✅ |
| HTTP SSE mode | ❌ | ✅ |
| 24+ модулей ServiceNow | 4-5 | ✅ **24** |

---

## 📦 Возможности (24 модуля ServiceNow)

| Модуль | Что можно делать |
|--------|------------------|
| **Incident Management** | Создавать, искать, обновлять, получать статистику инцидентов |
| **Change Management** | Создавать CR, утверждать, отслеживать статус |
| **Problem Management** | Создавать проблемы, привязывать инциденты, искать root cause |
| **Service Catalog** | Просматривать каталог, создавать запросы, проверять статус |
| **CMDB** | Искать CI, смотреть зависимости, проверять здоровье |
| **Knowledge Base** | Искать статьи, получать контент |
| **Reporting & Analytics** | SLA-отчёты, MTTR, загрузка групп, overdue |
| **Workflow / Flow Designer** | Список рабочих процессов |
| **Integrations** | Список REST-интеграций с эндпоинтами |
| **Business Rules** | Просмотр бизнес-правил на таблицах |
| **Users & Groups** | Информация о пользователях, состав групп |
| **+ ещё 13 модулей** | Service Portal, Virtual Agent, Approvals, SLA и др. |

---

## 🚀 Быстрый старт

### 1. Установка

```bash
git clone https://github.com/vladarchitectservicenow-oss/servicenow-universal-mcp.git
cd servicenow-universal-mcp
pip install -e ".[all]"
```

### 2. Настройка

```bash
cp .env.example .env
# Заполни .env:
#   - Данные ServiceNow (SNOW_INSTANCE_URL, SNOW_USERNAME, SNOW_PASSWORD)
#   - Ключ к ЛЮБОМУ LLM-провайдеру (выбери один):
#       OpenAI: OPENAI_API_KEY
#       Anthropic: ANTHROPIC_API_KEY
#       DeepSeek: DEEPSEEK_API_KEY
#       Ollama: OLLAMA_HOST=http://localhost:11434
#       OpenRouter: OPENROUTER_API_KEY
```

### 3. Запуск

```bash
# Режим STDIO (для Claude Desktop, Continue, Cline)
sn-mcp --stdio

# Режим HTTP (для веб-клиентов, Open WebUI, своего фронтенда)
sn-mcp --sse --port 8000
```

### 4. Использование

После запуска любая LLM с поддержкой MCP может управлять ServiceNow:

> *«Создай инцидент P1 для падения продакшен-базы, назначь на DBA team»*
>
> *«Покажи все change requests на эти выходные со статусом approval»*
>
> *«Какая команда имеет больше всего просроченных инцидентов в этом месяце?»*
>
> *«Найди все серверы в Production на Windows Server 2019»*

---

## 🏗️ Архитектура

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
│  │           ToolHandlers (диспетчер)                │   │
│  │  incident_create  | change_approve | cmdb_search │   │
│  │  problem_link     | catalog_list   | kb_search   │   │
│  │  ... + ещё 20 инструментов                      │   │
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

# Режимы запуска
sn-mcp --stdio              # STDIO — Claude Desktop, Continue
sn-mcp --sse                # HTTP SSE на порту 8000
sn-mcp --sse --port 9090    # HTTP на своём порту
sn-mcp --stdio --verbose    # Отладка

# Прямой чат с LLM (без MCP)
python -c "
import asyncio
from mcp_server.config import Config
from mcp_server.client import ServiceNowClient
from mcp_server.mcp_server import UniversalMCPServer

async def main():
    cfg = Config()
    server = UniversalMCPServer(ServiceNowClient(cfg.sn), cfg)
    answer = await server.chat('Сколько открытых инцидентов сейчас?')
    print(answer)

asyncio.run(main())
"
```

---

## 🔧 Поддерживаемые LLM Providers

| Provider | Модели | Переменная |
|----------|--------|------------|
| **OpenAI** | GPT-4o, GPT-4-turbo, GPT-3.5 | `OPENAI_API_KEY` |
| **Anthropic** | Claude Opus, Sonnet, Haiku | `ANTHROPIC_API_KEY` |
| **DeepSeek** | deepseek-chat, deepseek-reasoner | `DEEPSEEK_API_KEY` |
| **Ollama** | Llama3, Qwen2.5, Mistral, Gemma | `OLLAMA_HOST` |
| **OpenRouter** | Все модели (150+) | `OPENROUTER_API_KEY` |
| **Custom** | Любой OpenAI-совместимый API | `base_url` + `api_key` в коде |

---

## 📂 Структура проекта

```
servicenow-universal-mcp/
├── src/mcp_server/
│   ├── __init__.py          # Версия, метаданные
│   ├── config.py            # Конфигурация (.env автозагрузка)
│   ├── client.py            # ServiceNow REST API клиент
│   ├── mcp_server.py        # Ядро: MCP протокол + STDIO/SSE
│   ├── tools.py             # TOOLS — 30+ инструментов (схемы)
│   ├── cli.py               # CLI точка входа
│   ├── modules/
│   │   └── __init__.py      # ToolHandlers — реализация всех tools
│   └── llm/
│       └── __init__.py      # LLM-адаптеры (OpenAI/Anthropic/Ollama)
├── docs/                    # Документация
├── examples/                # Примеры использования
├── tests/                   # Тесты
├── pyproject.toml           # Зависимости и сборка
├── LICENSE                  # AGPL-3.0 + commercial
├── .env.example             # Шаблон конфигурации
└── README.md                # Этот файл
```

---

## 🧪 Тестирование на реальном инстансе

Проект протестирован на PDI ServiceNow:
- **197 catalog items** (147 активных)
- **6 workflows**
- **11 интеграций** (Azure AD, Slack, Jira, Okta, AWS...)
- **Australia release** (AI Agent Studio, Now Assist skills, Generative AI Controller)

---

## 📄 Лицензия

**AGPL-3.0** — свободное использование с одним условием: если вы модифицируете код и предоставляете его как сервис, вы обязаны открыть исходный код.

**Коммерческая лицензия** — для встраивания в проприетарные продукты без обязательств AGPL-3.0.
Связь: создайте issue в репозитории.

---

## 🤝 Контрибьюция

1. Форкните репозиторий
2. Создайте ветку: `git checkout -b feature/имя-модуля`
3. Добавьте новый модуль в `tools.py` + handler в `modules/__init__.py`
4. Запушьте и создайте Pull Request

**Добавить новый ServiceNow модуль — 15 минут:**
```python
# 1. tools.py — добавьте схему
{"name": "my_module_action", "description": "...", "inputSchema": {...}},

# 2. modules/__init__.py — добавьте handler
async def handle_my_module_action(self, a: dict) -> str:
    result = await self.client.list("my_table", ...)
    return _ok(data=result)
```

---

⭐ **Если проект полезен — поставьте звезду на GitHub. Это помогает другим найти его.**

Построено [Hermes Agent](https://github.com/NousResearch/hermes-agent) — агентом, который сам учится.
