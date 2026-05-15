select
    c.customer_id,
    c.segment,
    c.state,
    c.internal_score,
    count(l.loan_id) as loan_count,
    coalesce(sum(l.principal_amount), 0) as total_principal_amount,
    coalesce(sum(l.outstanding_balance), 0) as total_outstanding_balance,
    coalesce(max(l.days_past_due), 0) as max_days_past_due,
    coalesce(avg(l.days_past_due), 0) as avg_days_past_due,
    min(l.risk_rating) as best_risk_rating,
    max(l.risk_rating) as worst_risk_rating
from {{ ref('stg_customers') }} c
left join {{ ref('stg_loans') }} l
    on c.customer_id = l.customer_id
group by
    c.customer_id,
    c.segment,
    c.state,
    c.internal_score
