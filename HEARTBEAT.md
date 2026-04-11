# Keep this file empty (or with only comments) to skip heartbeat API calls.

# Add tasks below when you want the agent to check something periodically.

## Periodic Checks (during heartbeats)

### 1. Cron Job Status Check
Check all cron jobs for errors. Alert only on **fresh failures** — not known/old errors.

**Skip if ALL of these are true**:
- `lastRunStatus` is `error`
- AND `lastError` contains a known/expected error that was already diagnosed and fixed (timeout, missing delivery.to, etc.)
- AND a fix was already applied but next run hasn't happened yet

**Always alert if**:
- A job that previously ran OK now shows `error` (new failure)
- `consecutiveErrors` just increased
- Unknown error message

When alerting, include: task name, error message, fix applied or plan.

### 2. Task Log Review
Read TASK_LOG.md and ISSUE_LOG.md. If no entries in the past 24h, consider:
- Updating MEMORY.md with pending context
- Flagging for user's attention if important

### 3. Memory Maintenance
Every 3 days during heartbeat:
1. Read recent `memory/YYYY-MM-DD.md` files
2. Update MEMORY.md with significant learnings
3. Clean up outdated entries
