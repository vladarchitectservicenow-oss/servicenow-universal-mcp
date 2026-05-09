"""Обработчики (handlers) для всех MCP tools.

Каждый handler получает ServiceNowClient + аргументы и возвращает JSON-строку.
"""

from __future__ import annotations

from typing import Any

from .client import ServiceNowClient
from .tools import _ok, _err


class ToolHandlers:
    """Dispatcher: вызывает нужный метод модуля по имени tool."""

    def __init__(self, client: ServiceNowClient):
        self.client = client

    async def dispatch(self, name: str, args: dict[str, Any]) -> str:
        handler = getattr(self, f"handle_{name}", None)
        if not handler:
            return _err(f"Unknown tool: {name}")
        try:
            return await handler(args)
        except Exception as e:
            return _err(f"Tool '{name}' failed: {e}")

    # ══════════════════════════════════════════════════════════════════════
    # INCIDENT MANAGEMENT
    # ══════════════════════════════════════════════════════════════════════

    async def handle_incident_create(self, a: dict) -> str:
        payload = {
            "short_description": a["short_description"],
            "impact": "2", "urgency": "2",
        }
        if "priority" in a:
            payload["priority"] = str(a["priority"])
        if "category" in a:
            payload["category"] = a["category"]
        if "assignment_group" in a:
            grp = await self._resolve_group(a["assignment_group"])
            if grp:
                payload["assignment_group"] = grp
        if "caller_id" in a:
            user = await self._resolve_user(a["caller_id"])
            if user:
                payload["caller_id"] = user
        if "description" in a:
            payload["description"] = a["description"]

        result = await self.client.create("incident", payload)
        return _ok(incident=result, number=result.get("number"), sys_id=result.get("sys_id"))

    async def handle_incident_list(self, a: dict) -> str:
        query_parts = []
        if "state" in a:
            query_parts.append(f"state={a['state']}")
        if "priority" in a:
            query_parts.append(f"priority={a['priority']}")
        if "assignment_group" in a:
            grp = await self._resolve_group(a["assignment_group"])
            if grp:
                query_parts.append(f"assignment_group={grp}")
        if "assigned_to" in a:
            query_parts.append(f"assigned_to={a['assigned_to']}")

        limit = int(a.get("limit", 20))
        results = await self.client.list(
            "incident",
            fields=["number", "short_description", "priority", "state", "assignment_group", "assigned_to", "sys_created_on"],
            query="^".join(query_parts),
            limit=limit,
        )
        return _ok(incidents=results, count=len(results))

    async def handle_incident_get(self, a: dict) -> str:
        results = await self.client.list("incident", query=f"number={a['number']}", limit=1)
        if not results:
            return _err(f"Incident {a['number']} not found")
        return _ok(incident=results[0])

    async def handle_incident_update(self, a: dict) -> str:
        recs = await self.client.list("incident", query=f"number={a['number']}", limit=1)
        if not recs:
            return _err(f"Incident {a['number']} not found")
        sys_id = recs[0]["sys_id"]
        payload = {}
        if "state" in a:
            payload["state"] = a["state"]
        if "work_notes" in a:
            payload["work_notes"] = a["work_notes"]
        if "comments" in a:
            payload["comments"] = a["comments"]
        if "assignment_group" in a:
            grp = await self._resolve_group(a["assignment_group"])
            if grp:
                payload["assignment_group"] = grp
        result = await self.client.update("incident", sys_id, payload)
        return _ok(incident=result, number=result.get("number"))

    async def handle_incident_stats(self, a: dict) -> str:
        group_by = a.get("group_by", "state")
        # Получаем все инциденты и группируем
        all_incidents = await self.client.list("incident", fields=["state", "priority", "assignment_group", "category"], limit=200)
        groups: dict[str, int] = {}
        for inc in all_incidents:
            key = str(inc.get(group_by, "unknown"))
            groups[key] = groups.get(key, 0) + 1

        # Доп. статистика
        total = len(all_incidents)
        overdue = await self.client.count("incident", "active=true^sla_due<now")
        return _ok(
            total=total,
            overdue=overdue,
            by_field={group_by: groups},
        )

    # ══════════════════════════════════════════════════════════════════════
    # CHANGE MANAGEMENT
    # ══════════════════════════════════════════════════════════════════════

    async def handle_change_list(self, a: dict) -> str:
        query_parts = []
        if "type" in a:
            query_parts.append(f"type={a['type']}")
        if "approval" in a:
            query_parts.append(f"approval={a['approval']}")
        if "state" in a:
            query_parts.append(f"state={a['state']}")
        limit = int(a.get("limit", 20))
        results = await self.client.list(
            "change_request",
            fields=["number", "short_description", "type", "state", "approval", "risk", "sys_created_on"],
            query="^".join(query_parts),
            limit=limit,
        )
        return _ok(changes=results, count=len(results))

    async def handle_change_create(self, a: dict) -> str:
        payload = {"short_description": a["short_description"]}
        for f in ("type", "risk", "justification", "implementation_plan", "planned_start", "planned_end"):
            if f in a:
                payload[f] = a[f]
        result = await self.client.create("change_request", payload)
        return _ok(change=result, number=result.get("number"), sys_id=result.get("sys_id"))

    async def handle_change_approve(self, a: dict) -> str:
        recs = await self.client.list("change_request", query=f"number={a['number']}", limit=1)
        if not recs:
            return _err(f"Change {a['number']} not found")
        sys_id = recs[0]["sys_id"]
        payload = {
            "approval": "approved" if a["approved"] else "rejected",
        }
        if "comments" in a:
            payload["comments"] = a["comments"]
        result = await self.client.update("change_request", sys_id, payload)
        return _ok(change=result, number=result.get("number"))

    # ══════════════════════════════════════════════════════════════════════
    # PROBLEM MANAGEMENT
    # ══════════════════════════════════════════════════════════════════════

    async def handle_problem_create(self, a: dict) -> str:
        payload = {"short_description": a["short_description"]}
        if "description" in a:
            payload["description"] = a["description"]
        if "priority" in a:
            payload["priority"] = str(a["priority"])
        if "assignment_group" in a:
            grp = await self._resolve_group(a["assignment_group"])
            if grp:
                payload["assignment_group"] = grp
        result = await self.client.create("problem", payload)
        return _ok(problem=result, number=result.get("number"), sys_id=result.get("sys_id"))

    async def handle_problem_list(self, a: dict) -> str:
        query_parts = []
        if "state" in a:
            query_parts.append(f"state={a['state']}")
        if "assignment_group" in a:
            grp = await self._resolve_group(a["assignment_group"])
            if grp:
                query_parts.append(f"assignment_group={grp}")
        limit = int(a.get("limit", 20))
        results = await self.client.list(
            "problem",
            fields=["number", "short_description", "state", "priority", "assignment_group", "sys_created_on"],
            query="^".join(query_parts),
            limit=limit,
        )
        return _ok(problems=results, count=len(results))

    async def handle_problem_link_incidents(self, a: dict) -> str:
        # Найти проблему
        prb = await self.client.list("problem", query=f"number={a['problem_number']}", limit=1)
        if not prb:
            return _err(f"Problem {a['problem_number']} not found")
        problem_id = prb[0]["sys_id"]

        linked = []
        for inc_num in a["incident_numbers"]:
            incs = await self.client.list("incident", query=f"number={inc_num}", limit=1)
            if incs:
                await self.client.update("incident", incs[0]["sys_id"], {"problem_id": problem_id})
                linked.append(inc_num)
        return _ok(linked_incidents=linked, problem_number=a["problem_number"])

    # ══════════════════════════════════════════════════════════════════════
    # SERVICE CATALOG & REQUESTS
    # ══════════════════════════════════════════════════════════════════════

    async def handle_catalog_list(self, a: dict) -> str:
        query_parts = ["active=true"]
        if "search" in a:
            query_parts.append(f"nameLIKE{a['search']}")
        if "category" in a:
            query_parts.append(f"categoryLIKE{a['category']}")
        limit = int(a.get("limit", 20))
        results = await self.client.list(
            "sc_cat_item",
            fields=["sys_id", "name", "short_description", "category", "sys_class_name"],
            query="^".join(query_parts),
            limit=limit,
        )
        return _ok(catalog_items=results, count=len(results))

    async def handle_request_create(self, a: dict) -> str:
        # Найти catalog item
        items = await self.client.list("sc_cat_item", query=f"nameLIKE{a['catalog_item_name']}", limit=1)
        if not items:
            return _err(f"Catalog item '{a['catalog_item_name']}' not found")

        # Найти пользователя
        user_id = await self._resolve_user(a["requested_for"])
        if not user_id:
            return _err(f"User '{a['requested_for']}' not found")

        # Создать запрос через Cart API
        import httpx
        from base64 import b64encode

        auth = b64encode(f"{self.client.config.username}:{self.client.config.password}".encode()).decode()
        cart_url = f"{self.client._base}/api/sn_sc/servicecatalog/cart"
        headers = {
            "Authorization": f"Basic {auth}",
            "Content-Type": "application/json",
            "Accept": "application/json",
        }

        async with httpx.AsyncClient(timeout=30) as c:
            # Add to cart
            add_resp = await c.post(cart_url, headers=headers, json={
                "sysparm_id": items[0]["sys_id"],
                "sysparm_quantity": a.get("quantity", 1),
                "variables": a.get("variables", {}),
            })
            add_resp.raise_for_status()

            # Checkout
            checkout_resp = await c.post(
                f"{self.client._base}/api/sn_sc/servicecatalog/cart/checkout",
                headers=headers,
            )
            checkout_resp.raise_for_status()
            result = checkout_resp.json()

        return _ok(
            request=result,
            catalog_item=a["catalog_item_name"],
            requested_for=a["requested_for"],
        )

    async def handle_request_status(self, a: dict) -> str:
        number = a["number"]
        # Пробуем разные таблицы
        for table, prefix in [("sc_request", "REQ"), ("sc_req_item", "RITM"), ("sc_task", "SCTASK")]:
            if number.startswith(prefix):
                results = await self.client.list(table, query=f"number={number}", limit=1)
                if results:
                    return _ok(status=results[0], table=table)
        return _err(f"Request {number} not found in any table")

    async def handle_request_approvals(self, a: dict) -> str:
        query = ""
        if "approver" in a:
            user = await self._resolve_user(a["approver"])
            if user:
                query = f"approver={user}"
        results = await self.client.list(
            "sysapproval_approver",
            fields=["sys_id", "sysapproval", "approver", "state", "sys_created_on", "comments"],
            query=f"state=requested^{query}" if query else "state=requested",
            limit=30,
        )
        return _ok(pending_approvals=results, count=len(results))

    # ══════════════════════════════════════════════════════════════════════
    # CMDB
    # ══════════════════════════════════════════════════════════════════════

    async def handle_cmdb_search(self, a: dict) -> str:
        query_parts = []
        if "name" in a:
            query_parts.append(f"nameLIKE{a['name']}")
        if "class" in a:
            query_parts.append(f"sys_class_nameLIKE{a['class']}")
        if "environment" in a:
            query_parts.append(f"environment={a['environment']}")
        limit = int(a.get("limit", 30))
        results = await self.client.list(
            "cmdb_ci",
            fields=["sys_id", "name", "sys_class_name", "environment", "operational_status", "location", "owned_by", "sys_updated_on"],
            query="^".join(query_parts) if query_parts else "",
            limit=limit,
        )
        return _ok(cis=results, count=len(results))

    async def handle_cmdb_relationships(self, a: dict) -> str:
        cis = await self.client.list("cmdb_ci", query=f"name={a['ci_name']}", limit=1)
        if not cis:
            return _err(f"CI '{a['ci_name']}' not found")
        ci_id = cis[0]["sys_id"]

        # Отношения, где этот CI — родитель
        child_rels = await self.client.list(
            "cmdb_rel_ci",
            fields=["sys_id", "child", "type", "relationship_type"],
            query=f"parent={ci_id}",
            limit=50,
        )
        # Отношения, где этот CI — потомок
        parent_rels = await self.client.list(
            "cmdb_rel_ci",
            fields=["sys_id", "parent", "type", "relationship_type"],
            query=f"child={ci_id}",
            limit=50,
        )
        return _ok(
            ci_name=a["ci_name"],
            depends_on=parent_rels,
            dependents=child_rels,
        )

    async def handle_cmdb_health(self, a: dict) -> str:
        check = a.get("check", "all")
        result = {}

        if check in ("duplicates", "all"):
            # CI с одинаковыми именами
            total = await self.client.count("cmdb_ci")
            result["total_cis"] = total

        if check in ("orphans", "all"):
            # CI без отношений
            # (упрощённо — считаем общее количество)
            result["cmdb_orphans_note"] = "Orphan detection requires CMDB Health plugin. Run cmdb_search with empty query for full CI list."

        if check in ("stale", "all"):
            result["cmdb_stale_note"] = "Stale CI detection requires CMDB Health plugin (sys_updated_on < 90 days)."

        return _ok(**result)

    # ══════════════════════════════════════════════════════════════════════
    # KNOWLEDGE BASE
    # ══════════════════════════════════════════════════════════════════════

    async def handle_kb_search(self, a: dict) -> str:
        query_parts = ["workflow_state=published"]
        if "query" in a:
            # Split query into words and search across multiple fields
            words = a["query"].split()
            search_terms = "^OR".join([f"short_descriptionLIKE{w}^{w}textLIKE{w}" for w in words])
            query_parts.append(search_terms)

        limit = int(a.get("limit", 10))
        results = await self.client.list(
            "kb_knowledge",
            fields=["sys_id", "number", "short_description", "text", "category", "workflow_state", "sys_updated_on"],
            query="^".join(query_parts),
            limit=limit,
        )
        return _ok(articles=results, count=len(results))

    # ══════════════════════════════════════════════════════════════════════
    # REPORTING & ANALYTICS
    # ══════════════════════════════════════════════════════════════════════

    async def handle_report_performance(self, a: dict) -> str:
        metric = a.get("metric", "mttr")
        group = a.get("assignment_group", "")

        if metric == "sla_breach":
            count = await self.client.count("task_sla", "breached=true")
            return _ok(metric="sla_breach", breached_count=count)

        if metric == "mttr":
            # Среднее время решения (упрощённо)
            resolved = await self.client.list("incident", query="state=6", limit=500)
            return _ok(metric="mttr", resolved_count=len(resolved), note="Full MTTR calculation requires time-series analysis")

        if metric == "group_load":
            incidents = await self.client.list("incident", fields=["assignment_group", "state"], query="active=true", limit=200)
            group_load: dict[str, int] = {}
            for inc in incidents:
                grp = inc.get("assignment_group", {})
                grp_name = grp.get("display_value", "unassigned") if isinstance(grp, dict) else str(grp)
                group_load[grp_name] = group_load.get(grp_name, 0) + 1
            return _ok(metric="group_load", groups=sorted(group_load.items(), key=lambda x: -x[1]))

        if metric == "overdue_trend":
            overdue = await self.client.count("incident", "active=true^overdue=true")
            total_active = await self.client.count("incident", "active=true")
            rate = round(overdue / total_active * 100, 1) if total_active else 0
            return _ok(metric="overdue_trend", overdue_count=overdue, total_active=total_active, overdue_pct=rate)

        return _ok(message=f"Report type '{metric}' — use one of: sla_breach, mttr, group_load, overdue_trend")

    # ══════════════════════════════════════════════════════════════════════
    # WORKFLOW
    # ══════════════════════════════════════════════════════════════════════

    async def handle_workflow_list(self, a: dict) -> str:
        query = ""
        if "name" in a:
            query = f"nameLIKE{a['name']}"
        limit = int(a.get("limit", 20))
        results = await self.client.list(
            "wf_workflow_version",
            fields=["sys_id", "name", "table", "published", "version", "sys_updated_on"],
            query=f"published=true^{query}" if query else "published=true",
            limit=limit,
        )
        return _ok(workflows=results, count=len(results))

    # ══════════════════════════════════════════════════════════════════════
    # INTEGRATIONS
    # ══════════════════════════════════════════════════════════════════════

    async def handle_integration_list(self, a: dict) -> str:
        query = "active=true"
        if "name" in a:
            query += f"^nameLIKE{a['name']}"
        limit = int(a.get("limit", 20))
        results = await self.client.list(
            "sys_rest_message",
            fields=["sys_id", "name", "endpoint", "active", "authentication_type", "sys_updated_on"],
            query=query,
            limit=limit,
        )
        return _ok(integrations=results, count=len(results))

    # ══════════════════════════════════════════════════════════════════════
    # BUSINESS RULES
    # ══════════════════════════════════════════════════════════════════════

    async def handle_business_rule_list(self, a: dict) -> str:
        table = a.get("table", "incident")
        query = f"collection={table}"
        if a.get("active", True):
            query += "^active=true"
        limit = int(a.get("limit", 20))
        results = await self.client.list(
            "sys_script",
            fields=["sys_id", "name", "collection", "when", "active", "script", "sys_updated_on"],
            query=query,
            limit=limit,
        )
        return _ok(business_rules=results, count=len(results), table=table)

    # ══════════════════════════════════════════════════════════════════════
    # USER & GROUP
    # ══════════════════════════════════════════════════════════════════════

    async def handle_user_info(self, a: dict) -> str:
        if "email" in a:
            results = await self.client.list("sys_user", query=f"email={a['email']}", limit=1)
        elif "name" in a:
            results = await self.client.list("sys_user", query=f"nameLIKE{a['name']}", limit=5)
        else:
            return _err("Specify email or name")
        return _ok(users=results, count=len(results))

    async def handle_group_members(self, a: dict) -> str:
        groups = await self.client.list("sys_user_group", query=f"nameLIKE{a['group_name']}", limit=1)
        if not groups:
            return _err(f"Group '{a['group_name']}' not found")
        group_id = groups[0]["sys_id"]
        members = await self.client.list(
            "sys_user_grmember",
            fields=["sys_id", "user", "group"],
            query=f"group={group_id}",
            limit=50,
        )
        user_ids = [m["user"]["value"] for m in members if isinstance(m.get("user"), dict)]
        return _ok(
            group=groups[0]["name"],
            group_sys_id=group_id,
            member_count=len(members),
            member_user_ids=user_ids,
        )

    # ══════════════════════════════════════════════════════════════════════
    # HELPERS
    # ══════════════════════════════════════════════════════════════════════

    async def _resolve_group(self, name: str) -> str | None:
        """Resolve group name → sys_id."""
        groups = await self.client.list("sys_user_group", query=f"nameLIKE{name}", limit=1)
        return groups[0]["sys_id"] if groups else None

    async def _resolve_user(self, email_or_name: str) -> str | None:
        """Resolve user email/name → sys_id."""
        users = await self.client.list("sys_user", query=f"email={email_or_name}^ORnameLIKE{email_or_name}", limit=1)
        return users[0]["sys_id"] if users else None
