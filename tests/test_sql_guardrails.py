import pytest

from src.ai_assistant.sql_guardrails import SqlGuardrailError, build_guarded_query


def test_appends_default_limit_to_allowed_select() -> None:
    sql = "select customer_id, total_outstanding_balance from analytics_marts.mart_customer_exposure"

    guarded = build_guarded_query(sql, allowed_schemas=("analytics_marts",), default_limit=100)

    assert guarded == (
        "select customer_id, total_outstanding_balance "
        "from analytics_marts.mart_customer_exposure limit 100"
    )


def test_preserves_existing_limit_when_it_is_more_restrictive() -> None:
    sql = "select * from analytics_marts.mart_daily_transactions limit 25"

    guarded = build_guarded_query(sql, allowed_schemas=("analytics_marts",), default_limit=100)

    assert guarded == "select * from analytics_marts.mart_daily_transactions limit 25"


def test_caps_existing_limit_when_it_is_too_large() -> None:
    sql = "select * from analytics_marts.mart_daily_transactions limit 10000"

    guarded = build_guarded_query(sql, allowed_schemas=("analytics_marts",), default_limit=500)

    assert guarded == "select * from analytics_marts.mart_daily_transactions limit 500"


@pytest.mark.parametrize(
    "sql",
    [
        "delete from analytics_marts.mart_customer_exposure",
        "select * from analytics_marts.mart_customer_exposure; drop table raw.customers",
        "insert into analytics_marts.mart_customer_exposure values (1)",
        "select * from raw.customers",
    ],
)
def test_rejects_unsafe_or_out_of_scope_sql(sql: str) -> None:
    with pytest.raises(SqlGuardrailError):
        build_guarded_query(sql, allowed_schemas=("analytics_marts",), default_limit=100)
