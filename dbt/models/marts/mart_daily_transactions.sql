select
    transaction_date,
    channel,
    transaction_type,
    count(*) as transaction_count,
    sum(amount) as total_amount,
    avg(amount) as avg_amount,
    sum(case when is_suspicious then 1 else 0 end) as suspicious_count
from {{ ref('stg_transactions') }}
group by
    transaction_date,
    channel,
    transaction_type
