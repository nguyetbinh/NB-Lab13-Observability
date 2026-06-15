# Day 13 Observability Lab Report

## 1. Team Metadata

- [GROUP_NAME]: NB-Lab13-Observability
- [REPO_URL]: https://github.com/nguyetbinh/NB-Lab13-Observability
- [MEMBERS]:
  - Member A: Tin Duong | Role: Individual submission - Logging, Tracing, SRE, Incident Response, Report
  - Member B: Not assigned | Role: Individual submission
  - Member C: Not assigned | Role: Individual submission
  - Member D: Not assigned | Role: Individual submission
  - Member E: Not assigned | Role: Individual submission

---

## 2. Group Performance (Auto-Verified)

- [VALIDATE_LOGS_FINAL_SCORE]: 100/100
- [TOTAL_TRACES_COUNT]: 77 agent traces in Langfuse; latest 10 verified automatically
- [PII_LEAKS_FOUND]: 0

---

## 3. Technical Evidence (Group)

### 3.1 Logging & Tracing

- [EVIDENCE_CORRELATION_ID_SCREENSHOT]: [docs/evidence/correlation-log.png](evidence/correlation-log.png)
- [EVIDENCE_PII_REDACTION_SCREENSHOT]: [docs/evidence/pii-redaction-log.png](evidence/pii-redaction-log.png)
- [EVIDENCE_TRACE_LIST_SCREENSHOT]: [docs/evidence/trace-list.png](evidence/trace-list.png)
- [EVIDENCE_TRACE_WATERFALL_SCREENSHOT]: [docs/evidence/trace-waterfall.png](evidence/trace-waterfall.png)
- [TRACE_WATERFALL_EXPLANATION]: Trace `65c9bd50639192acc5020afe53019648` took 3663 ms. Its `rag-retrieval` span took 3506 ms while `llm-generation` took 156 ms, proving retrieval was the latency bottleneck.

### 3.2 Dashboard & SLOs

- [DASHBOARD_6_PANELS_SCREENSHOT]: [docs/evidence/dashboard-6-panels.png](evidence/dashboard-6-panels.png)
- [INCIDENT_DASHBOARD_SCREENSHOT]: [docs/evidence/incident-dashboard.png](evidence/incident-dashboard.png)
- [RECOVERY_DASHBOARD_SCREENSHOT]: [docs/evidence/recovery-dashboard.png](evidence/recovery-dashboard.png)
- [SLO_TABLE]:

| SLI | Target | Window | Current Value |
|---|---:|---|---:|
| Latency P95 | < 3000 ms | 28d objective; current run | 158 ms |
| Error Rate | < 2% | 28d objective; current run | 0.00% |
| Cost Budget | < $2.50/day | 1d objective; current run | $0.019545 |
| Quality Average | >= 0.75 | current run | 0.88 |

### 3.3 Alerts & Runbook

- [ALERT_RULES_SCREENSHOT]: [docs/evidence/alert-rules.png](evidence/alert-rules.png)
- [SAMPLE_RUNBOOK_LINK]: [docs/alerts.md#1-high-latency-p95](alerts.md#1-high-latency-p95)

---

## 4. Incident Response (Group)

- [SCENARIO_NAME]: `rag_slow`
- [SYMPTOMS_OBSERVED]: Baseline P95 was 157 ms. During the incident P95 rose to 3662 ms and breached the 3000 ms SLO. Error rate remained 0%, isolating the symptom to latency.
- [ROOT_CAUSE_PROVED_BY]: Trace `65c9bd50639192acc5020afe53019648`; `rag-retrieval=3506 ms`, `llm-generation=156 ms`. Log correlation ID `incident-rag-slow` contains the same trace ID, session and request context.
- [FIX_ACTION]: Disabled `rag_slow`, reset the measurement window and reran the 10-query load test.
- [PREVENTIVE_MEASURE]: Alert when P95 exceeds 3000 ms for 5 minutes; inspect RAG span first, then use a retrieval timeout/fallback source.

Full RCA: [docs/incident-report.md](incident-report.md)

---

## 5. Individual Contributions & Evidence

### Tin Duong

- [TASKS_COMPLETED]: Implemented correlation middleware, structured log enrichment, recursive PII redaction, Langfuse v3 tracing, RAG/LLM waterfall spans, rolling run metrics, six-panel dashboard, alert validation, incident drill, automated evidence generation and final report.
- [EVIDENCE_LINK]: [Implementation commit 00c8c67](https://github.com/nguyetbinh/NB-Lab13-Observability/commit/00c8c67), [Phase 1/2/4 walkthrough](phase1-2-4-walkthrough.md), [Phase 3 walkthrough](phase3-walkthrough.md), [Phase 5-7 walkthrough](phase5-7-walkthrough.md)

### Not Assigned - Member B

- [TASKS_COMPLETED]: Individual submission; covered by Tin Duong.
- [EVIDENCE_LINK]: Not applicable.

### Not Assigned - Member C

- [TASKS_COMPLETED]: Individual submission; covered by Tin Duong.
- [EVIDENCE_LINK]: Not applicable.

### Not Assigned - Member D

- [TASKS_COMPLETED]: Individual submission; covered by Tin Duong.
- [EVIDENCE_LINK]: Not applicable.

### Not Assigned - Member E

- [TASKS_COMPLETED]: Individual submission; covered by Tin Duong.
- [EVIDENCE_LINK]: Not applicable.

---

## 6. Bonus Items (Optional)

- [BONUS_COST_OPTIMIZATION]: Token and cost details are attached to every Langfuse generation and displayed on the dashboard for future optimization.
- [BONUS_AUDIT_LOGS]: Not implemented.
- [BONUS_CUSTOM_METRIC]: Added quality average, error rate, total attempts and trace ID correlation beyond the starter metrics.
