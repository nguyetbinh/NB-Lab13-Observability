from __future__ import annotations

import html
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from app.tracing import get_langfuse_client

ROOT = Path(__file__).resolve().parents[1]
EVIDENCE = ROOT / "docs" / "evidence"


def page(title: str, subtitle: str, content: str) -> str:
    return f"""<!doctype html>
<html><head><meta charset="utf-8"><title>{html.escape(title)}</title>
<style>
body {{ background:#07111f;color:#e5eefb;font-family:Inter,system-ui;margin:0;padding:34px }}
main {{ max-width:1120px;margin:auto }} h1 {{ margin-bottom:6px }} .subtitle {{ color:#91a9c7;margin-bottom:22px }}
article,pre {{ background:#101e32;border:1px solid #294563;border-radius:12px;padding:17px;margin:12px 0 }}
.row {{ display:grid;grid-template-columns:2fr 1fr 1fr;gap:12px }} code {{ color:#48d597 }}
.tag {{ display:inline-block;background:#233c59;border-radius:12px;padding:3px 8px;margin:2px;color:#8fc7ff }}
pre {{ white-space:pre-wrap;word-break:break-word;font-size:15px;line-height:1.5 }} mark {{ background:#234d43;color:#60e8aa }}
</style></head><body><main><h1>{html.escape(title)}</h1>
<div class="subtitle">{html.escape(subtitle)}</div>{content}</main></body></html>"""


def as_dict(model) -> dict:
    if hasattr(model, "model_dump"):
        return model.model_dump(by_alias=True)
    return model.dict(by_alias=True)


def main() -> None:
    EVIDENCE.mkdir(parents=True, exist_ok=True)
    records = [
        json.loads(line)
        for line in (ROOT / "data" / "logs.jsonl").read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]
    api_records = [record for record in records if record.get("service") == "api"]
    correlation = next(
        record for record in api_records if record.get("event") == "response_sent"
    )
    pii = next(
        record
        for record in api_records
        if "[REDACTED_" in json.dumps(record, ensure_ascii=False)
    )

    correlation_text = json.dumps(correlation, ensure_ascii=False, indent=2)
    pii_text = json.dumps(pii, ensure_ascii=False, indent=2)
    (EVIDENCE / "correlation-log.html").write_text(
        page(
            "Structured Log Correlation Evidence",
            "One response log connects correlation ID, trace ID and enriched request context.",
            f"<pre>{html.escape(correlation_text)}</pre>",
        ),
        encoding="utf-8",
    )
    (EVIDENCE / "pii-redaction-log.html").write_text(
        page(
            "PII Redaction Evidence",
            "Raw personal data is removed before JSON rendering and file output.",
            f"<pre>{html.escape(pii_text)}</pre>",
        ),
        encoding="utf-8",
    )

    client = get_langfuse_client()
    traces = as_dict(
        client.api.trace.list(limit=10, name="agent-run", tags="lab", order_by="timestamp.desc")
    )["data"]
    rows = []
    for trace in traces:
        tags = "".join(
            f'<span class="tag">{html.escape(tag)}</span>' for tag in trace.get("tags", [])
        )
        rows.append(
            f"""<article class="row">
            <div><b>{html.escape(trace['name'])}</b><br><code>{html.escape(trace['id'])}</code><br>{tags}</div>
            <div>Session<br><b>{html.escape(trace.get('sessionId') or '')}</b></div>
            <div>Latency<br><b>{(trace.get('latency') or 0) * 1000:.0f} ms</b></div>
            </article>"""
        )
    (EVIDENCE / "trace-list.html").write_text(
        page(
            "Langfuse Trace List",
            f"{len(traces)} recent agent traces with session IDs and lab/feature/model tags.",
            "".join(rows),
        ),
        encoding="utf-8",
    )

    print(f"Built evidence pages in {EVIDENCE}")


if __name__ == "__main__":
    main()
