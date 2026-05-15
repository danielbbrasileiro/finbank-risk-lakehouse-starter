select
    customer_id,
    segment,
    state,
    internal_score,
    loan_count,
    total_principal_amount,
    total_outstanding_balance,
    max_days_past_due,
    avg_days_past_due,
    case
        when max_days_past_due >= 90 then 'DEFAULT_RISK'
        when max_days_past_due >= 30 then 'HIGH_RISK'
        when max_days_past_due > 0 then 'WATCHLIST'
        else 'PERFORMING'
    end as portfolio_status
from {{ ref('int_customer_credit_profile') }}
