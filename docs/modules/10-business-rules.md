# Business Rules & Scripts

**ServiceNow Module:** Scripts (`sys_script`), Business Rules

## Purpose

Audit business rules on tables — server-side scripts that trigger on record operations.

## Available MCP Tools

| Tool | Description |
|------|-------------|
| `business_rule_list` | List business rules on a table: active, conditions, scripts |

## Example Prompts

```
> Show all business rules on the incident table
> How many active rules are on sc_req_item?
> Find rules that fire on insert for change_request
```

## Key Fields

- `collection` — table name
- `when` — trigger condition (before/after insert/update/delete)
- `active` — 5,654 business rules on test PDI
- `script` — script body

---

*Author: Vlady | License: AGPL-3.0 | 2026*
