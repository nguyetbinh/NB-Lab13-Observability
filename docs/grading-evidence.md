# Evidence Collection Sheet

## Required Evidence

| Requirement | Evidence |
|---|---|
| Langfuse trace list with >= 10 traces | [trace-list.png](evidence/trace-list.png) |
| One full trace waterfall | [trace-waterfall.png](evidence/trace-waterfall.png) |
| JSON logs showing correlation ID | [correlation-log.png](evidence/correlation-log.png) |
| Log line with PII redaction | [pii-redaction-log.png](evidence/pii-redaction-log.png) |
| Dashboard with 6 panels | [dashboard-6-panels.png](evidence/dashboard-6-panels.png) |
| Alert rules with runbook link | [alert-rules.png](evidence/alert-rules.png) |

## Incident Evidence

| Stage | Evidence |
|---|---|
| Baseline metrics | [baseline-metrics.json](evidence/baseline-metrics.json) |
| Incident metrics | [incident-metrics.json](evidence/incident-metrics.json) |
| Incident dashboard | [incident-dashboard.png](evidence/incident-dashboard.png) |
| Correlated incident log | [incident-log.json](evidence/incident-log.json) |
| Langfuse trace details | [incident-trace.json](evidence/incident-trace.json) |
| Recovery metrics | [recovery-metrics.json](evidence/recovery-metrics.json) |
| Recovery dashboard | [recovery-dashboard.png](evidence/recovery-dashboard.png) |

## Verification Commands

```bash
.venv/bin/pytest -q
.venv/bin/python scripts/validate_logs.py
.venv/bin/python scripts/verify_traces.py --minimum 10
.venv/bin/python scripts/verify_alerts.py
```
