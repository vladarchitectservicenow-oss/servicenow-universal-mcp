# Workflows & Flow Designer

**ServiceNow Module:** Workflow Versions (`wf_workflow_version`), Flows

## Purpose

View and audit automated workflows and flows published in the system.

## Available MCP Tools

| Tool | Description |
|------|-------------|
| `workflow_list` | List published workflows with name search |

## Example Prompts

```
> Show all published workflows
> Find workflows related to onboarding
> How many active flows are tied to incident management?
```

## Key Fields

- `wf_workflow_version` — workflow version records
- `published=true` — only published workflows returned
- 6 workflows on test PDI (May 2026)
- ServiceNow Australia: Workflow Studio unifies Flow Designer + Playbooks + Decision Tables

---

*Author: Vlady | License: AGPL-3.0 | 2026*
