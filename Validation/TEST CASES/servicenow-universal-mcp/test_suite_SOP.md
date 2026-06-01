# Test Suite SOP: servicenow-universal-mcp

**Product:** ServiceNow Universal MCP Adapter
**Repository:** servicenow-universal-mcp
**Scope:** x_universal_mcp
**Version:** 1.0.0
**Author:** Vladimir Kapustin
**License:** AGPL-3.0-only
**Last Updated:** 2026-06-01

---

## Purpose

This Standard Operating Procedure (SOP) defines the complete test suite for validating the ServiceNow Universal MCP Adapter. All tests must pass before deployment to production.

**Minimum Pass Criteria:** 12/12 scenarios PASS
**Recommended Pass Criteria:** 15/15 scenarios PASS (including edge cases)

---

## Test Environment Requirements

| Requirement | Specification | Verification |
|-------------|---------------|--------------|
| ServiceNow Instance | Australia release or later | Instance info page |
| Node.js | 18+ | `node --version` |
| Python | 3.10+ | `python3 --version` |
| pytest | 7.0+ | `pytest --version` |
| Git | 2.30+ | `git --version` |
| OAuth Plugin | Activated | System OAuth menu visible |
| REST Plugin | Activated | REST Explorer accessible |

---

## Test Scenarios (15 Total)

### P0 Critical Scenarios (Core Functionality)

#### Test 1: OAuth Token Acquisition

**ID:** `test_oauth_token_acquisition`
**Priority:** P0
**Purpose:** Verify OAuth 2.0 token can be obtained from configured provider

**Preconditions:**
- OAuth client configured in `sys_oauth_client`
- Valid client_id and client_secret

**Steps:**
1. Send POST request to OAuth token endpoint
2. Include client_id and client_secret in request body
3. Include grant_type=client_credentials

**Expected Result:**
- HTTP 200 response
- JSON body contains `access_token`
- Token has `expires_in` field

**Pass Criteria:**
```json
{
  "access_token": "<non-empty string>",
  "token_type": "Bearer",
  "expires_in": 3600
}
```

**Failure Actions:**
- Verify OAuth client is active
- Check client credentials
- Review OAuth plugin logs

---

#### Test 2: MCP Protocol Handshake

**ID:** `test_mcp_handshake`
**Priority:** P0
**Purpose:** Verify MCP initialize() completes successfully

**Preconditions:**
- Valid OAuth token obtained
- MCP server endpoint accessible

**Steps:**
1. Send MCP initialize request with protocol version
2. Include client capabilities
3. Wait for server response

**Expected Result:**
- HTTP 200 response
- Server returns capabilities object
- Protocol version negotiated

**Pass Criteria:**
```json
{
  "jsonrpc": "2.0",
  "result": {
    "protocolVersion": "2024-11-05",
    "capabilities": {
      "tools": {},
      "resources": {},
      "prompts": {}
    }
  }
}
```

**Failure Actions:**
- Verify MCP handler Script Include is active
- Check protocol version compatibility
- Review server logs for errors

---

#### Test 3: Tool Discovery

**ID:** `test_list_tools`
**Priority:** P0
**Purpose:** Verify MCP listTools() returns available operations

**Preconditions:**
- MCP handshake completed
- Script Includes loaded

**Steps:**
1. Send MCP tools/list request
2. Parse response

**Expected Result:**
- List of available tools returned
- Each tool has name, description, inputSchema

**Pass Criteria:**
- At least 5 tools listed
- Tools include: query_table, create_record, update_record, delete_record, execute_flow

**Failure Actions:**
- Verify Script Includes are loaded
- Check tool registration in UniversalMCPHandler
- Review tool definition JSON

---

#### Test 4: Table Query Execution

**ID:** `test_table_query`
**Priority:** P0
**Purpose:** Verify MCP callTool(query_table) returns data

**Preconditions:**
- MCP session established
- sys_user table has records

**Steps:**
1. Send callTool request with query_table
2. Specify table: sys_user
3. Specify limit: 10

**Expected Result:**
- Records returned from sys_user
- Each record has sys_id, user_name, email

**Pass Criteria:**
- At least 1 record returned
- Response format matches MCP specification

**Failure Actions:**
- Verify ACLs allow read access
- Check table name is valid
- Review GlideRecord query logic

---

### P1 High Priority Scenarios (Robustness)

