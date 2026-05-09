# LinkedIn Post: ServiceNow Universal MCP

📡 **Я построил MCP-сервер для ServiceNow, который работает с ЛЮБОЙ LLM. Не только с Claude.**

Месяц назад в LinkedIn разлетелся пост про MCP-интеграцию Claude → ServiceNow. Красиво: «The future isn't better UI. It's no UI.» Согласен на 100%.

Но есть нюанс. То решение привязано к Claude Desktop. Хочешь OpenAI? DeepSeek? Локальную Llama? — Мимо.

Я пошёл дальше и построил **универсальный MCP-сервер** — один протокол, любой провайдер.

---

### Что умеет сервер (26 инструментов, 11 модулей):

✅ **Incident Management** — создание, поиск, обновление, статистика
✅ **Change Management** — CR от черновика до утверждения
✅ **Problem Management** — root cause + связывание инцидентов
✅ **Service Catalog** — просмотр каталога, создание запросов, Cart API
✅ **CMDB** — поиск CI, зависимости, здоровье конфигураций
✅ **Knowledge Base** — поиск по 53 статьям
✅ **Reporting** — SLA, MTTR, загрузка групп, overdue trend
✅ **Workflows, Integrations, Business Rules, Users & Groups**

---

### Архитектура:

```
OpenAI / Claude / DeepSeek / Ollama / OpenRouter
              ↓  (tool call)
      Universal MCPServer
              ↓  (REST API + retry)
        ServiceNow Instance
```

Один `.env` файл — и сервер сам определяет доступного провайдера.

---

### Протестировано на реальном инстансе:

- 197 catalog items (147 активных)
- 6 workflows, 11 интеграций (Azure AD, Slack, Jira, Okta, AWS, SAP)
- Australia release: AI Agent Studio, Now Assist skills, Generative AI Controller

---

### Почему это важно:

Мы тратим часы на навигацию по ITSM-формам. MCP-сервер схлопывает всё это в один диалог:

> «Создай P1 инцидент для падения базы, назначь DBA team»
> «Какие изменения запланированы на эти выходные?»
> «Какая команда имеет больше всего просроченных инцидентов?»

Без кликов. Без навигации. Без привязки к одному провайдеру.

---

🔗 **GitHub:** [servicenow-universal-mcp](https://github.com/vladarchitectservicenow-oss/servicenow-universal-mcp)
📄 **Лицензия:** AGPL-3.0 (коммерческая по запросу)
🐍 **Стек:** Python, httpx, MCP SDK, OpenTelemetry-ready

Документация на русском 🇷🇺 — 12 страниц описания каждого модуля с примерами промптов.

Буду рад фидбеку и звёздам ⭐. Если кто-то строит похожие интеграции — давайте спишемся, обсудим архитектуру.

#ServiceNow #MCP #LLM #OpenAI #Anthropic #DeepSeek #ITSM #Python #EnterpriseAI #Automation #OpenSource #AGPL

---

*Автор: Vlady | ServiceNow Developer & AI Architect | Май 2026*
