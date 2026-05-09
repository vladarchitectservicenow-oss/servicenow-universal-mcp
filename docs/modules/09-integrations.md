# Integrations

**ServiceNow Module:** REST Messages (`sys_rest_message`), Webhooks

## Purpose

Audit and view external integrations: REST API connections to third-party services, endpoints, authentication types.

## Available MCP Tools

| Tool | Description |
|------|-------------|
| `integration_list` | List active REST integrations with endpoints |

## Example Prompts

```
> Show all external integrations with their endpoints
> Is there an integration with Azure AD?
> Find all integrations related to monitoring
```

## Key Fields

- `endpoint` — external API URL
- `authentication_type` — basic, oauth, api_key
- `active=true` — 11 integrations on test PDI (Azure AD, Slack, Jira, Okta, AWS, Datadog, SAP...)

---

*Author: Vlady | License: AGPL-3.0 | 2026*
