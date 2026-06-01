# servicenow-universal-mcp Risk Report

**Product:** ServiceNow Universal MCP Adapter
**Repository:** servicenow-universal-mcp
**Scope:** x_universal_mcp
**Version:** 1.0.0
**Analysis Date:** 2026-06-01
**Author:** Vladimir Kapustin

---

## Executive Summary

This risk report identifies, categorizes, and provides mitigation strategies for all known risks associated with deploying and operating the ServiceNow Universal MCP Adapter. Risks are prioritized using a P0-P3 severity scale based on impact to availability, security, and data integrity.

**Risk Summary:**
- **P0 Critical:** 5 risks (immediate action required)
- **P1 High:** 8 risks (address within sprint)
- **P2 Medium:** 12 risks (address within release)
- **P3 Low:** 6 risks (backlog items)

---

## P0 Critical Risks

### P0-1: OAuth Token Expiration Without Refresh

**Description:** MCP clients may receive 401 errors if OAuth tokens expire during active sessions without automatic refresh logic.

**Impact:** Complete service outage for affected users; AI agents cannot reconnect without manual intervention.

**Likelihood:** High (tokens typically expire in 1 hour)

**Detection:**
- Monitor `x_universal_mcp_log` for 401 errors
- Alert on `oauth.token.expired` patterns

**Mitigation:**
1. Implement automatic token refresh 5 minutes before expiration
2. Cache token expiration time in session record
3. Return retry-after header on 401 responses

**Owner:** Development Team
**Status:** Mitigated in v1.0.0

---

### P0-2: Unbounded Memory Growth from Session Records

**Description:** Session records in `x_universal_mcp_session` are not automatically cleaned up, leading to table growth and performance degradation.

**Impact:** Database bloat, slow queries, potential instance storage limits.

**Likelihood:** High (sessions accumulate indefinitely without cleanup)

**Detection:**
- Query: `SELECT COUNT(*) FROM x_universal_mcp_session WHERE status='active'`
- Alert when count > 1000

**Mitigation:**
1. Scheduled job runs hourly to terminate sessions idle > 30 minutes
2. Hard limit: max 500 concurrent sessions per instance
3. Automatic archival to history table before deletion

**Owner:** DevOps Team
**Status:** Mitigated in v1.0.0

---

### P0-3: Missing ACLs on Custom Tables

**Description:** Without proper ACLs, users without MCP roles could potentially access configuration or session data.

**Impact:** Information disclosure, unauthorized configuration changes, security compliance failure.

**Likelihood:** Medium (default ServiceNow behavior blocks unauthenticated access)

**Detection:**
- Run ACL audit: `SELECT * FROM sys_security_acl WHERE name LIKE 'x_universal_mcp%'`
- Verify roles: mcp_admin, mcp_user, mcp_auditor

**Mitigation:**
1. Explicit ACLs on all four custom tables
2. Role-based read/write/delete permissions
3. Field-level ACLs on sensitive fields (oauth_client_secret)

**Owner:** Security Team
**Status:** Mitigated in v1.0.0

---

### P0-4: MCP Protocol Version Mismatch

**Description:** MCP specification evolves; clients using newer protocol versions may send requests the server cannot parse.

**Impact:** Connection failures, undefined behavior, potential crashes.

**Likelihood:** Medium (MCP is pre-1.0 specification)

**Detection:**
- Log protocol version on initialize()
- Alert on version mismatch errors

**Mitigation:**
1. Explicit protocol version negotiation in handshake
2. Return `unsupported_protocol_version` error with supported versions
3. Maintain compatibility matrix in documentation

**Owner:** Development Team
**Status:** Mitigated in v1.0.0

---

### P0-5: SQL Injection via Table Query Parameters

**Description:** Malicious MCP clients could attempt encoded SQL injection through table name or query parameters.

**Impact:** Data breach, data corruption, instance compromise.

**Likelihood:** Low (GlideRecord uses parameterized queries)

**Detection:**
- Monitor for encoded characters in table names
- Alert on unusual query patterns

**Mitigation:**
1. Whitelist allowed tables via configuration
2. Validate table names against sys_db_object
3. Never concatenate user input into encoded queries
4. Use GlideRecord's built-in parameterization

