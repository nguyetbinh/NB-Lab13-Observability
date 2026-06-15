from __future__ import annotations

import argparse
import sys
import time
from datetime import datetime, timedelta, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from app.tracing import flush_traces, get_langfuse_client, tracing_enabled

REQUIRED_OBSERVATIONS = {"agent-run", "rag-retrieval", "llm-generation"}


def as_dict(model) -> dict:
    if hasattr(model, "model_dump"):
        return model.model_dump(by_alias=True)
    return model.dict(by_alias=True)


def validate_trace(trace: dict) -> list[str]:
    errors: list[str] = []
    tags = set(trace.get("tags") or [])
    metadata = trace.get("metadata") or {}
    observations = trace.get("observations") or []
    observation_names = {item.get("name") for item in observations}
    generations = [
        item for item in observations if item.get("name") == "llm-generation"
    ]

    if not trace.get("userId"):
        errors.append("missing hashed user ID")
    if not trace.get("sessionId"):
        errors.append("missing session ID")
    if "lab" not in tags or len(tags) < 3:
        errors.append("missing lab/feature/model tags")
    if not {"doc_count", "query_preview"}.issubset(metadata):
        errors.append("missing doc_count/query_preview metadata")
    if not REQUIRED_OBSERVATIONS.issubset(observation_names):
        errors.append("missing agent/RAG/LLM waterfall observations")
    if not generations or not generations[0].get("usageDetails"):
        errors.append("missing generation token usage")

    return errors


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--minimum", type=int, default=10)
    parser.add_argument("--retries", type=int, default=6)
    parser.add_argument("--delay", type=float, default=3.0)
    args = parser.parse_args()

    if not tracing_enabled():
        raise SystemExit("Langfuse tracing is not configured.")

    client = get_langfuse_client()
    if not client or not client.auth_check():
        raise SystemExit("Langfuse authentication failed.")

    flush_traces()
    traces: list[dict] = []
    since = datetime.now(timezone.utc) - timedelta(hours=1)

    for attempt in range(1, args.retries + 1):
        response = client.api.trace.list(
            limit=max(args.minimum * 2, 20),
            name="agent-run",
            tags="lab",
            from_timestamp=since,
            order_by="timestamp.desc",
        )
        summaries = as_dict(response).get("data", [])
        valid_traces = []
        for summary in summaries:
            details = client.api.trace.get(summary["id"])
            trace = as_dict(details)
            if not validate_trace(trace):
                valid_traces.append(trace)
            if len(valid_traces) >= args.minimum:
                break
        traces = valid_traces

        if len(traces) >= args.minimum:
            break

        print(
            f"Waiting for Langfuse ingestion "
            f"({len(traces)}/{args.minimum}, attempt {attempt}/{args.retries})..."
        )
        time.sleep(args.delay)

    if len(traces) < args.minimum:
        raise SystemExit(
            f"Only {len(traces)} valid candidate traces found; "
            f"expected at least {args.minimum}."
        )

    evidence = traces[0]
    trace_url = f"{client._host.rstrip('/')}{evidence['htmlPath']}"

    print("--- Phase 4 Langfuse Verification ---")
    print(f"Authentication: passed")
    print(f"Verified traces: {args.minimum}")
    print("Required metadata/tags: passed")
    print("Token usage: passed")
    print("Waterfall observations: agent-run, rag-retrieval, llm-generation")
    print(f"Evidence trace ID: {evidence['id']}")
    print(f"Evidence trace URL: {trace_url}")


if __name__ == "__main__":
    main()
