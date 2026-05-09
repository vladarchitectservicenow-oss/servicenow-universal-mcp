# Change Management

**ServiceNow Module:** Change Request (`change_request`)

## Purpose

Manage IT infrastructure change requests: from draft to approval and implementation. Risk-controlled process.

## Available MCP Tools

| Tool | Description |
|------|-------------|
| `change_list` | List changes with filters: type, approval status, planned date |
| `change_create` | Create a change request: description, type, risk, implementation plan |
| `change_approve` | Approve or reject a change request |

## Example Prompts

```
> What changes are planned for this weekend and their approval status?
> Create a standard change for the weekly patch cycle, Saturday 11 PM IST
> Show me all emergency changes from the last 7 days with their risk levels
> Approve CHG0001234 — "Risk assessed, implementation plan verified"
```

## Key Fields

- `number` — change number (CHG...)
- `type` — normal, standard, emergency
- `risk` — high, medium, low
- `approval` — requested, approved, rejected
- `state` — draft → approved → in progress → closed

---

*Author: Vlady | License: AGPL-3.0 | 2026*