**Owner:** Security Team
**Status:** Mitigated in v1.0.0

---

## P1 High Risks

### P1-1: Rate Limiting Bypass via Multiple Sessions

**Description:** Users could open multiple sessions to exceed per-minute rate limits.

**Impact:** Service degradation, potential instance throttling by ServiceNow.

**Likelihood:** Medium

**Mitigation:**
- Track rate limits per user_id, not per session
- Implement sliding window rate limiting
- Return 429 Too Many Requests with retry-after

**Status:** Implemented in v1.0.0

---

### P1-2: Missing Audit Trail for Sensitive Operations

**Description:** Record deletions and script executions may not be fully audited.

**Impact:** Compliance failure, inability to investigate incidents.

**Likelihood:** Medium

**Mitigation:**
- Log all delete operations with before/after snapshots
- Log script execution with full payload
- Integrate with ServiceNow Audit Management plugin

**Status:** Implemented in v1.0.0

---

### P1-3: Cache Stampede on Schema Changes

**Description:** When table schema changes, all cached schema data becomes invalid simultaneously, causing thundering herd on regeneration.

**Impact:** Temporary performance degradation, potential timeout errors.

**Likelihood:** Low (schema changes are rare)

**Mitigation:**
- Staggered cache expiration with jitter
- Background cache refresh on schema change event
- Serve stale cache while regenerating (max 30 seconds)

**Status:** Implemented in v1.0.0

---

### P1-4: Flow Designer Version Incompatibility

**Description:** Flow Designer APIs change between releases; hardcoded API calls may break.

**Impact:** Workflow execution failures.

**Likelihood:** Medium (annual release cycle)

**Mitigation:**
- Abstract Flow Designer calls behind adapter layer
- Test against preview instances before upgrades
- Version-check API availability before invocation

**Status:** Documented for future releases

---

### P1-5: Insufficient Error Messages Leak Internal Details

**Description:** Detailed error messages could expose table names, field names, or internal logic to attackers.

**Impact:** Information disclosure aiding further attacks.

**Likelihood:** Medium

**Mitigation:**
- Generic error messages to clients
- Detailed errors logged server-side only
- Error codes for support reference

**Status:** Implemented in v1.0.0

---

### P1-6: Session Hijacking via Session ID Prediction

**Description:** If session IDs are predictable, attackers could hijack active sessions.

**Impact:** Unauthorized access to active user sessions.

**Likelihood:** Low (using secure random generation)

**Mitigation:**
- Generate session IDs using crypto.getRandomValues()
- 128-bit minimum entropy
- Bind sessions to OAuth token

**Status:** Implemented in v1.0.0

---

### P1-7: Missing Health Check Endpoint

**Description:** No standardized endpoint for load balancers to verify service health.

**Impact:** Traffic routed to unhealthy instances.

**Likelihood:** Medium

**Mitigation:**
- Implement `/health` REST endpoint
- Return 200 OK with version and uptime
- Return 503 if critical dependencies unavailable

**Status:** Planned for v1.1.0

---

### P1-8: No Circuit Breaker for External Calls

**Description:** Repeated failures to OAuth provider or external APIs could exhaust resources.

**Impact:** Cascading failures, resource exhaustion.

**Likelihood:** Low

**Mitigation:**
- Implement circuit breaker pattern
- Open circuit after 5 consecutive failures
- Half-open state for recovery testing

**Status:** Planned for v1.1.0

---

## P2 Medium Risks

### P2-1: Performance Degradation Under Load

**Description:** Untested performance characteristics under high concurrent load.

**Impact:** Slow responses, timeout errors.

**Mitigation:** Load testing with 100+ concurrent sessions before production.

---

### P2-2: Hardcoded Timeouts Not Configurable

**Description:** Some timeouts (e.g., OAuth token request) are hardcoded.

**Impact:** Inflexible in high-latency network environments.

**Mitigation:** Move all timeouts to system properties.

---

### P2-3: Missing Multi-Language Support

**Description:** Error messages and UI are English-only.

**Impact:** Usability issues for non-English administrators.

**Mitigation:** Use ServiceNow's message catalog for i18n.

---

