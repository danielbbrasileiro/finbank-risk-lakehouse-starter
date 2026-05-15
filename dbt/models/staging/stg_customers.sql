select
    customer_id,
    customer_name,
    document_type,
    segment,
    state,
    cast(created_at as date) as created_at,
    cast(internal_score as integer) as internal_score
from {{ source('raw', 'customers') }}
