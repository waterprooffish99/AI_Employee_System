# Error Recovery - Agent Skill for Graceful Degradation

## Overview

Handles errors gracefully with automatic recovery and user notification.

## Error Categories

### 1. Transient Errors
- **Examples**: Temporary network issues, API timeouts
- **Action**: Retry with exponential backoff
- **User Notification**: No

### 2. Authentication Errors
- **Examples**: Expired tokens, invalid credentials
- **Action**: Request credential refresh
- **User Notification**: Yes (High priority)

### 3. Rate Limit Errors
- **Examples**: API rate limits exceeded
- **Action**: Backoff and queue
- **User Notification**: No

### 4. Validation Errors
- **Examples**: Invalid input, missing required fields
- **Action**: Log and skip
- **User Notification**: No

### 5. Critical Errors
- **Examples**: System failures, data corruption
- **Action**: Stop and alert
- **User Notification**: Yes (Critical priority)

## Usage

### Handle Error

```
An error occurred while posting to Twitter:
"Rate limit exceeded"

Apply error recovery strategy.
```

### Retry Failed Operation

```
Retry the failed invoice creation with:
- Max retries: 3
- Backoff: exponential
```

### Report Errors

```
Generate error report for the last 24 hours.
Include:
- Total errors
- By category
- Resolution status
```

## Retry Configuration

```yaml
max_retries: 3
backoff_base: 2  # Exponential factor
backoff_max: 60  # Maximum seconds between retries
jitter: 1.0      # Randomness factor
```

## Error Response Format

```json
{
  "category": "rate_limit",
  "action": "backoff_and_queue",
  "message": "Rate limit exceeded: Twitter API",
  "retry_recommended": true,
  "retry_delay_seconds": 60,
  "user_notification": false
}
```

## Graceful Degradation Strategies

### Odoo Unavailable
- Queue transactions locally
- Sync when connection restored
- Log all pending operations

### Social Media API Down
- Save posts as drafts
- Schedule for later posting
- Notify of delay

### Email Service Down
- Save emails locally
- Queue for sending
- Alert if urgent

## Error Logging

All errors logged with:
- Timestamp
- Error type and message
- Context (action, parameters)
- Resolution action taken
- Final status

## User Notification Rules

**Notify Immediately**:
- Authentication failures
- Critical system errors
- Data loss risks
- Security incidents

**Notify in Summary**:
- Repeated transient errors
- Rate limit issues
- Non-critical failures

**Don't Notify**:
- Single transient errors (auto-recovered)
- Expected validation failures
- Handled gracefully

## Recovery Procedures

### Procedure 1: API Reconnection
1. Detect connection loss
2. Wait 5 seconds
3. Attempt reconnection
4. Retry up to 3 times
5. Alert if still failing

### Procedure 2: Credential Refresh
1. Detect auth error
2. Check token expiry
3. Attempt token refresh
4. Retry operation
5. Alert if refresh fails

### Procedure 3: Data Sync Recovery
1. Detect sync failure
2. Queue pending changes
3. Mark items for retry
4. Sync when available
5. Verify consistency

## Monitoring

Track error metrics:
- Errors per hour/day
- Error rate by category
- Mean time to recovery
- Recurring error patterns

---

*Skill Version: 1.0.0 | Gold Tier*
