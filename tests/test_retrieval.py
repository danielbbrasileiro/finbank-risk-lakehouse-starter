from pathlib import Path

from src.ai_assistant.retrieval import build_corpus, retrieve_context


def test_build_corpus_keeps_source_paths(tmp_path: Path) -> None:
    docs = tmp_path / "docs"
    docs.mkdir()
    (docs / "risk.md").write_text(
        "# Risk mart\nmart_customer_exposure contains portfolio_status and days past due.",
        encoding="utf-8",
    )

    corpus = build_corpus([docs])

    assert len(corpus) == 1
    assert corpus[0].source.endswith("risk.md")
    assert "portfolio_status" in corpus[0].text


def test_retrieve_context_returns_relevant_citations(tmp_path: Path) -> None:
    docs = tmp_path / "docs"
    docs.mkdir()
    (docs / "risk.md").write_text(
        "The mart_customer_exposure table tracks total_outstanding_balance by segment.",
        encoding="utf-8",
    )
    (docs / "quality.md").write_text(
        "The Rust validator checks required columns before loading raw CSV files.",
        encoding="utf-8",
    )

    corpus = build_corpus([docs])
    results = retrieve_context("customer exposure by segment", corpus, top_k=1)

    assert len(results) == 1
    assert results[0].source.endswith("risk.md")
    assert "mart_customer_exposure" in results[0].text
