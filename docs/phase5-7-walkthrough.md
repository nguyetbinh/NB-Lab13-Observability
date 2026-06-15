# Walkthrough Phase 5, 6 va 7

## Phase 5 - Metrics va Dashboard

`app/metrics.py` duoc bo sung thread lock, reset measurement window va cac SLI:

- P50/P95/P99 latency theo milliseconds;
- traffic va total attempts;
- error count, error rate va breakdown;
- average/total cost USD;
- input/output tokens;
- average quality score.

`app/dashboard.py` cung cap dashboard tai `/dashboard`:

- dung 6 panels;
- range hien thi 1 gio;
- refresh 15 giay;
- latency SLO `< 3000 ms`;
- error SLO `< 2%`;
- cost budget `< $2.50/day`;
- quality objective `>= 0.75`.

Baseline:

```text
P50=156 ms
P95=157 ms
P99=157 ms
error_rate=0.00%
cost=$0.020040
quality=0.88
```

Evidence: `docs/evidence/dashboard-6-panels.png`.

## Phase 6 - Alerts va Incident Drill

### Alert rules

Ba rules trong `config/alert_rules.yaml`:

1. `high_latency_p95`: P2, P95 > 3000 ms for 5m.
2. `high_error_rate`: P1, error rate > 2% for 5m.
3. `cost_budget_spike`: P2, daily cost > $2.50 for 15m.

`scripts/verify_alerts.py` kiem tra name, severity, owner, condition, type va
runbook anchor.

### Incident drill

Scenario: `rag_slow`.

Flow dieu tra:

1. Metrics: P95 tang tu 157 ms len 3662 ms.
2. Traces: trace `65c9bd50639192acc5020afe53019648` cho thay
   `rag-retrieval=3506 ms`, `llm-generation=156 ms`.
3. Logs: correlation ID `incident-rag-slow` chua cung trace ID va request
   context.

Sau khi disable incident va reset metrics, P95 phuc hoi ve 158 ms.

Evidence:

- `docs/evidence/incident-dashboard.png`;
- `docs/evidence/trace-waterfall.png`;
- `docs/evidence/incident-log.json`;
- `docs/evidence/recovery-dashboard.png`.

## Phase 7 - Report va Evidence

Da dien:

- `docs/blueprint-template.md`;
- `docs/grading-evidence.md`;
- `docs/incident-report.md`;
- SLO table bang so lieu that;
- individual contribution;
- 6 required evidence images.

Git implementation evidence:

```text
00c8c67 feat: complete observability metrics tracing and incident tooling
```

Scripts phuc vu verification/evidence:

- `scripts/verify_traces.py`;
- `scripts/verify_alerts.py`;
- `scripts/capture_trace_evidence.py`;
- `scripts/build_evidence_pages.py`.

## Final Commands

```bash
.venv/bin/pytest -q
.venv/bin/python scripts/validate_logs.py
.venv/bin/python scripts/verify_traces.py --minimum 10
.venv/bin/python scripts/verify_alerts.py
```
