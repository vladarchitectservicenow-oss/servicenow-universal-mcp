# Reporting & Analytics

**ServiceNow Module:** SLA (`task_sla`), Incidents, Performance Analytics

## Purpose

IT support performance metrics: SLA breaches, Mean Time to Resolution (MTTR), group workload, overdue trends.

## Available MCP Tools

| Tool | Description |
|------|-------------|
| `report_performance` | Multi-metric: sla_breach, mttr, group_load, overdue_trend |

## Example Prompts

```
> How many SLA breaches today?
> Which group has the heaviest workload right now?
> Show me the percentage of overdue incidents this month
> What's the average resolution time for critical incidents?
```

## Available Metrics

| Metric | What it shows |
|--------|---------------|
| `sla_breach` | Count of breached SLAs |
| `mttr` | Mean Time to Resolution (resolved incidents) |
| `group_load` | Active incidents per assignment group |
| `overdue_trend` | % of active incidents past due date |

---

*Author: Vlady | License: AGPL-3.0 | 2026*
