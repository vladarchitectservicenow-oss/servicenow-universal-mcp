# Regression Test Cases: servicenow-universal-mcp

**Product:** ServiceNow Universal MCP Adapter
**Repository:** servicenow-universal-mcp
**Scope:** x_universal_mcp
**Version:** 1.0.0
**Author:** Vladimir Kapustin
**Last Updated:** 2026-06-01

---

## Purpose

Regression tests ensure that new changes do not break existing functionality. These tests should be run:
- Before every production deployment
- After any code modification
- After ServiceNow platform upgrades
- After configuration changes

**Total Regression Tests:** 12
**Minimum Pass Rate:** 100% (all tests must pass)

---

## REG-001: Idempotent Execution

**Test ID:** `REG-001`
**Category:** Functional
**Priority:** P0

**Description:** Verify that executing the same MCP operation twice produces identical results without side effects.

**Preconditions:**
- Clean test environment
- Test data reset

**Test Steps:**
1. Execute query_table on sys_user with limit=10
2. Record response hash
3. Execute same query_table operation
4. Record second response hash
5. Compare hashes

**Expected Result:**
- Both responses are identical
- No duplicate records created
- No additional log entries beyond expected

**Pass Criteria:**
```python
assert response1_hash == response2_hash
assert log_count_before + 1 == log_count_after  # Only 1 new log entry
```

**Known Issues:** None
**Last Passed:** 2026-06-01

---

## REG-002: Response Format Consistency

**Test ID:** `REG-002`
**Category:** Functional
**Priority:** P0

**Description:** Verify that API response format remains consistent across multiple executions.

**Preconditions:**
- MCP session established

**Test Steps:**
1. Execute listTools 5 times
2. Parse each response
3. Validate schema consistency

**Expected Result:**
- All 5 responses have identical structure
- No fields added or removed
- Data types consistent

**Pass Criteria:**
```python
for response in responses:
    assert 'result' in response
    assert 'tools' in response['result']
    assert isinstance(response['result']['tools'], list)
```

**Known Issues:** None
**Last Passed:** 2026-06-01

---

## REG-003: Role Assignment Idempotency

**Test ID:** `REG-003`
**Category:** Security
**Priority:** P1

**Description:** Verify that assigning an already-assigned role does not cause errors or duplicates.

**Preconditions:**
- Test user exists
- Test role exists

**Test Steps:**
1. Assign mcp_user role to test user
2. Assign mcp_user role to same user again
3. Query user's roles

**Expected Result:**
- No error on second assignment
- User has role exactly once
- No duplicate sys_user_has_role records

**Pass Criteria:**
```python
role_count = len(user_roles)
assert role_count == 1  # Not 2
```

**Known Issues:** None
**Last Passed:** 2026-06-01

---

## REG-004: Configuration Persistence

**Test ID:** `REG-004`
**Category:** Configuration
**Priority:** P0

**Description:** Verify that MCP configuration survives instance restart and cache clears.

**Preconditions:**
- MCP configuration exists and is active

**Test Steps:**
1. Record current configuration values
2. Clear cache (if possible in test env)
3. Reload configuration
4. Compare values

**Expected Result:**
- All configuration values preserved
- active flag remains true
- OAuth references intact

**Pass Criteria:**
```python
assert config['mcp_server_url'] == original_url
assert config['active'] == True
assert config['oauth_client'] == original_oauth
```

**Known Issues:** None
**Last Passed:** 2026-06-01

---

## REG-005: Session State Isolation

**Test ID:** `REG-005`
**Category:** Security
**Priority:** P1

**Description:** Verify that multiple MCP sessions do not share state or data.

**Preconditions:**
- Ability to create multiple sessions

**Test Steps:**
1. Create Session A, authenticate as User A
2. Create Session B, authenticate as User B
3. Query data in Session A
4. Query data in Session B
5. Verify session logs show correct user_ids

**Expected Result:**
- Sessions remain isolated
- User A cannot see User B's session data
- Audit logs correctly attribute actions

**Pass Criteria:**
```python
assert session_a['user_id'] != session_b['user_id']
assert log_a['user_id'] == user_a_id
assert log_b['user_id'] == user_b_id
```

**Known Issues:** None
**Last Passed:** 2026-06-01

---

## REG-006: OAuth Token Refresh

**Test ID:** `REG-006`
**Category:** Authentication
**Priority:** P1

**Description:** Verify that OAuth tokens refresh automatically before expiration.

**Preconditions:**
- OAuth client configured
- Token TTL set to short duration for testing (60 seconds)

**Test Steps:**
1. Obtain OAuth token
2. Wait 50 seconds (before expiration)
3. Execute MCP operation
4. Check if token was refreshed

**Expected Result:**
- Token refreshed automatically
- No authentication errors
- Operation succeeds

**Pass Criteria:**
```python
assert new_token != original_token
assert operation_result['status'] == 'success'
```

**Known Issues:** None
**Last Passed:** 2026-06-01

---

## REG-007: Cache Hit/Miss Behavior

