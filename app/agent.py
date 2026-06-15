from __future__ import annotations

import time
from dataclasses import dataclass

from . import metrics
from .mock_llm import FakeLLM
from .mock_rag import retrieve
from .pii import hash_user_id, summarize_text
from .tracing import current_trace_id, get_langfuse_client, observe


@dataclass
class AgentResult:
    answer: str
    latency_ms: int
    tokens_in: int
    tokens_out: int
    cost_usd: float
    quality_score: float
    trace_id: str | None = None


class LabAgent:
    def __init__(self, model: str = "claude-sonnet-4-5") -> None:
        self.model = model
        self.llm = FakeLLM(model=model)

    @observe(name="agent-run", capture_input=False, capture_output=False)
    def run(self, user_id: str, feature: str, session_id: str, message: str) -> AgentResult:
        started = time.perf_counter()
        client = get_langfuse_client()
        query_preview = summarize_text(message)

        if client:
            client.update_current_trace(
                name="agent-run",
                user_id=hash_user_id(user_id),
                session_id=session_id,
                tags=["lab", feature, self.model],
                input={"feature": feature, "query_preview": query_preview},
                metadata={"feature": feature, "model": self.model},
            )

        with client.start_as_current_span(
            name="rag-retrieval",
            input={"query_preview": query_preview},
        ) if client else _null_span() as rag_span:
            docs = retrieve(message)
            rag_span.update(
                output={"doc_count": len(docs)},
                metadata={"doc_count": len(docs), "query_preview": query_preview},
            )

        prompt = f"Feature={feature}\nDocs={docs}\nQuestion={message}"
        with client.start_as_current_generation(
            name="llm-generation",
            model=self.model,
            input={"feature": feature, "query_preview": query_preview},
        ) if client else _null_span() as generation:
            response = self.llm.generate(prompt)
            cost_usd = self._estimate_cost(
                response.usage.input_tokens, response.usage.output_tokens
            )
            generation.update(
                output={"answer_preview": summarize_text(response.text)},
                metadata={"doc_count": len(docs), "query_preview": query_preview},
                usage_details={
                    "input": response.usage.input_tokens,
                    "output": response.usage.output_tokens,
                    "total": response.usage.input_tokens + response.usage.output_tokens,
                },
                cost_details={"total": cost_usd},
            )

        quality_score = self._heuristic_quality(message, response.text, docs)
        latency_ms = int((time.perf_counter() - started) * 1000)
        trace_id = current_trace_id()

        if client:
            client.update_current_span(
                output={
                    "answer_preview": summarize_text(response.text),
                    "quality_score": quality_score,
                },
                metadata={"doc_count": len(docs), "query_preview": query_preview},
            )
            client.update_current_trace(
                output={
                    "latency_ms": latency_ms,
                    "quality_score": quality_score,
                }
            )

        metrics.record_request(
            latency_ms=latency_ms,
            cost_usd=cost_usd,
            tokens_in=response.usage.input_tokens,
            tokens_out=response.usage.output_tokens,
            quality_score=quality_score,
        )

        return AgentResult(
            answer=response.text,
            latency_ms=latency_ms,
            tokens_in=response.usage.input_tokens,
            tokens_out=response.usage.output_tokens,
            cost_usd=cost_usd,
            quality_score=quality_score,
            trace_id=trace_id,
        )

    def _estimate_cost(self, tokens_in: int, tokens_out: int) -> float:
        input_cost = (tokens_in / 1_000_000) * 3
        output_cost = (tokens_out / 1_000_000) * 15
        return round(input_cost + output_cost, 6)

    def _heuristic_quality(self, question: str, answer: str, docs: list[str]) -> float:
        score = 0.5
        if docs:
            score += 0.2
        if len(answer) > 40:
            score += 0.1
        if question.lower().split()[0:1] and any(token in answer.lower() for token in question.lower().split()[:3]):
            score += 0.1
        if "[REDACTED" in answer:
            score -= 0.2
        return round(max(0.0, min(1.0, score)), 2)


class _NullSpan:
    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback) -> None:
        return None

    def update(self, **kwargs) -> None:
        return None


def _null_span() -> _NullSpan:
    return _NullSpan()
