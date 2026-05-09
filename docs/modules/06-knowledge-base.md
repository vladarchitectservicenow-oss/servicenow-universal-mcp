# Knowledge Base

**ServiceNow Module:** Knowledge Articles (`kb_knowledge`)

## Purpose

Search published knowledge base articles by keywords. Help users and agents resolve issues faster.

## Available MCP Tools

| Tool | Description |
|------|-------------|
| `kb_search` | Search articles by query and category |

## Example Prompts

```
> How to configure VPN on macOS?
> Find articles about password reset
> What does the KB say about "MFA setup"?
```

## Key Fields

- `kb_knowledge` — articles table
- `workflow_state=published` — only published articles returned
- Search across `short_description` and `text` fields
- 53 articles on test PDI (May 2026)

---

*Author: Vlady | License: AGPL-3.0 | 2026*
