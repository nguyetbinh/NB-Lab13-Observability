# Incident Report: RAG Latency Spike

## Summary

The `rag_slow` scenario caused retrieval latency to breach the user-facing P95
SLO. The investigation followed `Metrics -> Traces -> Logs`, then disabled the
incident and confirmed recovery.

## Timeline

| Stage | P50 | P95 | P99 | Error Rate |
|---|---:|---:|---:|---:|
| Baseline | 156 ms | 157 ms | 157 ms | 0.00% |
| `rag_slow` enabled | 3659 ms | 3662 ms | 3662 ms | 0.00% |
| Recovery | 156 ms | 158 ms | 158 ms | 0.00% |

## Investigation

### 1. Metrics

P95 increased by 3505 ms, from 157 ms to 3662 ms. Error rate stayed at 0%,
which indicated a latency degradation rather than an availability failure.

### 2. Traces

Evidence trace: `65c9bd50639192acc5020afe53019648`

| Observation | Latency |
|---|---:|
| `agent-run` | 3663 ms |
| `rag-retrieval` | 3506 ms |
| `llm-generation` | 156 ms |

The RAG span accounted for approximately 96% of total trace latency.

### 3. Logs

Correlation ID: `incident-rag-slow`

The `response_sent` log contains:

- the same trace ID;
- latency `3662 ms`;
- hashed user ID;
- session `incident-rag-slow`;
- feature and model context.

Evidence: [incident-log.json](evidence/incident-log.json)

## Root Cause

The injected `rag_slow` state added a 3.5-second delay inside retrieval. The LLM
generation duration remained normal, so model performance was not the cause.

## Mitigation and Recovery

1. Disabled `rag_slow`.
2. Reset the metrics measurement window.
3. Reran the 10-query load test.
4. Confirmed P95 recovered to 158 ms and all incident flags were false.

## Prevention

- Alert on `latency_p95_ms > 3000 for 5m`.
- Inspect RAG and LLM spans separately.
- Add a retrieval timeout and fallback data source in a production system.
- Keep trace IDs in response logs for direct log-to-trace navigation.
