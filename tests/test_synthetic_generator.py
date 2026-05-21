from src.python_ingestion.synthetic_generator import (
    make_accounts,
    make_customers,
    make_loans,
    make_transactions,
)


def test_synthetic_generator_produces_relational_banking_data() -> None:
    customers = make_customers(25)
    accounts = make_accounts(customers)
    transactions = make_transactions(accounts, 100)
    loans = make_loans(customers, 40)

    assert customers["customer_id"].is_unique
    assert accounts["customer_id"].isin(customers["customer_id"]).all()
    assert transactions["account_id"].isin(accounts["account_id"]).all()
    assert loans["customer_id"].isin(customers["customer_id"]).all()
    assert transactions["amount"].gt(0).all()
    assert loans["outstanding_balance"].ge(0).all()
