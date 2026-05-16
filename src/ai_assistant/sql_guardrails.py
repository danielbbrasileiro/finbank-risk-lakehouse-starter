from __future__ import annotations

import re


class SqlGuardrailError(ValueError):
    """Raised when generated SQL violates the assistant safety contract."""


_BLOCKED_KEYWORDS = {
    "alter",
    "call",
    "copy",
    "create",
    "delete",
    "drop",
    "execute",
    "grant",
    "insert",
    "merge",
    "revoke",
    "truncate",
    "update",
    "vacuum",
}


def build_guarded_query(
    sql: str,
    *,
    allowed_schemas: tuple[str, ...],
    default_limit: int = 500,
) -> str:
    """Validate a generated analytical SQL query and enforce a row limit."""
    query = _normalize_statement(sql)
    lowered = _without_string_literals(query).lower()

    if not lowered.startswith(("select ", "with ")):
        raise SqlGuardrailError("Only SELECT statements are allowed.")

    blocked = sorted(keyword for keyword in _BLOCKED_KEYWORDS if re.search(rf"\b{keyword}\b", lowered))
    if blocked:
        raise SqlGuardrailError(f"Blocked SQL keyword: {blocked[0]}")

    _validate_statement_count(query)
    _validate_schema_scope(lowered, allowed_schemas)

    return _enforce_limit(query, default_limit)


def _normalize_statement(sql: str) -> str:
    query = " ".join(sql.strip().split())
    if not query:
        raise SqlGuardrailError("SQL statement is empty.")
    return query[:-1].strip() if query.endswith(";") else query


def _without_string_literals(sql: str) -> str:
    return re.sub(r"'(?:''|[^'])*'", "''", sql)


def _validate_statement_count(query: str) -> None:
    statement_probe = _without_string_literals(query)
    if ";" in statement_probe:
        raise SqlGuardrailError("Only one SQL statement is allowed.")


def _validate_schema_scope(lowered_sql: str, allowed_schemas: tuple[str, ...]) -> None:
    allowed = {schema.lower() for schema in allowed_schemas}
    relation_matches = re.findall(r"\b(?:from|join)\s+([a-z_][\w]*)\.([a-z_][\w]*)\b", lowered_sql)
    if not relation_matches:
        raise SqlGuardrailError("Query must reference an allowlisted schema-qualified table.")

    schemas = {schema for schema, _table in relation_matches}
    out_of_scope = sorted(schema for schema in schemas if schema not in allowed)
    if out_of_scope:
        raise SqlGuardrailError(f"Schema is not allowlisted: {out_of_scope[0]}")


def _enforce_limit(query: str, default_limit: int) -> str:
    limit_match = re.search(r"\blimit\s+(\d+)\s*$", query, flags=re.IGNORECASE)
    if not limit_match:
        return f"{query} limit {default_limit}"

    requested_limit = int(limit_match.group(1))
    if requested_limit <= default_limit:
        return query

    return re.sub(r"\blimit\s+\d+\s*$", f"limit {default_limit}", query, flags=re.IGNORECASE)
