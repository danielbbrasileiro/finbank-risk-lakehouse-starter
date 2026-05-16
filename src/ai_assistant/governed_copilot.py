from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from src.ai_assistant.retrieval import build_corpus, retrieve_context
from src.ai_assistant.sql_guardrails import SqlGuardrailError, build_guarded_query


@dataclass(frozen=True)
class CopilotAnswer:
    response: str
    citations: list[str]
    guarded_sql: str | None


def answer_question(
    question: str,
    *,
    corpus_paths: list[Path] | None = None,
    allowed_schemas: tuple[str, ...] = ("analytics_marts",),
    default_limit: int = 100,
) -> CopilotAnswer:
    """Return a deterministic governed answer for demos and CI evaluation."""
    if _looks_destructive(question):
        return CopilotAnswer(
            response=(
                "I cannot run destructive or administrative SQL. "
                "The FinBank copilot is limited to governed read-only portfolio analysis."
            ),
            citations=[],
            guarded_sql=None,
        )

    corpus = build_corpus(corpus_paths or _default_corpus_paths())
    contexts = retrieve_context(question, corpus, top_k=3)
    citations = [context.source for context in contexts]

    draft_sql = _draft_sql(question)
    guarded_sql: str | None = None
    if draft_sql:
        try:
            guarded_sql = build_guarded_query(
                draft_sql,
                allowed_schemas=allowed_schemas,
                default_limit=default_limit,
            )
        except SqlGuardrailError as exc:
            return CopilotAnswer(
                response=f"The generated SQL was rejected by guardrails: {exc}",
                citations=citations,
                guarded_sql=None,
            )

    return CopilotAnswer(
        response=_compose_response(question, citations, guarded_sql),
        citations=citations,
        guarded_sql=guarded_sql,
    )


def _default_corpus_paths() -> list[Path]:
    return [Path("docs"), Path("dbt/models"), Path("schemas")]


def _looks_destructive(question: str) -> bool:
    lowered = question.lower()
    return any(keyword in lowered for keyword in ("delete", "drop", "truncate", "update", "insert", "grant"))


def _draft_sql(question: str) -> str | None:
    lowered = question.lower()
    if "exposure" in lowered and "segment" in lowered:
        return (
            "select segment, sum(total_outstanding_balance) as total_outstanding_balance "
            "from analytics_marts.mart_customer_exposure "
            "group by segment "
            "order by total_outstanding_balance desc"
        )
    if "suspicious" in lowered or "transaction" in lowered:
        return (
            "select transaction_date, channel, sum(suspicious_count) as suspicious_count "
            "from analytics_marts.mart_daily_transactions "
            "group by transaction_date, channel "
            "order by transaction_date desc"
        )
    if "default" in lowered or "high risk" in lowered:
        return (
            "select portfolio_status, count(*) as customer_count, "
            "sum(total_outstanding_balance) as total_outstanding_balance "
            "from analytics_marts.mart_customer_exposure "
            "group by portfolio_status "
            "order by total_outstanding_balance desc"
        )
    return None


def _compose_response(question: str, citations: list[str], guarded_sql: str | None) -> str:
    response = (
        "FinBank governed offline mode: I can answer from project documentation and "
        "only propose read-only SQL against allowlisted risk marts."
    )
    if guarded_sql:
        response += f"\n\nGuarded SQL:\n```sql\n{guarded_sql}\n```"
    else:
        response += "\n\nI did not need SQL for this question."
    if citations:
        response += "\n\nSources:\n" + "\n".join(f"- {source}" for source in citations)
    else:
        response += "\n\nNo local source matched this question."
    return response
