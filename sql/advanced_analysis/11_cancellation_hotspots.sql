-- Finance QA: value-based posting ratio; not a matched sale return rate.
WITH p AS (SELECT product_key,sum(CASE WHEN line_status='sale' THEN amount_pence ELSE 0 END) gross_pence,
-sum(CASE WHEN line_status='cancellation' THEN amount_pence ELSE 0 END) cancellation_pence,
count(*) FILTER(WHERE line_status='cancellation') cancellation_lines
FROM mart.v_complete_lines GROUP BY 1)
SELECT *,cancellation_pence::DOUBLE/nullif(gross_pence,0) cancellation_value_ratio
FROM p WHERE gross_pence>=100000 ORDER BY cancellation_pence DESC;
