# Keep this file empty (or with only comments) to skip heartbeat API calls.

# Add tasks below when you want the agent to check something periodically.

## Periodic Checks (during heartbeats)

### 1. Cron Job Status Check
Check all cron jobs for errors. If any `lastRunStatus` is `error` or `consecutiveErrors > 0`:
- **Immediately notify user via WeChat** with:
  1. Task name and ID
  2. Error message
  3. Fix already applied or planned
- This is a hard rule: do NOT wait, do NOT ask permission

### 2. Task Log Review
Read TASK_LOG.md and ISSUE_LOG.md. If no entries in the past 24h, consider:
- Updating MEMORY.md with pending context
- Flagging for user's attention if important

### 3. Memory Maintenance
Every 3 days during heartbeat:
1. Read recent `memory/YYYY-MM-DD.md` files
2. Update MEMORY.md with significant learnings
3. Clean up outdated entries
