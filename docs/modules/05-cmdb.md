# CMDB — Configuration Management

**ServiceNow Module:** Configuration Items (`cmdb_ci`), Relationships (`cmdb_rel_ci`)

## Purpose

Track and manage Configuration Items (CIs): servers, applications, databases, network devices. Map dependencies between them.

## Available MCP Tools

| Tool | Description |
|------|-------------|
| `cmdb_search` | Search CIs by name, class, environment |
| `cmdb_relationships` | Show dependencies: what depends on a CI and what it depends on |
| `cmdb_health` | CMDB health summary: duplicates, orphans, stale records |

## Example Prompts

```
> Find all servers in Production running Windows Server 2019
> Which applications depend on PROD-DB-01?
> Show dependencies for the SAP cluster
> Give me a CMDB health summary
```

## Key Fields

- `name` — CI name
- `sys_class_name` — class (Server, Application, Database, Network Gear...)
- `environment` — Production, Test, Development, Staging
- `cmdb_rel_ci` — parent → child relationships

---

*Author: Vlady | License: AGPL-3.0 | 2026*
