# Dashboard Spec

Runtime URL: `http://127.0.0.1:8000/dashboard`

## Main Layer

| Panel | Source fields | Unit | Threshold |
|---|---|---|---|
| Latency | `latency_p50_ms`, `latency_p95_ms`, `latency_p99_ms` | milliseconds | P95 `< 3000 ms` |
| Traffic | `traffic`, `total_requests` | requests | informational |
| Errors | `error_rate_pct`, `error_breakdown` | percent | `< 2%` |
| Cost | `total_cost_usd` | USD | `< $2.50/day` |
| Tokens | `tokens_in_total`, `tokens_out_total` | tokens | informational |
| Quality | `quality_avg` | score 0-1 | `>= 0.75` |

## Dashboard Settings

- Default time range: last 1 hour.
- Auto refresh: 15 seconds.
- Main layer panel count: exactly 6.
- SLO source: `config/slo.yaml`.
- Evidence path: `docs/evidence/dashboard-6-panels.png`.
