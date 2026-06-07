select
    audit_timestamp,
    status,
    question,
    citations,
    guarded_sql,
    response
from {{ ref('stg_ai_copilot_audit') }}
