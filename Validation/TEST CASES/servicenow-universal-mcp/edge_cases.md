# Edge Cases Test Suite: servicenow-universal-mcp

**Product:** ServiceNow Universal MCP Adapter
**Repository:** servicenow-universal-mcp
**Scope:** x_universal_mcp
**Version:** 1.0.0
**Author:** Vladimir Kapustin
**Last Updated:** 2026-06-01

---

## Purpose

Edge case tests validate system behavior under unusual, extreme, or unexpected conditions. These tests ensure robustness and graceful degradation when inputs deviate from normal operating parameters.

**Total Edge Case Tests:** 18
**Minimum Pass Rate:** 85% (15/18)

---

## EC-001: Empty Table Query

**Test ID:** `EC-001`
**Category:** Data Handling
**Priority:** P2

**Description:** Verify behavior when querying a table with zero matching records.

**Test Steps:**
1. Query table with filter that matches no records
2. Example: `sys_user` where `user_nameSTARTSWITHxyz123notexist`

**Expected Result:**
- Empty array returned
- No error thrown
- Response includes count: 0

**Pass Criteria:**
```json
{
  "result": {
    "records": [],
    "count": 0
  }
}
```

---

## EC-002: Maximum Batch Size (50k Records)

**Test ID:** `EC-002`
**Category:** Performance
**Priority:** P2

**Description:** Verify behavior when query returns more than 50,000 records.

**Test Steps:**
1. Query large table (e.g., `sys_audit`) without limit
2. Or query with limit=100000

**Expected Result:**
- Response truncated to max batch size
- Warning or pagination info returned
- No timeout or crash

**Pass Criteria:**
- Response includes `truncated: true` or `has_more: true`
- Execution completes within 30 seconds

---

## EC-003: Null Configuration Values

**Test ID:** `EC-003`
**Category:** Configuration
**Priority:** P1

**Description:** Verify behavior when required configuration properties are null or missing.

**Test Steps:**
1. Set `x_universal_mcp_config.rate_limit_per_minute` to null
2. Attempt MCP operation
3. Set `oauth_client_id` to empty string
4. Attempt authentication

**Expected Result:**
- Default values used when available
- Clear error when defaults not available
- No null pointer exceptions

**Pass Criteria:**
```python
assert 'NullPointerException' not in error
assert error_message is descriptive
```

---

## EC-004: Missing Plugin Dependency

**Test ID:** `EC-004`
**Category:** Dependencies
**Priority:** P1

**Description:** Verify behavior when required plugin is not activated.

**Test Steps:**
1. Deactivate System Web Services plugin (test environment only)
2. Attempt MCP operation

**Expected Result:**
- Clear error indicating missing dependency
- Plugin name provided in error message
- Graceful degradation (no crash)

**Pass Criteria:**
```python
assert 'System Web Services' in error_message
assert 'plugin' in error_message.lower()
```

---

## EC-005: Request Timeout

**Test ID:** `EC-005`
**Category:** Performance
**Priority:** P2

**Description:** Verify behavior when operation exceeds timeout threshold.

**Test Steps:**
1. Execute query with artificial delay (or query very large table)
2. Wait for timeout

**Expected Result:**
- Timeout error after configured threshold
- Resources released properly
- Session not left in hung state

**Pass Criteria:**
- Timeout occurs within 10% of configured limit
- Session can be reused after timeout

---

## EC-006: Unicode and Special Characters

**Test ID:** `EC-006`
**Category:** Data Handling
**Priority:** P2

**Description:** Verify handling of unicode, emojis, and special characters in field names and values.

**Test Steps:**
1. Query with filter: `user_nameLIKEéàü中文`
2. Create record with emoji in description
3. Query with special regex characters in filter

**Expected Result:**
- Unicode handled correctly
- No encoding errors
- Special characters properly escaped

**Pass Criteria:**
- Records with unicode returned correctly
- No `UnicodeDecodeError` or similar

---

## EC-007: Concurrent Scan Race Conditions

**Test ID:** `EC-007`
**Category:** Concurrency
**Priority:** P2

**Description:** Verify behavior when multiple scans execute simultaneously on same data.

**Test Steps:**
1. Launch 10 concurrent queries against same table
2. All queries modify a counter field
3. Verify final count

**Expected Result:**
- No race conditions
- Final count matches expected
- No deadlocks

**Pass Criteria:**
```python
assert final_count == expected_count
assert no_deadlock_detected
```

---

## EC-008: Malformed JSON Payload

**Test ID:** `EC-008`
**Category:** Security
**Priority:** P1

**Description:** Verify behavior when receiving malformed JSON in request body.

**Test Steps:**
1. Send POST with invalid JSON: `{"key": value}` (missing quotes)
2. Send POST with truncated JSON
3. Send POST with invalid escape sequences

**Expected Result:**
- HTTP 400 Bad Request
- Error indicates JSON parsing failure
- No stack trace exposed

**Pass Criteria:**
```python
assert response.status_code == 400
assert 'JSON' in error_message or 'parse' in error_message.lower()
```

---

## EC-009: SQL Injection Attempt

**Test ID:** `EC-009`
**Category:** Security
**Priority:** P0

**Description:** Verify protection against SQL injection attempts.

**Test Steps:**
1. Send table_name: `sys_user; DROP TABLE sys_user;--`
2. Send filter with: `user_name=test' OR '1'='1`
3. Send encoded injection: `user_name=test%27%20OR%20%271%27%3D%271`

**Expected Result:**
- All attempts blocked
- Input treated as literal string
- No SQL execution