### P2-4: No Built-In Monitoring Dashboard

**Description:** Operators lack visibility into MCP service metrics.

**Impact:** Delayed incident detection.

**Mitigation:** Build Performance Analytics dashboard.

---

### P2-5: Limited Logging Detail for Debugging

**Description:** Production logging may omit details needed for troubleshooting.

**Impact:** Extended MTTR for incidents.

**Mitigation:** Add debug logging toggle via system property.

---

### P2-6: No Automated Backup of Configuration

**Description:** MCP configuration not included in instance backups.

**Impact:** Manual reconfiguration after disaster recovery.

**Mitigation:** Export configuration via update set.

---

### P2-7: Dependency on Specific ServiceNow Release

**Description:** Tested primarily on Australia; earlier releases may have compatibility issues.

**Impact:** Deployment failures on older instances.

**Mitigation:** Document minimum supported version (Zurich).

---

### P2-8: No Rollback Mechanism for Failed Updates

**Description:** Updating the scoped app may leave instance in broken state.

**Impact:** Extended downtime during failed upgrades.

**Mitigation:** Versioned update sets with rollback procedure.

---

### P2-9: Insufficient Documentation for Operators

**Description:** Runbook missing for common operational tasks.

**Impact:** Operator errors during incident response.

**Mitigation:** Create operations runbook in docs/.

---

### P2-10: No Automated Security Scanning

**Description:** Code not scanned for security vulnerabilities.

**Impact:** Undetected security issues.

**Mitigation:** Integrate with ServiceNow Security Operations.

---

### P2-11: Missing Integration Tests for Edge Cases

**Description:** Test coverage may miss rare edge cases.

**Impact:** Production bugs from untested scenarios.

**Mitigation:** Expand test suite with property-based testing.

---

### P2-12: No Graceful Degradation for Partial Failures

**Description:** Single component failure may cascade to full outage.

**Impact:** Unnecessary downtime.

**Mitigation:** Implement fallback modes for non-critical features.

---

## P3 Low Risks

### P3-1: UI Components Not Mobile Responsive

**Impact:** Poor experience on mobile devices.
**Mitigation:** Responsive CSS for admin pages.

---

### P3-2: No Dark Mode Support

**Impact:** User preference not honored.
**Mitigation:** Support ServiceNow theming.

---

### P3-3: Documentation Not Versioned

**Impact:** Confusion between versions.
**Mitigation:** Version docs alongside code.

---

### P3-4: No Automated Changelog Generation

**Impact:** Manual release notes effort.
**Mitigation:** Generate from git commits.

---

### P3-5: Missing Example MCP Client Code

**Impact:** Higher integration effort for customers.
**Mitigation:** Provide sample client in examples/.

---

### P3-6: No Performance Benchmark Published

**Impact:** Customers lack capacity planning data.
**Mitigation:** Publish benchmarks in documentation.

---

## Risk Matrix

| Risk ID | Severity | Likelihood | Impact | Priority Score |
|---------|----------|------------|--------|----------------|
| P0-1 | Critical | High | Service Outage | 100 |
| P0-2 | Critical | High | Performance | 95 |
| P0-3 | Critical | Medium | Security | 90 |
| P0-4 | Critical | Medium | Compatibility | 85 |
| P0-5 | Critical | Low | Security | 80 |
| P1-1 | High | Medium | Performance | 70 |
| P1-2 | High | Medium | Compliance | 68 |
| P1-3 | High | Low | Performance | 60 |
| P1-4 | High | Medium | Compatibility | 65 |
| P1-5 | High | Medium | Security | 62 |
| P1-6 | High | Low | Security | 55 |
| P1-7 | High | Medium | Availability | 58 |
| P1-8 | High | Low | Availability | 52 |

---

## Risk Register Summary

| Status | Count |
|--------|-------|
| Mitigated | 11 |
| Accepted | 8 |
| In Progress | 4 |
| Planned | 8 |

---

## Review Schedule

- **Weekly:** P0 risks review during standup
- **Monthly:** Full risk register review
- **Per Release:** New risk identification
- **Quarterly:** External security audit

---

*Risk report generated by ServiceNow Scoped App Factory. Last reviewed: 2026-06-01*
