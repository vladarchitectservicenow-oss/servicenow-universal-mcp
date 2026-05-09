# Copyright (c) 2026 Vlady
# SPDX-License-Identifier: AGPL-3.0-only

"""MCP Tools — полный набор инструментов для всех модулей ServiceNow.

Все инструменты возвращают JSON-строки (требование MCP).
Каждый модуль — изолированный набор tools.

Модули:
  - Incident Management
  - Change Management
  - Problem Management
  - Service Catalog & Requests
  - CMDB (Configuration Management)
  - Knowledge Base
  - Service Portal / Employee Center
  - Virtual Agent
  - Reporting & Analytics
  - Business Rules & Scripts
  - Workflow & Flow Designer
  - User & Group Management
"""

from __future__ import annotations

import json
from typing import Any

from .client import ServiceNowClient


# ═══════════════════════════════════════════════════════════════════════════
# Helpers
# ═══════════════════════════════════════════════════════════════════════════

def _j(obj: Any) -> str:
    """Serialize to JSON string (MCP requirement)."""
    return json.dumps(obj, ensure_ascii=False, indent=2)


def _ok(data: Any = None, **kw) -> str:
    return _j({"success": True, "data": data, **kw})


def _err(msg: str) -> str:
    return _j({"success": False, "error": msg})


# ═══════════════════════════════════════════════════════════════════════════
# TOOL DEFINITIONS (schema для каждой LLM)
# ═══════════════════════════════════════════════════════════════════════════