**Pass Criteria:**
- Query returns 0 results (not all users)
- No database errors
- Attempt logged as security event

---

## EC-010: XSS Payload in Input

**Test ID:** `EC-010`
**Category:** Security
**Priority:** P1

**Description:** Verify protection against XSS attacks via input fields.

**Test Steps:**
1. Send record creation with: `<script>alert('xss')</script>`
2. Send with encoded XSS: `%3Cscript%3Ealert('xss')%3C/script%3E`

**Expected Result:**
- Input sanitized or escaped
- Script not executed in any UI
- Stored as literal text

**Pass Criteria:**
- No script execution in UI
- Stored value shows escaped HTML

---

## EC-011: Extremely Long Input Strings

**Test ID:** `EC-011`
**Category:** Data Handling
**Priority:** P2

**Description:** Verify behavior with extremely long input strings.

**Test Steps:**
1. Send query filter with 10,000 character string
2. Send record creation with max-length description

**Expected Result:**
- Input truncated to field limit
- Or rejected with clear error
- No buffer overflow

**Pass Criteria:**
- System remains stable
- Error message if rejected

---

## EC-012: Invalid OAuth Token Format

**Test ID:** `EC-012`
**Category:** Security
**Priority:** P1

**Description:** Verify behavior with malformed OAuth tokens.

**Test Steps:**
1. Send request with token: `invalid_token`
2. Send request with token: `Bearer ` (empty)
3. Send request with expired token format

**Expected Result:**
- HTTP 401 Unauthorized
- Token rejected without processing
- No information disclosure

**Pass Criteria:**
```python
assert response.status_code == 401
assert 'token' in error_message.lower()
```

---

## EC-013: Zero Rate Limit Configuration

**Test ID:** `EC-013`
**Category:** Configuration
**Priority:** P2

**Description:** Verify behavior when rate limit is configured to 0.

**Test Steps:**
1. Set `rate_limit_per_minute` to 0
2. Attempt any MCP operation

**Expected Result:**
- Either: All requests blocked with clear error
- Or: Default rate limit applied
- No division by zero errors

**Pass Criteria:**
- No crash or exception
- Behavior is documented and consistent

---

## EC-014: Session ID Manipulation

**Test ID:** `EC-014`
**Category:** Security
**Priority:** P1

**Description:** Verify behavior with manipulated or forged session IDs.

**Test Steps:**
1. Capture valid session ID
2. Modify one character
3. Use modified ID in request

**Expected Result:**
- Session not found error
- No session hijacking possible
- Attempt logged

**Pass Criteria:**
```python
assert 'session_not_found' in error_code
assert no_unauthorized_access
```

---

## EC-015: Memory Exhaustion Attack

**Test ID:** `EC-015`
**Category:** Security
**Priority:** P2

**Description:** Verify behavior under memory exhaustion conditions.

**Test Steps:**
1. Send requests with extremely large payloads
2. Send many concurrent large requests
3. Monitor memory usage

**Expected Result:**
- Requests rejected when memory threshold reached
- System remains stable
- No OOM crash

**Pass Criteria:**
- Memory stays within bounds
- Graceful rejection of oversized requests

---

## EC-016: Timezone Edge Cases

**Test ID:** `EC-016`
**Category:** Data Handling
**Priority:** P3

**Description:** Verify behavior with unusual timezone configurations.

**Test Steps:**
1. Set instance timezone to UTC+14 (maximum)
2. Set to UTC-12 (minimum)
3. Query with date filters across DST boundaries

**Expected Result:**
- Dates handled correctly
- No off-by-one-day errors
- DST transitions handled

**Pass Criteria:**
- Query results match expected dates
- No timezone conversion errors

---

## EC-017: Database Connection Loss

**Test ID:** `EC-017`
**Category:** Resilience
**Priority:** P2

**Description:** Verify behavior when database connection is lost mid-operation.

**Test Steps:**
1. Start long-running query
2. Simulate database disconnect (test environment)
3. Observe error handling

**Expected Result:**
- Connection error returned
- Session cleaned up
- Reconnection possible

**Pass Criteria:**
- Clear error message
- No hung sessions
- Recovery possible

---

## EC-018: Invalid MCP Protocol Version

**Test ID:** `EC-018`
**Category:** Protocol
**Priority:** P2

**Description:** Verify behavior with unsupported MCP protocol versions.

**Test Steps:**
1. Send initialize with `protocolVersion: "999.99.99"`
2. Send initialize with `protocolVersion: "invalid"`

**Expected Result:**
- Error indicating unsupported version
- List of supported versions returned
- Connection not established

**Pass Criteria:**
```json
{
  "error": {
    "code": "unsupported_protocol_version",
    "message": "...",
    "supported_versions": ["2024-11-05"]
  }
}
```

---

## Edge Case Test Results Log

| Date | Tests Run | Passed | Failed | Blocked | Notes |
|------|-----------|--------|--------|---------|-------|
| 2026-06-01 | 18 | TBD | TBD | TBD | Initial run |

---

## Risk Mitigation Summary

| Edge Case | Production Risk | Mitigation |
|-----------|-----------------|------------|
| Empty tables | Low | Handled gracefully |
| Large datasets | Medium | Pagination implemented |
| Null configs | Medium | Defaults + validation |
| Missing plugins | Low | Dependency checks |
| Timeouts | Medium | Configurable limits |
| Unicode | Low | UTF-8 throughout |
| Concurrency | Medium | Transaction isolation |
| Injection attacks | High | Parameterized queries |

---

*Edge cases test suite generated by ServiceNow Scoped App Factory. Version: 1.0.0*
