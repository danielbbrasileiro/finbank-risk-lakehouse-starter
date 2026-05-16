from __future__ import annotations

import sys
from argparse import ArgumentParser
from dataclasses import dataclass
from pathlib import Path

import yaml

from src.ai_assistant.governed_copilot import answer_question


@dataclass(frozen=True)
class EvalCaseResult:
    case_id: str
    passed: bool
    details: str


@dataclass(frozen=True)
class EvalSummary:
    total: int
    passed: int
    failed: int
    results: list[EvalCaseResult]


def run_eval_file(eval_file: Path, *, corpus_paths: list[Path] | None = None) -> EvalSummary:
    payload = yaml.safe_load(eval_file.read_text(encoding="utf-8")) or {}
    results: list[EvalCaseResult] = []

    for case in payload.get("cases", []):
        result = _run_case(case, corpus_paths=corpus_paths)
        results.append(result)

    passed = sum(1 for result in results if result.passed)
    return EvalSummary(total=len(results), passed=passed, failed=len(results) - passed, results=results)


def _run_case(case: dict, *, corpus_paths: list[Path] | None) -> EvalCaseResult:
    case_id = str(case["id"])
    answer = answer_question(str(case["question"]), corpus_paths=corpus_paths)
    answer_text = f"{answer.response}\n{answer.guarded_sql or ''}".lower()

    missing_terms = [
        term for term in case.get("expected_terms", [])
        if str(term).lower() not in answer_text
    ]
    requires_sql = bool(case.get("requires_sql", False))
    sql_state_ok = answer.guarded_sql is not None if requires_sql else True

    if missing_terms:
        return EvalCaseResult(case_id=case_id, passed=False, details=f"Missing terms: {missing_terms}")
    if not sql_state_ok:
        return EvalCaseResult(case_id=case_id, passed=False, details="Expected guarded SQL, got none")
    return EvalCaseResult(case_id=case_id, passed=True, details="ok")


def main(argv: list[str] | None = None) -> int:
    parser = ArgumentParser(description="Run deterministic evals for the FinBank governed copilot.")
    parser.add_argument("--eval-file", default="ai/evals/risk_copilot.yml")
    parser.add_argument("--corpus-path", action="append", default=["docs", "dbt/models", "schemas"])
    args = parser.parse_args(argv)

    summary = run_eval_file(Path(args.eval_file), corpus_paths=[Path(path) for path in args.corpus_path])
    for result in summary.results:
        status = "PASS" if result.passed else "FAIL"
        print(f"{status} {result.case_id}: {result.details}")
    print(f"Summary: {summary.passed}/{summary.total} passed")
    return 0 if summary.failed == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
