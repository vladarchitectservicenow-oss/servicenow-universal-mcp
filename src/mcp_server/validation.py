# Copyright (c) 2026 Vlady
# SPDX-License-Identifier: AGPL-3.0-only

"""Pydantic models for input validation — все аргументы MCP tools."""

from __future__ import annotations

from pydantic import BaseModel, Field, field_validator


# ═══════════════════════════════════════════════════════════════════════════
# INCIDENT MANAGEMENT
# ═══════════════════════════════════════════════════════════════════════════

class IncidentCreate(BaseModel):
    short_description: str = Field(..., min_length=1, max_length=160)
    priority: int | None = Field(default=None, ge=1, le=5)
    category: str | None = Field(default=None, max_length=80)
    assignment_group: str | None = Field(default=None, max_length=160)
    caller_id: str | None = Field(default=None, max_length=255)
    description: str | None = Field(default=None, max_length=4000)


class IncidentList(BaseModel):
    state: str | None = None
    priority: str | None = None
    assignment_group: str | None = None
    assigned_to: str | None = None
    limit: int = Field(default=20, ge=1, le=1000)


class IncidentGet(BaseModel):
    number: str = Field(..., min_length=1, max_length=40)


class IncidentUpdate(BaseModel):
    number: str = Field(..., min_length=1, max_length=40)
    state: str | None = None
    work_notes: str | None = Field(default=None, max_length=4000)
    comments: str | None = Field(default=None, max_length=4000)
    assignment_group: str | None = Field(default=None, max_length=160)


class IncidentStats(BaseModel):
    group_by: str = Field(default="state", max_length=40)
    limit: int = Field(default=1000, ge=1, le=10000)


# ═══════════════════════════════════════════════════════════════════════════
# CHANGE MANAGEMENT
# ═══════════════════════════════════════════════════════════════════════════

class ChangeList(BaseModel):
    type: str | None = None
    approval: str | None = None
    state: str | None = None
    planned_start: str | None = None
    limit: int = Field(default=20, ge=1, le=1000)


class ChangeCreate(BaseModel):
    short_description: str = Field(..., min_length=1, max_length=160)
    type: str | None = None
    risk: str | None = None
    justification: str | None = Field(default=None, max_length=4000)
    implementation_plan: str | None = Field(default=None, max_length=4000)
    planned_start: str | None = None
    planned_end: str | None = None


class ChangeApprove(BaseModel):
    number: str = Field(..., min_length=1, max_length=40)
    approved: bool = ...
    comments: str | None = Field(default=None, max_length=4000)


# ═══════════════════════════════════════════════════════════════════════════
# PROBLEM MANAGEMENT
# ═══════════════════════════════════════════════════════════════════════════

class ProblemCreate(BaseModel):
    short_description: str = Field(..., min_length=1, max_length=160)
    description: str | None = Field(default=None, max_length=4000)
    assignment_group: str | None = None
    priority: int | None = Field(default=None, ge=1, le=5)


class ProblemList(BaseModel):
    state: str | None = None
    assignment_group: str | None = None
    limit: int = Field(default=20, ge=1, le=1000)


class ProblemLinkIncidents(BaseModel):
    problem_number: str = Field(..., min_length=1, max_length=40)
    incident_numbers: list[str] = Field(..., min_length=1, max_length=100)


# ═══════════════════════════════════════════════════════════════════════════
# SERVICE CATALOG
# ═══════════════════════════════════════════════════════════════════════════

class CatalogList(BaseModel):
    search: str | None = None
    category: str | None = None
    limit: int = Field(default=20, ge=1, le=1000)


class RequestCreate(BaseModel):
    catalog_item_name: str = Field(..., min_length=1, max_length=200)
    requested_for: str = Field(..., min_length=1, max_length=255)
    quantity: int = Field(default=1, ge=1, le=100)
    variables: dict | None = None


class RequestStatus(BaseModel):
    number: str = Field(..., min_length=1, max_length=40)


