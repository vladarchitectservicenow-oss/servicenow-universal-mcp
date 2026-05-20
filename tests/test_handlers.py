# Copyright (c) 2026 Vlady
# SPDX-License-Identifier: AGPL-3.0-only

"""Тесты для modules/__init__.py — ToolHandlers и все 26 tool handlers."""

from __future__ import annotations

import json
from unittest.mock import AsyncMock, patch

import pytest
from mcp_server.modules import ToolHandlers
from mcp_server.client import ServiceNowClient
from mcp_server.config import SNConfig


# ═══════════════════════════════════════════════════════════════════════════
# Fixtures
# ═══════════════════════════════════════════════════════════════════════════


@pytest.fixture
def sn_config():
    return SNConfig(
        url="https://test.service-now.com",
        username="admin",
        password="test",
    )


@pytest.fixture
def client(sn_config):
    return ServiceNowClient(sn_config)


@pytest.fixture
def handlers(client):
    return ToolHandlers(client)


def parse_json(result: str) -> dict:
    return json.loads(result)


# ═══════════════════════════════════════════════════════════════════════════
# Dispatch
# ═══════════════════════════════════════════════════════════════════════════


class TestDispatch:
    async def test_unknown_tool(self, handlers):
        result = await handlers.dispatch("nonexistent", {})
        data = parse_json(result)
        assert data["success"] is False
        assert "Unknown tool" in data["error"]

    async def test_validation_error(self, handlers):
        result = await handlers.dispatch("incident_create", {})
        data = parse_json(result)
        assert data["success"] is False
        assert "Validation error" in data["error"]


# ═══════════════════════════════════════════════════════════════════════════
# INCIDENT MANAGEMENT
# ═══════════════════════════════════════════════════════════════════════════


class TestIncidentCreate:
    async def test_minimal(self, handlers):
        with patch.object(
            handlers.client, "create", new_callable=AsyncMock
        ) as mock_create:
            mock_create.return_value = {"sys_id": "abc123", "number": "INC0010001"}
            result = await handlers.dispatch(
                "incident_create", {"short_description": "Test"}
            )
            data = parse_json(result)
            assert data["success"] is True
            assert data["number"] == "INC0010001"
            mock_create.assert_called_once()

    async def test_missing_required(self, handlers):
        result = await handlers.dispatch("incident_create", {"priority": 1})
        data = parse_json(result)
        assert data["success"] is False

    async def test_priority_out_of_range(self, handlers):
        result = await handlers.dispatch(
            "incident_create", {"short_description": "X", "priority": 99}
        )
        data = parse_json(result)
        assert data["success"] is False

    async def test_description_too_long(self, handlers):
        result = await handlers.dispatch(
            "incident_create",
            {
                "short_description": "X",
                "description": "A" * 5000,
            },
        )
        data = parse_json(result)
        assert data["success"] is False


class TestIncidentList:
    async def test_defaults(self, handlers):
        with patch.object(handlers.client, "list", new_callable=AsyncMock) as mock_list:
            mock_list.return_value = []
            result = await handlers.dispatch("incident_list", {})
            data = parse_json(result)
            assert data["success"] is True
            assert data["count"] == 0

    async def test_with_filters(self, handlers):
        with patch.object(handlers.client, "list", new_callable=AsyncMock) as mock_list:
            mock_list.return_value = [{"number": "INC001"}]
            result = await handlers.dispatch(
                "incident_list", {"state": "1", "limit": 50}
            )
            data = parse_json(result)
            assert data["success"] is True
            args = mock_list.call_args[1]
            assert "state=1" in args["query"] or "state" in str(args)

    async def test_limit_too_high(self, handlers):
        result = await handlers.dispatch("incident_list", {"limit": 9999})
        data = parse_json(result)
        assert data["success"] is False


class TestIncidentGet:
    async def test_found(self, handlers):
        with patch.object(handlers.client, "list", new_callable=AsyncMock) as mock_list:
            mock_list.return_value = [{"number": "INC001"}]
            result = await handlers.dispatch("incident_get", {"number": "INC001"})
            data = parse_json(result)
            assert data["success"] is True

    async def test_not_found(self, handlers):
        with patch.object(handlers.client, "list", new_callable=AsyncMock) as mock_list:
            mock_list.return_value = []
            result = await handlers.dispatch("incident_get", {"number": "INC999"})
            data = parse_json(result)
            assert data["success"] is False
            assert "not found" in data["error"]


