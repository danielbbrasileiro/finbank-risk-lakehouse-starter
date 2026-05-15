select
    transaction_id,
    customer_id,
    account_id,
    cast(transaction_date as date) as transaction_date,
    channel,
    transaction_type,
    cast(amount as numeric) as amount,
    cast(is_suspicious as boolean) as is_suspicious
from {{ source('raw', 'transactions') }}