class RequestApprovals(BaseModel):
    approver: str | None = None


# ═══════════════════════════════════════════════════════════════════════════
# CMDB
# ═══════════════════════════════════════════════════════════════════════════

class CMDBSearch(BaseModel):
    name: str | None = None
    class_: str | None = Field(default=None, alias="class")
    environment: str | None = None
    limit: int = Field(default=30, ge=1, le=1000)


class CMDBRelationships(BaseModel):
    ci_name: str = Field(..., min_length=1, max_length=255)


class CMDBHealth(BaseModel):
    check: str = Field(default="all")


# ═══════════════════════════════════════════════════════════════════════════
# KNOWLEDGE BASE
# ═══════════════════════════════════════════════════════════════════════════

class KBSearch(BaseModel):
    query: str = Field(..., min_length=1, max_length=500)
    category: str | None = None
    limit: int = Field(default=10, ge=1, le=100)


# ═══════════════════════════════════════════════════════════════════════════
# REPORTING
# ═══════════════════════════════════════════════════════════════════════════

class ReportPerformance(BaseModel):
    metric: str = Field(..., max_length=40)
    period: str | None = None
    assignment_group: str | None = None


# ═══════════════════════════════════════════════════════════════════════════
# WORKFLOW
# ═══════════════════════════════════════════════════════════════════════════

class WorkflowList(BaseModel):
    name: str | None = None
    limit: int = Field(default=20, ge=1, le=1000)


# ═══════════════════════════════════════════════════════════════════════════
# INTEGRATIONS
# ═══════════════════════════════════════════════════════════════════════════

class IntegrationList(BaseModel):
    name: str | None = None
    limit: int = Field(default=20, ge=1, le=1000)


# ═══════════════════════════════════════════════════════════════════════════
# BUSINESS RULES
# ═══════════════════════════════════════════════════════════════════════════

class BusinessRuleList(BaseModel):
    table: str = Field(default="incident", max_length=80)
    active: bool = True
    limit: int = Field(default=20, ge=1, le=1000)


# ═══════════════════════════════════════════════════════════════════════════
# USERS & GROUPS
# ═══════════════════════════════════════════════════════════════════════════

class UserInfo(BaseModel):
    email: str | None = None
    name: str | None = None


class GroupMembers(BaseModel):
    group_name: str = Field(..., min_length=1, max_length=200)


# ═══════════════════════════════════════════════════════════════════════════
# VALIDATION DISPATCHER
# ═══════════════════════════════════════════════════════════════════════════

_VALIDATORS: dict[str, type[BaseModel]] = {
    "incident_create": IncidentCreate,
    "incident_list": IncidentList,
    "incident_get": IncidentGet,
    "incident_update": IncidentUpdate,
    "incident_stats": IncidentStats,
    "change_list": ChangeList,
    "change_create": ChangeCreate,
    "change_approve": ChangeApprove,
    "problem_create": ProblemCreate,
    "problem_list": ProblemList,
    "problem_link_incidents": ProblemLinkIncidents,
    "catalog_list": CatalogList,
    "request_create": RequestCreate,
    "request_status": RequestStatus,
    "request_approvals": RequestApprovals,
    "cmdb_search": CMDBSearch,
    "cmdb_relationships": CMDBRelationships,
    "cmdb_health": CMDBHealth,
    "kb_search": KBSearch,
    "report_performance": ReportPerformance,
    "workflow_list": WorkflowList,
    "integration_list": IntegrationList,
    "business_rule_list": BusinessRuleList,
    "user_info": UserInfo,
    "group_members": GroupMembers,
}


def validate_args(tool_name: str, args: dict) -> dict:
    """Validate and sanitize tool arguments. Returns sanitized dict or raises ValueError."""
    model = _VALIDATORS.get(tool_name)
    if not model:
        return args  # Unknown tools pass through
    validated = model(**args)
    return validated.model_dump(exclude_none=True, by_alias=False)