class TestIncidentStats:
    async def test_default_grouping(self, handlers):
        with patch.object(
            handlers.client, "count", new_callable=AsyncMock
        ) as mock_count:
            with patch.object(
                handlers.client, "list", new_callable=AsyncMock
            ) as mock_list:
                mock_count.return_value = 15
                mock_list.return_value = [
                    {"state": "1"},
                    {"state": "2"},
                    {"state": "2"},
                ]
                result = await handlers.dispatch("incident_stats", {})
                data = parse_json(result)
                assert data["success"] is True
                assert "total" in data


# ═══════════════════════════════════════════════════════════════════════════
# CHANGE MANAGEMENT
# ═══════════════════════════════════════════════════════════════════════════


class TestChangeCreate:
    async def test_minimal(self, handlers):
        with patch.object(handlers.client, "create", new_callable=AsyncMock) as mock:
            mock.return_value = {"number": "CHG001", "sys_id": "chg1"}
            result = await handlers.dispatch(
                "change_create", {"short_description": "Upgrade DB"}
            )
            data = parse_json(result)
            assert data["success"] is True
            assert data["number"] == "CHG001"


class TestChangeApprove:
    async def test_approve(self, handlers):
        with patch.object(handlers.client, "list", new_callable=AsyncMock) as mock_list:
            with patch.object(
                handlers.client, "update", new_callable=AsyncMock
            ) as mock_update:
                mock_list.return_value = [{"sys_id": "chg1", "number": "CHG001"}]
                mock_update.return_value = {"number": "CHG001", "approval": "approved"}
                result = await handlers.dispatch(
                    "change_approve", {"number": "CHG001", "approved": True}
                )
                data = parse_json(result)
                assert data["success"] is True

    async def test_reject(self, handlers):
        with patch.object(handlers.client, "list", new_callable=AsyncMock) as mock_list:
            with patch.object(
                handlers.client, "update", new_callable=AsyncMock
            ) as mock_update:
                mock_list.return_value = [{"sys_id": "chg1"}]
                mock_update.return_value = {"number": "CHG001"}
                result = await handlers.dispatch(
                    "change_approve", {"number": "CHG001", "approved": False}
                )
                data = parse_json(result)
                assert data["success"] is True


class TestChangeList:
    async def test_empty(self, handlers):
        with patch.object(handlers.client, "list", new_callable=AsyncMock) as mock:
            mock.return_value = []
            result = await handlers.dispatch("change_list", {})
            data = parse_json(result)
            assert data["success"] is True


# ═══════════════════════════════════════════════════════════════════════════
# PROBLEM MANAGEMENT
# ═══════════════════════════════════════════════════════════════════════════


class TestProblemCreate:
    async def test_minimal(self, handlers):
        with patch.object(handlers.client, "create", new_callable=AsyncMock) as mock:
            mock.return_value = {"number": "PRB001"}
            result = await handlers.dispatch(
                "problem_create", {"short_description": "Root cause"}
            )
            data = parse_json(result)
            assert data["success"] is True


class TestProblemList:
    async def test_empty(self, handlers):
        with patch.object(handlers.client, "list", new_callable=AsyncMock) as mock:
            mock.return_value = []
            result = await handlers.dispatch("problem_list", {})
            data = parse_json(result)
            assert data["success"] is True


class TestProblemLinkIncidents:
    async def test_link(self, handlers):
        with patch.object(handlers.client, "list", new_callable=AsyncMock) as mock_list:
            with patch.object(handlers.client, "update", new_callable=AsyncMock):
                mock_list.side_effect = [
                    [{"sys_id": "prb1"}],  # проблема
                    [{"sys_id": "inc1"}],  # инцидент 1
                    [{"sys_id": "inc2"}],  # инцидент 2
                ]
                result = await handlers.dispatch(
                    "problem_link_incidents",
                    {
                        "problem_number": "PRB001",
                        "incident_numbers": ["INC001", "INC002"],
                    },
                )
                data = parse_json(result)
                assert data["success"] is True
                assert len(data["linked_incidents"]) == 2


# ═══════════════════════════════════════════════════════════════════════════
# SERVICE CATALOG
# ═══════════════════════════════════════════════════════════════════════════


class TestCatalogList:
    async def test_empty(self, handlers):
        with patch.object(handlers.client, "list", new_callable=AsyncMock) as mock:
            mock.return_value = []
            result = await handlers.dispatch("catalog_list", {})
            data = parse_json(result)
            assert data["success"] is True

    async def test_with_search(self, handlers):
        with patch.object(handlers.client, "list", new_callable=AsyncMock) as mock:
            mock.return_value = [{"name": "Laptop"}]
            result = await handlers.dispatch("catalog_list", {"search": "laptop"})
            data = parse_json(result)
            assert data["success"] is True


