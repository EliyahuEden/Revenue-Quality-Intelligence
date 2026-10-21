-- CFO: reconcile merchandise gross, cancellation postings and net; no profit claim.
SELECT count(*) lines, sum(CASE WHEN line_status='sale' THEN amount_pence ELSE 0 END)/100.0 gross_gbp,
-sum(CASE WHEN line_status='cancellation' THEN amount_pence ELSE 0 END)/100.0 cancellation_gbp,
sum(amount_pence)/100.0 net_gbp,
count(DISTINCT CASE WHEN line_status='sale' THEN invoice_no END) orders,
count(DISTINCT CASE WHEN line_status='sale' AND customer_key<>'UNKNOWN' THEN customer_key END) known_buyers
FROM mart.v_complete_lines;