#### Test 5: Record Creation

**ID:** `test_record_create`
**Priority:** P1
**Purpose:** Verify create_record tool creates new records

**Preconditions:**
- Valid MCP session
- Target table allows creation

**Steps:**
1. Send callTool with create_record
2. Specify table: x_universal_mcp_log (test table)
3. Provide field values

**Expected Result:**
- Record created successfully
- sys_id returned in response

**Pass Criteria:**
- HTTP 200 response
- New record exists in database
- Field values match input

**Failure Actions:**
- Verify write ACLs configured
- Check mandatory fields provided
- Review Business Rules blocking creation

---

#### Test 6: Record Update

**ID:** `test_record_update`
**Priority:** P1
**Purpose:** Verify update_record tool modifies existing records

**Preconditions:**
- Test record exists

**Steps:**
1. Send callTool with update_record
2. Specify sys_id of test record
3. Provide new field values

**Expected Result:**
- Record updated successfully
- Updated values persisted

**Pass Criteria:**
- HTTP 200 response
- Record reflects new values
- sys_updated_on timestamp changed

**Failure Actions:**
- Verify record exists
- Check update ACLs
- Review Business Rules

---

#### Test 7: Record Deletion

**ID:** `test_record_delete`
**Priority:** P1
**Purpose:** Verify delete_record tool removes records

**Preconditions:**
- Test record exists (created for this test)

**Steps:**
1. Send callTool with delete_record
2. Specify sys_id of test record

**Expected Result:**
- Record deleted or marked inactive
- Confirmation in response

**Pass Criteria:**
- HTTP 200 response
- Record no longer queryable (or active=false)

**Failure Actions:**
- Verify delete ACLs
- Check if soft-delete is configured
- Review cascade rules

---

#### Test 8: Empty Data Handling

**ID:** `test_empty_table_query`
**Priority:** P1
**Purpose:** Verify graceful handling of empty tables

**Preconditions:**
- Query targets table with no matching records

**Steps:**
1. Send callTool with query_table
2. Use filter that matches no records

**Expected Result:**
- Empty array returned
- No error thrown

**Pass Criteria:**
```json
{
  "result": {
    "records": [],
    "count": 0
  }
}
```

**Failure Actions:**
- Verify query logic handles zero results
- Check response formatting
- Review error handling

---

### P2 Medium Priority Scenarios (Edge Cases)

#### Test 9: Invalid Table Query

**ID:** `test_invalid_table`
**Priority:** P2
**Purpose:** Verify error handling for non-existent tables

**Preconditions:**
- None

**Steps:**
1. Send callTool with query_table
2. Specify non-existent table name

**Expected Result:**
- Error response returned
- Error code indicates invalid table

**Pass Criteria:**
- HTTP 400 or 404 response
- Error message is descriptive (not stack trace)

**Failure Actions:**
- Verify table validation logic
- Check error response formatting
- Review security (no info disclosure)

---

#### Test 10: Authentication Failure

**ID:** `test_auth_failure`
**Priority:** P2
**Purpose:** Verify unauthorized requests are rejected

**Preconditions:**
- Invalid or expired OAuth token

**Steps:**
1. Send MCP request with invalid token
2. Observe response

**Expected Result:**
- HTTP 401 Unauthorized
- Error indicates authentication failure

**Pass Criteria:**
- Request rejected
- No data returned
- Audit log entry created

**Failure Actions:**
- Verify OAuth validator is active
- Check token validation logic
- Review ACL bypass possibilities

---

#### Test 11: Rate Limiting

**ID:** `test_rate_limiting`
**Priority:** P2
**Purpose:** Verify rate limiting prevents abuse

**Preconditions:**
- Rate limit configured (60 req/min default)

**Steps:**
1. Send 70 requests within 1 minute
2. Observe responses

**Expected Result:**
- First 60 requests succeed
- Requests 61-70 return 429 Too Many Requests

**Pass Criteria:**
- Rate limit enforced
- retry-after header included

**Failure Actions:**
- Verify rate limiter configuration
- Check counter reset logic
- Review sliding window implementation

---

#### Test 12: Session Timeout

**ID:** `test_session_timeout`
**Priority:** P2
**Purpose:** Verify sessions timeout after inactivity

**Preconditions:**
- Session timeout configured (1800 seconds)

