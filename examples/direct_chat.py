"""Пример: прямое использование UniversalMCPServer из Python (без MCP/STDIO).

Этот пример показывает, как встроить сервер в своё приложение
и отправлять запросы LLM напрямую.
"""

import asyncio
import os

# Добавляем src в PYTHONPATH (если запускаем из examples/)
import sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from mcp_server.config import Config
from mcp_server.client import ServiceNowClient
from mcp_server.mcp_server import UniversalMCPServer


async def main():
    # 1. Загружаем конфигурацию из .env
    cfg = Config()

    # 2. Создаём ServiceNow клиент
    sn = ServiceNowClient(cfg.sn)

    # 3. Поднимаем MCP сервер
    server = UniversalMCPServer(sn, cfg)

    # 4. Отправляем запросы через LLM
    queries = [
        "Сколько всего открытых инцидентов в системе?",
        "Создай тестовый инцидент: 'Проверка MCP-интеграции', приоритет 4, категория Software",
        "Покажи последние 5 изменений со статусом",
        "Найди в CMDB все Production-серверы",
    ]

    for q in queries:
        print(f"\n{'='*60}")
        print(f"📝 User: {q}")
        answer = await server.chat(q)
        print(f"🤖 AI:  {answer}")


if __name__ == "__main__":
    asyncio.run(main())
