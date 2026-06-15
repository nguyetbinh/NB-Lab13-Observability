# Báo cáo cá nhân Day 13 Observability Lab

## 1. Thông tin cá nhân

- [GROUP_NAME]: Vương Nguyệt Bình - Individual Submission
- [REPO_URL]: https://github.com/nguyetbinh/NB-Lab13-Observability
- [MEMBERS]:
  - Vương Nguyệt Bình | Vai trò: Thực hiện cá nhân toàn bộ Logging, Tracing, Metrics, Dashboard, Alerts, Incident Response và Report

---

## 2. Kết quả kỹ thuật (Auto-Verified)

- [VALIDATE_LOGS_FINAL_SCORE]: 100/100
- [TOTAL_TRACES_COUNT]: 77 agent traces in Langfuse; latest 10 verified automatically
- [PII_LEAKS_FOUND]: 0

---

## 3. Minh chứng kỹ thuật

### 3.1 Logging & Tracing

- [EVIDENCE_CORRELATION_ID_SCREENSHOT]: [docs/evidence/correlation-log.png](evidence/correlation-log.png)
- [EVIDENCE_PII_REDACTION_SCREENSHOT]: [docs/evidence/pii-redaction-log.png](evidence/pii-redaction-log.png)
- [EVIDENCE_TRACE_LIST_SCREENSHOT]: [docs/evidence/trace-list.png](evidence/trace-list.png)
- [EVIDENCE_TRACE_WATERFALL_SCREENSHOT]: [docs/evidence/trace-waterfall.png](evidence/trace-waterfall.png)
- [TRACE_WATERFALL_EXPLANATION]: Trace `65c9bd50639192acc5020afe53019648` mất tổng cộng 3663 ms. Span `rag-retrieval` chiếm 3506 ms, trong khi `llm-generation` chỉ mất 156 ms. Điều này chứng minh nút thắt nằm ở bước retrieval, không phải mô hình LLM.

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

## 4. Xử lý sự cố

- [SCENARIO_NAME]: `rag_slow`
- [SYMPTOMS_OBSERVED]: P95 baseline là 157 ms. Khi bật incident, P95 tăng lên 3662 ms và vượt SLO 3000 ms. Error rate vẫn bằng 0%, vì vậy đây là sự cố latency thay vì availability.
- [ROOT_CAUSE_PROVED_BY]: Trace `65c9bd50639192acc5020afe53019648` cho thấy `rag-retrieval=3506 ms`, còn `llm-generation=156 ms`. Log có correlation ID `incident-rag-slow` chứa cùng trace ID, session và request context.
- [FIX_ACTION]: Tắt `rag_slow`, reset cửa sổ metrics và chạy lại load test gồm 10 queries.
- [PREVENTIVE_MEASURE]: Cảnh báo khi P95 vượt 3000 ms trong 5 phút; kiểm tra RAG span trước, sau đó áp dụng retrieval timeout và fallback source.

Full RCA: [docs/incident-report.md](incident-report.md)

---

## 5. Đóng góp cá nhân và minh chứng

### Vương Nguyệt Bình

- [TASKS_COMPLETED]: Cá nhân hoàn thành toàn bộ bài lab: triển khai correlation ID middleware; enrich structured logs; hash user ID; redact đệ quy email, số điện thoại, CCCD, thẻ tín dụng, passport và địa chỉ; tích hợp Langfuse v3; xây dựng waterfall `agent-run -> rag-retrieval + llm-generation`; ghi token usage, cost và trace ID; xây dựng metrics và dashboard 6 panels; cấu hình 3 alert rules cùng runbook; chạy incident drill `rag_slow` theo flow Metrics -> Traces -> Logs; xác minh recovery; viết test, validation scripts, walkthrough, RCA và báo cáo cuối.
- [EVIDENCE_LINK]: [Implementation commit 00c8c67](https://github.com/nguyetbinh/NB-Lab13-Observability/commit/00c8c67), [Phase 1/2/4 walkthrough](phase1-2-4-walkthrough.md), [Phase 3 walkthrough](phase3-walkthrough.md), [Phase 5-7 walkthrough](phase5-7-walkthrough.md)

---

## 6. Bonus Items (Optional)

- [BONUS_COST_OPTIMIZATION]: Token and cost details are attached to every Langfuse generation and displayed on the dashboard for future optimization.
- [BONUS_AUDIT_LOGS]: Not implemented.
- [BONUS_CUSTOM_METRIC]: Added quality average, error rate, total attempts and trace ID correlation beyond the starter metrics.
