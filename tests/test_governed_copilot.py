from pathlib import Path

from src.ai_assistant.governed_copilot import answer_question


def test_answer_question_returns_citations_and_guarded_sql(tmp_path: Path) -> None:
    docs = tmp_path / "docs"
    docs.mkdir()
    (docs / "dictionary.md").write_text(
        "mart_customer_exposure exposes total_outstanding_balance, segment and portfolio_status.",
        encoding="utf-8",
    )

    answer = answer_question("show customer exposure by segment", corpus_paths=[docs])

    assert "analytics_marts.mart_customer_exposure" in answer.guarded_sql
    assert answer.guarded_sql.endswith("limit 100")
    assert answer.citations == [str(docs / "dictionary.md")]
    assert "governed offline mode" in answer.response.lower()


def test_answer_question_refuses_out_of_scope_questions(tmp_path: Path) -> None:
    docs = tmp_path / "docs"
    docs.mkdir()
    (docs / "quality.md").write_text("dbt tests validate risk mart quality.", encoding="utf-8")

    answer = answer_question("delete all raw customers", corpus_paths=[docs])

    assert answer.guarded_sql is None
    assert "cannot run destructive" in answer.response.lower()
