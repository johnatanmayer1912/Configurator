---
name: incident-response
description: Handle network incidents for NLAP — triage, mitigate, communicate, and write postmortems for network analysis platform incidents.
user-invocable: true
---

# Network Incident Response (Adapted for NLAP)

Handle production network incidents systematically for the Network Log Analysis Platform.

## Severity Levels

| Level | Definition | Response Time | Examples |
|-------|-----------|---------------|----------|
| SEV1 | Platform completely down, all network operators affected | Immediate | Application won't start, critical parsing failure, database corruption |
| SEV2 | Major feature broken, many network operators affected | < 30 min | Incident story generation fails, log collection broken, core parsing non-functional |
| SEV3 | Minor feature broken, workaround exists | < 4 hours | Single vendor parsing fails, UI display issue, slow performance |
| SEV4 | Cosmetic or low-impact issue | Next business day | Typo in UI, minor styling bug, documentation error |

## Incident Workflow

### 1. Detect & Triage (first 5 minutes)

- Acknowledge the incident — "I'm investigating this network incident"
- Determine severity level based on impact on network operations
- Check system logs: Look at recent error logs, application logs
- Check recent changes: Review `CHANGELOG.md` and recent commits
- Verify network device connectivity if applicable

### 2. Mitigate (next 15-30 minutes)

**The goal is to stop the bleeding, not find the root cause.**

Quick mitigations:
- **Restart application**: If application is completely unresponsive
- **Rollback code**: `git revert <commit>` if a recent change caused issues
- **Disable problematic feature**: Temporarily disable broken parsing or analysis
- **Switch to backup:** Use alternative log collection method if primary fails
- **Limit scope:** Restrict log processing to prevent overwhelming system
- **Clear cache:** Clear temporary files or cached data if corruption suspected

### 3. Communicate

**Internal:**
- Document incident in `docs/04-administrative/` incident logs
- Update incident status every 15-30 minutes
- Assign roles: Incident Commander, Technical Lead, Network Specialist

**External:**
- Update documentation if service is degraded
- Notify relevant team members if extended outage expected
- Be transparent about status and timeline

### 4. Resolve

- Deploy the fix
- Verify the fix works in production
- Test with realistic network data and device connections
- Close incident with summary

### 5. Postmortem (within 48 hours)

Write a comprehensive network incident postmortem:

```markdown
# Network Incident: Log Collection Failure for Cisco Devices
**Date:** 2026-06-15
**Duration:** 35 minutes (14:30 — 15:05 UTC)
**Severity:** SEV2
**Impact:** Network operators unable to collect logs from Cisco devices

## Timeline
- 14:30 — Alert fires: Cisco log collection success rate drops to 15%
- 14:35 — Investigation begins, examines error logs
- 14:40 - Identified: Cisco device connection timeout pattern
- 14:45 - Root cause: Recent change to SNMP timeout parameters caused timeout for slower devices
- 14:50 - Fix deployed: reverted SNMP timeout parameters
- 15:00 - Log collection success rate recovering
- 15:05 - Metrics back to normal, incident closed

## Root Cause
Recent parameter change in `modules/investigation/log_collectors.py` reduced SNMP timeout from 10s to 2s. This timeout was too short for slower network devices, causing connection failures for Cisco devices with slower response times.

## What Went Well
- Incident was detected by monitoring system within 5 minutes
- Quick rollback of timeout parameters resolved the issue
- No data loss occurred - logs were cached locally

## What Went Wrong
- Timeout parameter change was tested only with fast devices
- No testing with slower network devices common in production
- No monitoring for device-type-specific connection success rates

## Action Items
- [ ] Add device-type-specific timeout configuration (@network-team, due 2026-06-17)
- [ ] Implement per-vendor timeout parameters in log collectors (@network-team, due 2026-06-18)
- [ ] Add device-type monitoring to metrics dashboard (@observability-team, due 2026-06-19)
- [ ] Update device compatibility matrix for network device performance requirements (@docs-team, due 2026-06-20)
```

## NLAP-Specific Incident Types

### Log Collection Incidents
- Device connection failures
- Parsing errors for specific vendors
- Log file corruption or incomplete logs
- Performance degradation with large log files
- Multi-vendor collection coordination failures

### Analysis Incidents
- Incident story generation failures
- Network topology mapping errors
- Traffic analysis inaccuracies
- Configuration translation failures
- Pattern recognition false positives/negatives

### Platform Incidents
- Application startup failures
- Database connection issues
- Plugin system failures
- UI rendering problems
- Performance degradation

## Network-Specific Mitigation Strategies

### Device Connection Issues
- Fallback to cached logs if available
- Implement device-specific retry logic
- Use alternative connection methods if primary fails
- Prioritize critical devices over non-critical

### Parsing Errors
- Implement graceful degradation for unparseable logs
- Log unparseable entries for later investigation
- Skip problematic logs while continuing with others
- Alert operators to parsing issues for manual review

### Performance Issues
- Process logs in batches for large datasets
- Limit concurrent device connections
- Implement caching for frequently accessed data
- Optimize regex and parsing operations

## Tips

- Rollback recent code changes first — they're the most likely cause
- Test fixes with realistic network data, not just synthetic data
- Consider device variability when testing network operations
- Maintain runbooks for common network incident scenarios
- Document device-specific requirements and performance characteristics
- Use network monitoring data to validate incident resolution
- Practice incident response with simulated network incidents

## Post-Incident Follow-up

- Update device compatibility matrix if incident revealed new device requirements
- Update operational runbooks with new procedures
- Add monitoring for similar issues to prevent recurrence
- Update documentation with lessons learned
- Consider adding automated tests to prevent similar incidents
- Review change management process to prevent similar future incidents