TOOLS = [
    # ── INCIDENT MANAGEMENT ──────────────────────────────────────────────
    {
        "name": "incident_create",
        "description": "Создать инцидент в ServiceNow. Укажи краткое описание, приоритет (1-5), категорию и группу назначения.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "short_description": {"type": "string", "description": "Краткое описание инцидента"},
                "priority": {"type": "integer", "description": "Приоритет: 1 (Critical), 2 (High), 3 (Moderate), 4 (Low), 5 (Planning)"},
                "category": {"type": "string", "description": "Категория (например: Hardware, Software, Network, Database)"},
                "assignment_group": {"type": "string", "description": "Группа назначения (название группы)"},
                "caller_id": {"type": "string", "description": "Email пользователя, сообщившего об инциденте (опционально)"},
                "description": {"type": "string", "description": "Полное описание инцидента (опционально)"},
            },
            "required": ["short_description"],
        },
    },
    {
        "name": "incident_list",
        "description": "Получить список инцидентов с фильтрацией. Можно фильтровать по статусу, приоритету, группе.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "state": {"type": "string", "description": "Состояние: 1=New, 2=In Progress, 3=On Hold, 6=Resolved, 7=Closed"},
                "priority": {"type": "string", "description": "Приоритет: 1-5"},
                "assignment_group": {"type": "string", "description": "Фильтр по группе назначения"},
                "assigned_to": {"type": "string", "description": "Фильтр по исполнителю"},
                "limit": {"type": "integer", "description": "Максимум записей (по умолчанию 20)"},
            },
        },
    },
    {
        "name": "incident_get",
        "description": "Получить детали конкретного инцидента по номеру (например, INC0010001).",
        "inputSchema": {
            "type": "object",
            "properties": {
                "number": {"type": "string", "description": "Номер инцидента (например, INC0012345)"},
            },
            "required": ["number"],
        },
    },
    {
        "name": "incident_update",
        "description": "Обновить существующий инцидент: изменить статус, добавить комментарий, переназначить.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "number": {"type": "string", "description": "Номер инцидента (например, INC0012345)"},
                "state": {"type": "string", "description": "Новое состояние: 1=New, 2=In Progress, 3=On Hold, 6=Resolved, 7=Closed"},
                "work_notes": {"type": "string", "description": "Рабочие заметки"},
                "comments": {"type": "string", "description": "Комментарий для пользователя"},
                "assignment_group": {"type": "string", "description": "Новая группа назначения"},
            },
            "required": ["number"],
        },
    },
    {
        "name": "incident_stats",
        "description": "Получить статистику по инцидентам: по статусам, приоритетам, группам, overdue.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "group_by": {"type": "string", "description": "Группировка: state, priority, assignment_group, category"},
            },
        },
    },

    # ── CHANGE MANAGEMENT ────────────────────────────────────────────────
    {
        "name": "change_list",
        "description": "Получить список запросов на изменения (Change Requests). Фильтрация по типу, статусу, дате.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "type": {"type": "string", "description": "Тип изменения: normal, standard, emergency"},
                "approval": {"type": "string", "description": "Статус утверждения: requested, approved, rejected"},
                "state": {"type": "string", "description": "Состояние (числовой код)"},
                "planned_start": {"type": "string", "description": "Плановое начало (например, 'this weekend')"},
                "limit": {"type": "integer", "description": "Максимум записей (по умолчанию 20)"},
            },
        },
    },
    {
        "name": "change_create",
        "description": "Создать запрос на изменение (Change Request).",
        "inputSchema": {
            "type": "object",
            "properties": {
                "short_description": {"type": "string", "description": "Краткое описание изменения"},
                "type": {"type": "string", "description": "Тип: normal, standard, emergency"},
                "risk": {"type": "string", "description": "Уровень риска: high, medium, low"},
                "justification": {"type": "string", "description": "Обоснование изменения"},
                "implementation_plan": {"type": "string", "description": "План реализации"},
                "planned_start": {"type": "string", "description": "Дата/время планового начала (ISO 8601)"},
                "planned_end": {"type": "string", "description": "Дата/время планового окончания (ISO 8601)"},
            },
            "required": ["short_description"],
        },
    },
    {
        "name": "change_approve",
        "description": "Утвердить или отклонить запрос на изменение.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "number": {"type": "string", "description": "Номер запроса на изменение (CHG...)"},
                "approved": {"type": "boolean", "description": "True = утвердить, False = отклонить"},
                "comments": {"type": "string", "description": "Комментарий к решению"},
            },
            "required": ["number", "approved"],
        },
    },

    # ── PROBLEM MANAGEMENT ───────────────────────────────────────────────
    {
        "name": "problem_create",
        "description": "Создать запись проблемы (Problem) — для поиска корневой причины инцидентов.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "short_description": {"type": "string", "description": "Краткое описание проблемы"},
                "description": {"type": "string", "description": "Полное описание"},
                "assignment_group": {"type": "string", "description": "Группа назначения"},
                "priority": {"type": "integer", "description": "Приоритет 1-5"},
            },
            "required": ["short_description"],
        },
    },
    {
        "name": "problem_list",
        "description": "Получить список проблем с фильтрацией.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "state": {"type": "string", "description": "Состояние: 1=Open, 2=In Progress, 3=Resolved, 4=Closed"},
                "assignment_group": {"type": "string", "description": "Фильтр по группе"},
                "limit": {"type": "integer", "description": "Максимум записей (по умолчанию 20)"},
            },
        },
    },
    {
        "name": "problem_link_incidents",
        "description": "Привязать инциденты к проблеме для анализа корневой причины.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "problem_number": {"type": "string", "description": "Номер проблемы (PRB...)"},
                "incident_numbers": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "Список номеров инцидентов (например, [\"INC0010001\", \"INC0010002\"])",
                },
            },
            "required": ["problem_number", "incident_numbers"],
        },
    },

    # ── SERVICE CATALOG & REQUESTS ───────────────────────────────────────
    {
        "name": "catalog_list",
        "description": "Получить список элементов каталога услуг (Catalog Items) с поиском по названию.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "search": {"type": "string", "description": "Поиск по названию каталога"},
                "category": {"type": "string", "description": "Фильтр по категории"},
                "limit": {"type": "integer", "description": "Максимум записей (по умолчанию 20)"},
            },
        },
    },
    {
        "name": "request_create",
        "description": "Создать запрос на услугу (Service Request) из каталога.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "catalog_item_name": {"type": "string", "description": "Название элемента каталога (например, 'Laptop Request')"},
                "requested_for": {"type": "string", "description": "Email пользователя, для которого создаётся запрос"},
                "quantity": {"type": "integer", "description": "Количество"},
                "variables": {"type": "object", "description": "Дополнительные переменные запроса (опционально)"},
            },
            "required": ["catalog_item_name", "requested_for"],
        },
    },
    {
        "name": "request_status",
        "description": "Проверить статус запроса на услугу по номеру (REQ..., RITM..., SCTASK...).",
        "inputSchema": {
            "type": "object",
            "properties": {
                "number": {"type": "string", "description": "Номер запроса (REQ..., RITM... или SCTASK...)"},
            },
            "required": ["number"],
        },
    },
    {
        "name": "request_approvals",
        "description": "Показать все ожидающие утверждения запросы (для текущего пользователя или все).",
        "inputSchema": {
            "type": "object",
            "properties": {
                "approver": {"type": "string", "description": "Email утверждающего (опционально — если не указан, покажет все)"},
            },
        },
    },

    # ── CMDB ─────────────────────────────────────────────────────────────
    {
        "name": "cmdb_search",
        "description": "Поиск конфигурационных единиц (CI) в CMDB по названию, классу, окружению.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "name": {"type": "string", "description": "Поиск по названию (частичное совпадение)"},
                "class": {"type": "string", "description": "Класс CI (например, 'Server', 'Application', 'Database')"},
                "environment": {"type": "string", "description": "Окружение: Production, Test, Development, Staging"},
                "limit": {"type": "integer", "description": "Максимум записей (по умолчанию 30)"},
            },
        },
    },
    {
        "name": "cmdb_relationships",
        "description": "Показать зависимости (relationships) для CI — что от него зависит и от чего зависит он.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "ci_name": {"type": "string", "description": "Название CI (например, 'PROD-DB-01')"},
            },
            "required": ["ci_name"],
        },
    },
    {
        "name": "cmdb_health",
        "description": "Получить сводку здоровья CMDB: дубликаты, сироты, устаревшие записи.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "check": {"type": "string", "description": "Что проверять: duplicates, orphans, stale, all (по умолчанию all)"},
            },
        },
    },

    # ── KNOWLEDGE BASE ───────────────────────────────────────────────────
    {
        "name": "kb_search",
        "description": "Поиск в базе знаний (Knowledge Base) по ключевым словам.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "query": {"type": "string", "description": "Поисковый запрос"},
                "category": {"type": "string", "description": "Категория KB"},
                "limit": {"type": "integer", "description": "Максимум статей (по умолчанию 10)"},
            },
            "required": ["query"],
        },
    },

    # ── REPORTING & ANALYTICS ────────────────────────────────────────────
    {
        "name": "report_performance",
        "description": "Получить отчёт по производительности: SLA, среднее время решения, загрузка групп.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "metric": {"type": "string", "description": "Метрика: sla_breach, mttr, group_load, overdue_trend"},
                "period": {"type": "string", "description": "Период: today, this_week, this_month, last_month"},
                "assignment_group": {"type": "string", "description": "Фильтр по группе (опционально)"},
            },
            "required": ["metric"],
        },
    },

    # ── WORKFLOW & FLOW DESIGNER ─────────────────────────────────────────
    {
        "name": "workflow_list",
        "description": "Получить список опубликованных рабочих процессов (Workflows/Flows).",
        "inputSchema": {
            "type": "object",
            "properties": {
                "name": {"type": "string", "description": "Поиск по названию workflow"},
                "limit": {"type": "integer", "description": "Максимум записей (по умолчанию 20)"},
            },
        },
    },

    # ── INTEGRATIONS ─────────────────────────────────────────────────────
    {
        "name": "integration_list",
        "description": "Получить список внешних интеграций (REST Messages, Webhooks) с эндпоинтами.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "name": {"type": "string", "description": "Поиск по названию интеграции"},
                "limit": {"type": "integer", "description": "Максимум записей (по умолчанию 20)"},
            },
        },
    },

    # ── BUSINESS RULES & SCRIPTS ─────────────────────────────────────────
    {
        "name": "business_rule_list",
        "description": "Получить список бизнес-правил на указанной таблице.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "table": {"type": "string", "description": "Имя таблицы (например, incident, change_request, sc_req_item)"},
                "active": {"type": "boolean", "description": "Только активные (по умолчанию true)"},
                "limit": {"type": "integer", "description": "Максимум записей (по умолчанию 20)"},
            },
        },
    },

    # ── USER & GROUP ─────────────────────────────────────────────────────
    {
        "name": "user_info",
        "description": "Получить информацию о пользователе ServiceNow по email или имени.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "email": {"type": "string", "description": "Email пользователя"},
                "name": {"type": "string", "description": "Имя пользователя (частичное совпадение)"},
            },
        },
    },
    {
        "name": "group_members",
        "description": "Показать участников группы ServiceNow.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "group_name": {"type": "string", "description": "Название группы (частичное совпадение)"},
            },
            "required": ["group_name"],
        },
    },
]
