# Problem Management

**ServiceNow Module:** Problem (`problem`)

## Purpose

Root cause analysis of incidents. Eliminate recurring failures and prevent future incidents.

## Available MCP Tools

| Tool | Description |
|------|-------------|
| `problem_create` | Create a problem record: description, priority, assignment group |
| `problem_list` | List problems with filters: state, assignment group |
| `problem_link_incidents` | Link incidents to a problem for root cause analysis |

## Example Prompts

```
> Create a problem for recurring VPN disconnection issues at the Hyderabad site
> Link INC001111, INC001122, INC001133 to problem PRB0000456
> What root cause is documented for PRB0000456?
> Show all open problems assigned to the Network team
```

## Key Fields

- `number` — problem number (PRB...)
- `state` — 1=Open, 2=In Progress, 3=Resolved, 4=Closed
- `problem_id` on incident — incident → problem linkage

---

*Author: Vlady | License: AGPL-3.0 | 2026*
