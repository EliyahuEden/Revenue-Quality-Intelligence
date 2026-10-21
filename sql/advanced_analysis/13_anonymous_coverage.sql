-- Governance: quantify selection bias before making customer-level claims.
SELECT customer_key='UNKNOWN' anonymous,count(*) lines,
sum(CASE WHEN line_status='sale' THEN amount_pence ELSE 0 END)/100.0 gross_gbp
FROM mart.v_complete_lines GROUP BY 1;
