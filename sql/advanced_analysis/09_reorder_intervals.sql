-- CRM timing: LEAD creates inter-order intervals; conditional-on-repeat distribution.
WITH seq AS (SELECT customer_key,invoice_ts,
lead(invoice_ts) OVER(PARTITION BY customer_key ORDER BY invoice_ts,invoice_no) next_ts
FROM mart.fact_order WHERE customer_key<>'UNKNOWN' AND date_key<cast(getvariable('cutoff') AS DATE))
SELECT count(*) intervals,median(datediff('day',invoice_ts,next_ts)) median_days,
quantile_cont(datediff('day',invoice_ts,next_ts),.9) p90_days
FROM seq WHERE next_ts IS NOT NULL;
