# Incident Management

**ServiceNow Module:** Incident (`incident`)

## Purpose

Manage the full incident lifecycle — from creation to resolution. Restore normal service operations after disruptions.

## Available MCP Tools

| Tool | Description |
|------|-------------|
| `incident_create` | Create a new incident: description, priority, category, assignment group |
| `incident_list` | List incidents with filters: state, priority, assignment group, assignee |
| `incident_get` | Get full details of a specific incident by number |
| `incident_update` | Update an incident: change state, add work notes, reassign |
| `incident_stats` | Incident statistics: group by state, priority, category, overdue |

## Example Prompts

```
> Create a P1 incident for production database outage, category Database, assign to DBA team
> Show all critical incidents open for more than 24 hours
> How many overdue incidents do we have?
> Resolve INC0012345 with the comment "Fixed — applied patch v3.2.1"
```

## Key Fields

- `number` — incident number (INC...)
- `state` — 1=New, 2=In Progress, 3=On Hold, 6=Resolved, 7=Closed
- `priority` — 1 (Critical), 2 (High), 3 (Moderate), 4 (Low), 5 (Planning)
- `assignment_group` — target assignment group
- `category` — Hardware, Software, Network, Database

---

*Author: Vlady | License: AGPL-3.0 | 2026*
