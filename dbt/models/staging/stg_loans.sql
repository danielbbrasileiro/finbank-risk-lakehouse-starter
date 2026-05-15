select
    loan_id,
    customer_id,
    product_type,
    cast(origination_date as date) as origination_date,
    cast(maturity_date as date) as maturity_date,
    cast(principal_amount as numeric) as principal_amount,
    cast(outstanding_balance as numeric) as outstanding_balance,
    cast(interest_rate as numeric) as interest_rate,
    cast(days_past_due as integer) as days_past_due,
    risk_rating
from {{ source('raw', 'loans') }}
