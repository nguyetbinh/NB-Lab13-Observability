import json
from concurrent.futures import ThreadPoolExecutor

from fastapi.testclient import TestClient

from app import logging_config
from app.main import app


CHAT_PAYLOAD = {
    "user_id": "student-01",
    "session_id": "session-01",
    "feature": "qa",
    "message": "Contact student@vinuni.edu.vn about monitoring",
}


def test_chat_propagates_client_request_id_and_enriches_logs(tmp_path, monkeypatch) -> None:
    log_path = tmp_path / "logs.jsonl"
    monkeypatch.setattr(logging_config, "LOG_PATH", log_path)

    with TestClient(app) as client:
        response = client.post(
            "/chat",
            headers={"x-request-id": "client-request-123"},
            json=CHAT_PAYLOAD,
        )

    assert response.status_code == 200
    assert response.headers["x-request-id"] == "client-request-123"
    assert float(response.headers["x-response-time-ms"]) >= 0
    assert response.json()["correlation_id"] == "client-request-123"

    records = [
        json.loads(line)
        for line in log_path.read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]
    api_records = [record for record in records if record.get("service") == "api"]

    assert api_records
    for record in api_records:
        assert record["correlation_id"] == "client-request-123"
        assert record["user_id_hash"]
        assert record["session_id"] == "session-01"
        assert record["feature"] == "qa"
        assert record["model"]
        assert record["env"]
        assert "student@" not in json.dumps(record)


def test_chat_generates_request_id_when_header_is_missing(tmp_path, monkeypatch) -> None:
    monkeypatch.setattr(logging_config, "LOG_PATH", tmp_path / "logs.jsonl")

    with TestClient(app) as client:
        response = client.post("/chat", json=CHAT_PAYLOAD)

    correlation_id = response.headers["x-request-id"]
    assert response.status_code == 200
    assert correlation_id.startswith("req-")
    assert len(correlation_id) == 12
    assert response.json()["correlation_id"] == correlation_id


def test_parallel_requests_keep_distinct_correlation_ids(tmp_path, monkeypatch) -> None:
    monkeypatch.setattr(logging_config, "LOG_PATH", tmp_path / "logs.jsonl")
    request_ids = [f"parallel-request-{index}" for index in range(5)]

    def send_request(request_id: str) -> tuple[str, str]:
        with TestClient(app) as client:
            response = client.post(
                "/chat",
                headers={"x-request-id": request_id},
                json={**CHAT_PAYLOAD, "session_id": request_id},
            )
        assert response.status_code == 200
        return response.headers["x-request-id"], response.json()["correlation_id"]

    with ThreadPoolExecutor(max_workers=len(request_ids)) as executor:
        results = list(executor.map(send_request, request_ids))

    assert results == [(request_id, request_id) for request_id in request_ids]

    records = [
        json.loads(line)
        for line in logging_config.LOG_PATH.read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]
    api_records = [record for record in records if record.get("service") == "api"]
    assert {record["correlation_id"] for record in api_records} == set(request_ids)
    assert all(
        record["session_id"] == record["correlation_id"] for record in api_records
    )


def test_dashboard_and_alert_pages_are_available() -> None:
    with TestClient(app) as client:
        dashboard = client.get("/dashboard")
        alerts = client.get("/alerts")

    assert dashboard.status_code == 200
    assert dashboard.text.count('class="card"') == 6
    assert "Auto refresh: 15 seconds" in dashboard.text
    assert "P95 &lt; 3000 ms" in dashboard.text
    assert alerts.status_code == 200
    assert "high_latency_p95" in alerts.text
    assert "high_error_rate" in alerts.text
    assert "cost_budget_spike" in alerts.text