**Steps:**
1. Create MCP session
2. Wait for timeout period (or simulate)
3. Attempt to use session

**Expected Result:**
- Session marked as expired
- New handshake required

**Pass Criteria:**
- Expired session rejected
- Session record updated

**Failure Actions:**
- Verify session manager logic
- Check timeout calculation
- Review cleanup job

---

#### Test 13: Large Payload Handling

**ID:** `test_large_payload`
**Priority:** P2
**Purpose:** Verify handling of large query results

**Preconditions:**
- Table with 1000+ records available

**Steps:**
1. Query table with large result set
2. Request all records

**Expected Result:**
- Records returned with pagination
- Or truncated with warning

**Pass Criteria:**
- No timeout or crash
- Response under size limit

**Failure Actions:**
- Verify pagination logic
- Check memory limits
- Review streaming options

---

#### Test 14: Concurrent Sessions

**ID:** `test_concurrent_sessions`
**Priority:** P2
**Purpose:** Verify multiple sessions work simultaneously

**Preconditions:**
- Test framework supports parallel execution

**Steps:**
1. Open 10 concurrent MCP sessions
2. Execute queries on each
3. Verify all complete

**Expected Result:**
- All sessions function independently
- No data corruption

**Pass Criteria:**
- 10/10 sessions successful
- No race conditions

**Failure Actions:**
- Verify session isolation
- Check database locking
- Review connection pooling

---

#### Test 15: Cache Invalidation

**ID:** `test_cache_invalidation`
**Priority:** P2
**Purpose:** Verify cache updates on schema changes

**Preconditions:**
- Schema cache populated

**Steps:**
1. Modify table schema (add field)
2. Query cached table
3. Verify cache refreshed

**Expected Result:**
- Cache invalidated on change
- New schema reflected

**Pass Criteria:**
- Cache hit after refresh
- No stale data returned

**Failure Actions:**
- Verify cache invalidation trigger
- Check TTL configuration
- Review Business Rules

---

## Test Execution Procedure

### Step 1: Environment Setup

```bash
# Clone repository
cd ~/servicenow-universal-mcp

# Install dependencies
pip install -r requirements.txt

# Verify environment
pytest --collect-only
```

### Step 2: Run Full Test Suite

```bash
# Run all tests with verbose output
pytest tests/ -v --tb=short

# Run with coverage
pytest tests/ -v --cov=src --cov-report=html
```

### Step 3: Review Results

```bash
# Check for failures
pytest tests/ -v | grep FAILED

# Review coverage report
open htmlcov/index.html
```

### Step 4: Document Results

| Execution Date | Tester | Pass Rate | Notes |
|----------------|--------|-----------|-------|
| 2026-06-01 | Automated | TBD | Initial run |

---

## Pass/Fail Criteria Summary

| Priority | Tests | Required Pass | Optional |
|----------|-------|---------------|----------|
| P0 | 4 | 4/4 (100%) | N/A |
| P1 | 4 | 4/4 (100%) | N/A |
| P2 | 7 | 5/7 (71%) | 2 optional |
| **Total** | **15** | **13/15 (87%)** | **2 optional** |

**GO/NO-GO Decision:**
- GO: 13+ tests pass, all P0/P1 pass
- NO-GO: Any P0/P1 fails, or < 13 total pass

---

## Troubleshooting Guide

### Common Failures

| Symptom | Likely Cause | Resolution |
|---------|--------------|------------|
| OAuth token fails | Invalid credentials | Regenerate client secret |
| MCP handshake timeout | Network firewall | Open port 443 |
| Table query returns empty | ACL blocking | Grant read role |
| Rate limit triggers early | Counter not resetting | Check time window logic |
| Session expires immediately | Timeout misconfigured | Adjust system property |

### Log Locations

| Log Type | Location |
|----------|----------|
| Application Logs | System Logs > Application |
| OAuth Logs | System OAuth > Logs |
| REST Logs | System Web Services > Logs |
| MCP Logs | x_universal_mcp_log table |

---

## Test Maintenance

| Activity | Frequency | Owner |
|----------|-----------|-------|
| Review test coverage | Per release | QA Lead |
| Update for new features | As needed | Development |
| Performance baseline | Quarterly | DevOps |
| Security test review | Annually | Security |

---

*Test Suite SOP generated by ServiceNow Scoped App Factory. Version: 1.0.0*