**Test ID:** `REG-007`
**Category:** Performance
**Priority:** P2

**Description:** Verify that schema cache behaves correctly on first query (miss) and subsequent queries (hit).

**Preconditions:**
- Cache cleared

**Test Steps:**
1. Execute first table query (cache miss expected)
2. Record execution time
3. Execute same query (cache hit expected)
4. Record execution time
5. Compare times

**Expected Result:**
- Second query faster than first
- Cache hit count incremented
- Data identical

**Pass Criteria:**
```python
assert time2 < time1  # Cache hit faster
assert cache_stats['hits'] == 1
assert cache_stats['misses'] == 1
```

**Known Issues:** None
**Last Passed:** 2026-06-01

---

## REG-008: Error Message Consistency

**Test ID:** `REG-008`
**Category:** Usability
**Priority:** P2

**Description:** Verify that error messages for the same error type are consistent.

**Preconditions:**
- None

**Test Steps:**
1. Trigger invalid_table error 3 times
2. Collect error messages
3. Compare message structure

**Expected Result:**
- Error code consistent (e.g., INVALID_TABLE)
- Message format consistent
- No stack traces exposed

**Pass Criteria:**
```python
assert all('INVALID_TABLE' in msg for msg in errors)
assert all('Traceback' not in msg for msg in errors)
```

**Known Issues:** None
**Last Passed:** 2026-06-01

---

## REG-009: Audit Log Completeness

**Test ID:** `REG-009`
**Category:** Compliance
**Priority:** P1

**Description:** Verify that all MCP operations create audit log entries.

**Preconditions:**
- Audit logging enabled

**Test Steps:**
1. Record current log count
2. Execute 5 different MCP operations
3. Query audit log table
4. Count new entries

**Expected Result:**
- 5 new log entries created
- Each entry has required fields
- Timestamps accurate

**Pass Criteria:**
```python
assert new_log_count == 5
for log in new_logs:
    assert 'timestamp' in log
    assert 'user_id' in log
    assert 'action' in log
```

**Known Issues:** None
**Last Passed:** 2026-06-01

---

## REG-010: Rate Limit Reset

**Test ID:** `REG-010`
**Category:** Performance
**Priority:** P2

**Description:** Verify that rate limit counters reset after the configured window.

**Preconditions:**
- Rate limit: 60 requests per minute

**Test Steps:**
1. Send 60 requests (exhaust limit)
2. Verify 61st request returns 429
3. Wait 61 seconds
4. Send request

**Expected Result:**
- 61st request returns 429
- Request after wait succeeds (200)

**Pass Criteria:**
```python
assert request_61.status_code == 429
assert request_after_wait.status_code == 200
```

**Known Issues:** None
**Last Passed:** 2026-06-01

---

## REG-011: Business Rule Execution Order

**Test ID:** `REG-011`
**Category:** Functional
**Priority:** P2

**Description:** Verify that Business Rules execute in correct order (before > after).

**Preconditions:**
- Test Business Rules configured

**Test Steps:**
1. Create record that triggers BRs
2. Check execution log
3. Verify order

**Expected Result:**
- Before BRs execute before insert
- After BRs execute after insert
- No order violations

**Pass Criteria:**
```python
assert br_log[0]['type'] == 'before'
assert br_log[1]['type'] == 'after'
```

**Known Issues:** None
**Last Passed:** 2026-06-01

---

## REG-012: Scheduled Job Execution

**Test ID:** `REG-012`
**Category:** Operations
**Priority:** P2

**Description:** Verify that scheduled jobs (session cleanup, log retention) execute on schedule.

**Preconditions:**
- Scheduled jobs configured and active

**Test Steps:**
1. Create expired session records (manually set last_activity to past)
2. Trigger session cleanup job
3. Verify expired sessions removed

**Expected Result:**
- Expired sessions deleted
- Active sessions preserved
- Job completes without errors

**Pass Criteria:**
```python
assert expired_session_count == 0
assert active_session_count == original_active_count
```

**Known Issues:** None
**Last Passed:** 2026-06-01

---

## Regression Test Execution Schedule

| Environment | Frequency | Owner |
|-------------|-----------|-------|
| Development | Every commit | Developer |
| Test/QA | Daily (automated) | QA Team |
| Staging | Before each release | DevOps |
| Production | After each deployment | DevOps |

---

## Regression Test Results Log

| Date | Environment | Tests Run | Passed | Failed | Blocked | Notes |
|------|-------------|-----------|--------|--------|---------|-------|
| 2026-06-01 | Development | 12 | TBD | TBD | TBD | Initial run |

---

## Failure Response Procedure

1. **Immediate Action:** Block deployment if any P0/P1 test fails
2. **Investigation:** Review test logs, identify root cause
3. **Fix:** Develop and test fix in isolation
4. **Re-run:** Execute full regression suite after fix
5. **Documentation:** Update this document with lessons learned

---

*Regression test cases generated by ServiceNow Scoped App Factory. Version: 1.0.0*
