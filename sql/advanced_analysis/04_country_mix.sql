-- Expansion: prioritize large markets and investigate cancellation burden.
SELECT country_key,sum(CASE WHEN line_status='sale' THEN amount_pence ELSE 0 END)/100.0 gross_gbp,
sum(amount_pence)/100.0 net_gbp,
-sum(CASE WHEN line_status='cancellation' THEN amount_pence ELSE 0 END)::DOUBLE/
nullif(sum(CASE WHEN line_status='sale' THEN amount_pence ELSE 0 END),0) cancellation_value_ratio,
count(DISTINCT CASE WHEN line_status='sale' THEN invoice_no END) orders
FROM mart.v_complete_lines GROUP BY 1 ORDER BY net_gbp DESC;
