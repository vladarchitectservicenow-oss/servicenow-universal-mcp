# Users & Groups

**ServiceNow Module:** Users (`sys_user`), Groups (`sys_user_group`), Group Members (`sys_user_grmember`)

## Purpose

Look up users and groups, list group members, verify roles and assignments.

## Available MCP Tools

| Tool | Description |
|------|-------------|
| `user_info` | Search users by email or name |
| `group_members` | List group members with count |

## Example Prompts

```
> Find user vasily.pupkin@company.com
> Who is in the DBA Team group?
> Show all members of Service Desk
```

## Key Fields

- `email` — user email address
- `group` → `user` — group-to-member relationship
- `sys_user` / `sys_user_group` / `sys_user_grmember`

---

*Author: Vlady | License: AGPL-3.0 | 2026*
