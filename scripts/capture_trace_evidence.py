from __future__ import annotations

import argparse
import html
import json
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from app.tracing import get_langfuse_client


def as_dict(model) -> dict:
    if hasattr(model, "model_dump"):
        return model.model_dump(by_alias=True)
    return model.dict(by_alias=True)


def remove_sdk_metadata(value):
    if isinstance(value, dict):
        return {
            key: remove_sdk_metadata(item)
            for key, item in value.items()
            if key not in {"resourceAttributes", "scope"}
        }
    if isinstance(value, list):
        return [remove_sdk_metadata(item) for item in value]
    return value


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("trace_id")
    parser.add_argument("--output-dir", default="docs/evidence")
    parser.add_argument("--retries", type=int, default=6)
    args = parser.parse_args()

    client = get_langfuse_client()
    if not client or not client.auth_check():
        raise SystemExit("Langfuse authentication failed.")

    trace = None
    for attempt in range(args.retries):
        try:
            trace = remove_sdk_metadata(as_dict(client.api.trace.get(args.trace_id)))
            break
        except Exception:
            if attempt == args.retries - 1:
                raise
            time.sleep(3)

    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    (output_dir / "incident-trace.json").write_text(
        json.dumps(trace, ensure_ascii=False, indent=2, default=str) + "\n",
        encoding="utf-8",
    )

    observations = sorted(
        trace["observations"],
        key=lambda item: (
            item.get("parentObservationId") is not None,
            item.get("startTime"),
        ),
    )
    max_latency = max(item.get("latency") or 0 for item in observations) or 1
    rows = []
    for item in observations:
        latency = item.get("latency") or 0
        width = max(4, (latency / max_latency) * 100)
        usage = item.get("usageDetails") or {}
        rows.append(
            f"""
            <article>
              <div class="row">
                <div><b>{html.escape(item['name'])}</b> <span>{html.escape(item['type'])}</span></div>
                <strong>{latency * 1000:.0f} ms</strong>
              </div>
              <div class="track"><div class="bar" style="width:{width:.1f}%"></div></div>
              <div class="meta">Parent: {html.escape(str(item.get('parentObservationId') or 'root'))}
              | Tokens: {html.escape(str(usage or 'n/a'))}</div>
            </article>
            """
        )

    page = f"""<!doctype html>
<html><head><meta charset="utf-8"><title>Trace Waterfall</title>
<style>
body {{ background:#07111f;color:#e5eefb;font-family:Inter,system-ui;margin:0;padding:32px }}
main {{ max-width:1050px;margin:auto }} h1 {{ margin-bottom:6px }}
.subtitle,.meta,span {{ color:#91a9c7 }} article {{ background:#101e32;border:1px solid #294563;border-radius:12px;padding:18px;margin:14px 0 }}
.row {{ display:flex;justify-content:space-between;font-size:20px }} .track {{ height:16px;background:#1d3049;border-radius:8px;margin:14px 0 }}
.bar {{ height:100%;background:linear-gradient(90deg,#48d597,#4aa8ff);border-radius:8px }}
.root {{ color:#8fc7ff }} code {{ color:#48d597 }}
</style></head><body><main>
<h1>Langfuse Trace Waterfall</h1>
<div class="subtitle">Trace ID: <code>{html.escape(trace['id'])}</code> | Session: {html.escape(trace.get('sessionId') or '')}</div>
<div class="subtitle">Total latency: {trace.get('latency', 0) * 1000:.0f} ms | Root cause: RAG retrieval delay</div>
{''.join(rows)}
</main></body></html>"""
    (output_dir / "trace-waterfall.html").write_text(page, encoding="utf-8")

    print(f"Trace ID: {trace['id']}")
    for item in observations:
        print(f"- {item['name']}: {(item.get('latency') or 0) * 1000:.0f} ms")


if __name__ == "__main__":
    main()
