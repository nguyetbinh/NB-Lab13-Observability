from __future__ import annotations

import sys
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]
ALERT_CONFIG = ROOT / "config" / "alert_rules.yaml"
RUNBOOK = ROOT / "docs" / "alerts.md"
EXPECTED = {
    "high_latency_p95": {
        "severity": "P2",
        "owner": "team-oncall",
        "runbook": "docs/alerts.md#1-high-latency-p95",
    },
    "high_error_rate": {
        "severity": "P1",
        "owner": "team-oncall",
        "runbook": "docs/alerts.md#2-high-error-rate",
    },
    "cost_budget_spike": {
        "severity": "P2",
        "owner": "finops-owner",
        "runbook": "docs/alerts.md#3-cost-budget-spike",
    },
}


def main() -> None:
    config = yaml.safe_load(ALERT_CONFIG.read_text(encoding="utf-8"))
    runbook_text = RUNBOOK.read_text(encoding="utf-8")
    alerts = {item["name"]: item for item in config.get("alerts", [])}
    errors: list[str] = []

    if set(alerts) != set(EXPECTED):
        errors.append(f"expected alert names {sorted(EXPECTED)}, got {sorted(alerts)}")

    for name, expected in EXPECTED.items():
        alert = alerts.get(name)
        if not alert:
            continue
        for field, value in expected.items():
            if alert.get(field) != value:
                errors.append(
                    f"{name}.{field}: expected {value!r}, got {alert.get(field)!r}"
                )
        if not alert.get("condition"):
            errors.append(f"{name}: missing condition")
        if alert.get("type") != "symptom-based":
            errors.append(f"{name}: alert type must be symptom-based")

        heading = expected["runbook"].split("#", 1)[1].replace("-", " ").lower()
        normalized = runbook_text.lower().replace(".", "")
        if heading not in normalized:
            errors.append(f"{name}: runbook heading not found")

    if errors:
        print("Alert verification failed:")
        for error in errors:
            print(f"- {error}")
        sys.exit(1)

    print("--- Alert Verification ---")
    print("Rules verified: 3")
    for name in EXPECTED:
        alert = alerts[name]
        print(
            f"- {name}: {alert['severity']} | {alert['condition']} | "
            f"{alert['owner']} | {alert['runbook']}"
        )
    print("Runbook links: passed")


if __name__ == "__main__":
    main()