class TestRequestStatus:
    async def test_req(self, handlers):
        with patch.object(handlers.client, "list", new_callable=AsyncMock) as mock:
            mock.return_value = [{"number": "REQ001"}]
            result = await handlers.dispatch("request_status", {"number": "REQ001"})
            data = parse_json(result)
            assert data["success"] is True

    async def test_ritm(self, handlers):
        with patch.object(handlers.client, "list", new_callable=AsyncMock) as mock:
            mock.return_value = [{"number": "RITM001"}]
            result = await handlers.dispatch("request_status", {"number": "RITM001"})
            data = parse_json(result)
            assert data["success"] is True

    async def test_sctask(self, handlers):
        with patch.object(handlers.client, "list", new_callable=AsyncMock) as mock:
            mock.return_value = [{"number": "SCTASK001"}]
            result = await handlers.dispatch("request_status", {"number": "SCTASK001"})
            data = parse_json(result)
            assert data["success"] is True


class TestRequestApprovals:
    async def test_empty(self, handlers):
        with patch.object(handlers.client, "list", new_callable=AsyncMock) as mock:
            mock.return_value = []
            result = await handlers.dispatch("request_approvals", {})
            data = parse_json(result)
            assert data["success"] is True


# ═══════════════════════════════════════════════════════════════════════════
# CMDB
# ═══════════════════════════════════════════════════════════════════════════


class TestCMDBSearch:
    async def test_all(self, handlers):
        with patch.object(handlers.client, "list", new_callable=AsyncMock) as mock:
            mock.return_value = [{"name": "PROD-DB-01"}]
            result = await handlers.dispatch("cmdb_search", {})
            data = parse_json(result)
            assert data["success"] is True

    async def test_by_environment(self, handlers):
        with patch.object(handlers.client, "list", new_callable=AsyncMock) as mock:
            mock.return_value = []
            result = await handlers.dispatch(
                "cmdb_search", {"environment": "Production"}
            )
            data = parse_json(result)
            assert data["success"] is True


class TestCMDBRelationships:
    async def test_found(self, handlers):
        with patch.object(handlers.client, "list", new_callable=AsyncMock) as mock:
            mock.side_effect = [
                [{"sys_id": "ci1"}],  # сам CI
                [{"sys_id": "rel1", "child": "ci2"}],  # дочерние
                [{"sys_id": "rel2", "parent": "ci0"}],  # родительские
            ]
            result = await handlers.dispatch(
                "cmdb_relationships", {"ci_name": "PROD-DB-01"}
            )
            data = parse_json(result)
            assert data["success"] is True
            assert "depends_on" in data
            assert "dependents" in data

    async def test_not_found(self, handlers):
        with patch.object(handlers.client, "list", new_callable=AsyncMock) as mock:
            mock.return_value = []
            result = await handlers.dispatch(
                "cmdb_relationships", {"ci_name": "NONEXISTENT"}
            )
            data = parse_json(result)
            assert data["success"] is False


class TestCMDBHealth:
    async def test_all(self, handlers):
        with patch.object(
            handlers.client, "count", new_callable=AsyncMock
        ) as mock_count:
            with patch.object(
                handlers.client, "list", new_callable=AsyncMock
            ) as mock_list:
                mock_count.side_effect = [100, 5]  # total, stale
                mock_list.return_value = [{"name": "Server-A"} for _ in range(50)]
                result = await handlers.dispatch("cmdb_health", {})
                data = parse_json(result)
                assert data["success"] is True
                assert "total_cis" in data


# ═══════════════════════════════════════════════════════════════════════════
# KNOWLEDGE BASE
# ═══════════════════════════════════════════════════════════════════════════


class TestKBSearch:
    async def test_search(self, handlers):
        with patch.object(handlers.client, "list", new_callable=AsyncMock) as mock:
            mock.return_value = [{"short_description": "VPN setup"}]
            result = await handlers.dispatch("kb_search", {"query": "VPN"})
            data = parse_json(result)
            assert data["success"] is True

    async def test_missing_query(self, handlers):
        result = await handlers.dispatch("kb_search", {})
        data = parse_json(result)
        assert data["success"] is False


# ═══════════════════════════════════════════════════════════════════════════
# REPORTING
# ═══════════════════════════════════════════════════════════════════════════


