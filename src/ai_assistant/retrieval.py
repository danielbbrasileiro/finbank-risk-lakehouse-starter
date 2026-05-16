from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path

SUPPORTED_EXTENSIONS = {".md", ".sql", ".yml", ".yaml", ".json"}


@dataclass(frozen=True)
class CorpusDocument:
    source: str
    text: str


@dataclass(frozen=True)
class RetrievedContext:
    source: str
    text: str
    score: int


def build_corpus(paths: list[Path]) -> list[CorpusDocument]:
    documents: list[CorpusDocument] = []
    for base_path in paths:
        path = Path(base_path)
        candidates = path.rglob("*") if path.is_dir() else [path]
        for candidate in sorted(candidates):
            if not candidate.is_file() or candidate.suffix.lower() not in SUPPORTED_EXTENSIONS:
                continue
            text = candidate.read_text(encoding="utf-8")
            if text.strip():
                documents.append(CorpusDocument(source=str(candidate), text=text))
    return documents


def retrieve_context(query: str, corpus: list[CorpusDocument], *, top_k: int = 4) -> list[RetrievedContext]:
    query_terms = _tokenize(query)
    scored: list[RetrievedContext] = []

    for document in corpus:
        document_terms = _tokenize(document.text)
        score = sum(document_terms.count(term) for term in query_terms)
        if score > 0:
            scored.append(
                RetrievedContext(
                    source=document.source,
                    text=_compact_text(document.text),
                    score=score,
                )
            )

    return sorted(scored, key=lambda item: (-item.score, item.source))[:top_k]


def _tokenize(text: str) -> list[str]:
    return re.findall(r"[a-z0-9_]+", text.lower())


def _compact_text(text: str, *, max_chars: int = 900) -> str:
    compact = " ".join(text.split())
    if len(compact) <= max_chars:
        return compact
    return f"{compact[: max_chars - 3]}..."
