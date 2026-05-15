# Data dictionary

## customers

| Column | Description |
|---|---|
| customer_id | Synthetic customer unique identifier |
| customer_name | Synthetic name or company name |
| document_type | CPF or CNPJ synthetic flag |
| segment | Customer segment |
| state | Brazilian state |
| internal_score | Synthetic internal risk score |

## transactions

| Column | Description |
|---|---|
| transaction_id | Unique transaction identifier |
| customer_id | Related customer |
| account_id | Related account |
| transaction_date | Transaction date |
| channel | PIX, CARD, ATM, BRANCH, TED or APP |
| transaction_type | Debit, credit, transfer, payment or withdrawal |
| amount | Transaction amount |
| is_suspicious | Synthetic suspicious transaction flag |

## loans

| Column | Description |
|---|---|
| loan_id | Unique loan identifier |
| customer_id | Related customer |
| product_type | Loan product |
| principal_amount | Original loan principal |
| outstanding_balance | Current exposure |
| days_past_due | Days past due |
| risk_rating | Synthetic risk rating |