class TestReportPerformance:
    async def test_sla_breach(self, handlers):
        with patch.object(handlers.client, "count", new_callable=AsyncMock) as mock:
            mock.return_value = 3
            result = await handlers.dispatch(
                "report_performance", {"metric": "sla_breach"}
            )
            data = parse_json(result)
            assert data["success"] is True
            assert data["breached_count"] == 3

    async def test_mttr(self, handlers):
        with patch.object(handlers.client, "list", new_callable=AsyncMock) as mock:
            mock.return_value = [{"number": "INC001"}]
            result = await handlers.dispatch("report_performance", {"metric": "mttr"})
            data = parse_json(result)
            assert data["success"] is True

    async def test_group_load(self, handlers):
        with patch.object(handlers.client, "list", new_callable=AsyncMock) as mock:
            mock.return_value = [{"assignment_group": {"display_value": "DBA"}}]
            result = await handlers.dispatch(
                "report_performance", {"metric": "group_load"}
            )
            data = parse_json(result)
            assert data["success"] is True

    async def test_overdue_trend(self, handlers):
        with patch.object(handlers.client, "count", new_callable=AsyncMock) as mock:
            mock.side_effect = [5, 50]  # overdue, total_active
            result = await handlers.dispatch(
                "report_performance", {"metric": "overdue_trend"}
            )
            data = parse_json(result)
            assert data["success"] is True
            assert data["overdue_pct"] == 10.0

    async def test_unknown_metric(self, handlers):
        result = await handlers.dispatch(
            "report_performance", {"metric": "nonexistent"}
        )
        data = parse_json(result)
        assert data["success"] is True  # не ошибка, возвращает help


# ═══════════════════════════════════════════════════════════════════════════
# WORKFLOW
# ═══════════════════════════════════════════════════════════════════════════


class TestWorkflowList:
    async def test_empty(self, handlers):
        with patch.object(handlers.client, "list", new_callable=AsyncMock) as mock:
            mock.return_value = []
            result = await handlers.dispatch("workflow_list", {})
            data = parse_json(result)
            assert data["success"] is True


# ═══════════════════════════════════════════════════════════════════════════
# INTEGRATIONS
# ═══════════════════════════════════════════════════════════════════════════


class TestIntegrationList:
    async def test_empty(self, handlers):
        with patch.object(handlers.client, "list", new_callable=AsyncMock) as mock:
            mock.return_value = []
            result = await handlers.dispatch("integration_list", {})
            data = parse_json(result)
            assert data["success"] is True


# ═══════════════════════════════════════════════════════════════════════════
# BUSINESS RULES
# ═══════════════════════════════════════════════════════════════════════════


class TestBusinessRuleList:
    async def test_default_table(self, handlers):
        with patch.object(handlers.client, "list", new_callable=AsyncMock) as mock:
            mock.return_value = []
            result = await handlers.dispatch("business_rule_list", {})
            data = parse_json(result)
            assert data["success"] is True

    async def test_custom_table(self, handlers):
        with patch.object(handlers.client, "list", new_callable=AsyncMock) as mock:
            mock.return_value = [{"name": "Auto-close"}]
            result = await handlers.dispatch(
                "business_rule_list", {"table": "change_request"}
            )
            data = parse_json(result)
            assert data["success"] is True


# ═══════════════════════════════════════════════════════════════════════════
# USERS & GROUPS
# ═══════════════════════════════════════════════════════════════════════════


class TestUserInfo:
    async def test_by_email(self, handlers):
        with patch.object(handlers.client, "list", new_callable=AsyncMock) as mock:
            mock.return_value = [{"name": "John Doe"}]
            result = await handlers.dispatch("user_info", {"email": "john@example.com"})
            data = parse_json(result)
            assert data["success"] is True

    async def test_by_name(self, handlers):
        with patch.object(handlers.client, "list", new_callable=AsyncMock) as mock:
            mock.return_value = [{"name": "John Doe"}]
            result = await handlers.dispatch("user_info", {"name": "John"})
            data = parse_json(result)
            assert data["success"] is True

    async def test_no_args(self, handlers):
        result = await handlers.dispatch("user_info", {})
        data = parse_json(result)
        assert data["success"] is False


class TestGroupMembers:
    async def test_found(self, handlers):
        with patch.object(handlers.client, "list", new_callable=AsyncMock) as mock:
            mock.side_effect = [
                [{"sys_id": "grp1", "name": "DBA Team"}],  # группа
                [{"user": {"value": "u1"}}, {"user": {"value": "u2"}}],  # участники
            ]
            result = await handlers.dispatch("group_members", {"group_name": "DBA"})
            data = parse_json(result)
            assert data["success"] is True
            assert data["member_count"] == 2

    async def test_not_found(self, handlers):
        with patch.object(handlers.client, "list", new_callable=AsyncMock) as mock:
            mock.return_value = []
            result = await handlers.dispatch(
                "group_members", {"group_name": "NONEXISTENT"}
            )
            data = parse_json(result)
            assert data["success"] is False
