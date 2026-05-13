"""Пример: запуск MCP сервера в STDIO режиме для Claude Desktop.

1. Установите servicenow-universal-mcp
2. В claude_desktop_config.json добавьте:

```json
{
  "mcpServers": {
    "servicenow": {
      "command": "python",
      "args": ["-m", "mcp_server.cli", "--stdio"],
      "env": {
        "SNOW_INSTANCE_URL": "https://dev362840.service-now.com",
        "SNOW_USERNAME": "admin",
        "SNOW_PASSWORD": "your_password",
        "ANTHROPIC_API_KEY": "sk-ant-...",
        "ANTHROPIC_MODEL": "claude-sonnet-4"
      }
    }
  }
}
```

3. Перезапустите Claude Desktop
4. Claude автоматически обнаружит 26 инструментов ServiceNow

Теперь вы можете писать в Claude:
- "Create a P1 incident for database outage"
- "Show me all change requests pending approval"
- "What servers are in Production?"
"""

import asyncio
import json
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from mcp_server.config import Config
from mcp_server.client import ServiceNowClient
from mcp_server.mcp_server import UniversalMCPServer


async def test_mcp():
    """Тестовый запуск MCP — симулирует запрос от Claude."""
    cfg = Config()
    sn = ServiceNowClient(cfg.sn)
    server = UniversalMCPServer(sn, cfg)

    # Симулируем initialize
    resp = await server.handle_request("initialize", {
        "protocolVersion": "0.1.0",
        "clientInfo": {"name": "Claude Desktop", "version": "1.0.0"},
    })
    print("Initialize:", json.dumps(resp, indent=2, ensure_ascii=False)[:200])

    # Симулируем tools/list
    resp = await server.handle_request("tools/list")
    tool_names = [t["name"] for t in resp["tools"]]
    print(f"\nДоступно инструментов: {len(tool_names)}")
    print(", ".join(tool_names[:10]) + "...")

    # Симулируем tools/call — создание инцидента
    resp = await server.handle_request("tools/call", {
        "name": "incident_stats",
        "arguments": {"group_by": "state"},
    })
    print("\nIncident stats:", resp["content"][0]["text"][:300])


if __name__ == "__main__":
    asyncio.run(test_mcp())
