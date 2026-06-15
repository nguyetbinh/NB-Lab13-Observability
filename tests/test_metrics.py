from app.metrics import percentile, record_error, record_request, reset, snapshot


def test_percentile_basic() -> None:
    assert percentile([100, 200, 300, 400], 50) >= 100


def test_metrics_snapshot_includes_dashboard_slis() -> None:
    reset()
    record_request(120, 0.001, 20, 30, 0.8)
    record_error("RuntimeError")

    metrics = snapshot()

    assert metrics["total_requests"] == 2
    assert metrics["error_rate_pct"] == 50.0
    assert metrics["latency_p95_ms"] == 120.0
    assert metrics["tokens_in_total"] == 20
    assert metrics["tokens_out_total"] == 30
    assert metrics["quality_avg"] == 0.8

    reset()
