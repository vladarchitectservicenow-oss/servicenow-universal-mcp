# Service Catalog & Requests

**ServiceNow Module:** Catalog Items (`sc_cat_item`), Requests (`sc_request`, `sc_req_item`)

## Purpose

Browse the service catalog, raise requests, check status, and manage approvals — through conversation, without navigating the self-service portal.

## Available MCP Tools

| Tool | Description |
|------|-------------|
| `catalog_list` | Search catalog items by name and category |
| `request_create` | Create a service request via Cart API (auto checkout) |
| `request_status` | Check request status by number (REQ/RITM/SCTASK) |
| `request_approvals` | Show all pending approval requests |

## Example Prompts

```
> Find "VPN Access" in the service catalog
> Raise a software access request for Adobe Acrobat for sarah.jones@company.com
> What's the current status of my request REQ0098765?
> Show all requests awaiting my approval
```

## Key Fields

- `sc_cat_item` — catalog items (197 total on test PDI, 147 active)
- `sc_request` (REQ) → `sc_req_item` (RITM) → `sc_task` (SCTASK)
- Requests are created through the Service Catalog Cart API

---

*Author: Vlady | License: AGPL-3.0 | 2026*
