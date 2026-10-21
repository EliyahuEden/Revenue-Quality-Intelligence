-- CRM: actual calendar inactivity gaps using LAG over distinct active months.
WITH active AS (SELECT DISTINCT customer_key,cast(date_trunc('month',date_key) AS DATE) month_start
FROM mart.fact_order WHERE customer_key<>'UNKNOWN' AND date_key<cast(getvariable('cutoff') AS DATE)),
seq AS (SELECT *,lag(month_start) OVER(PARTITION BY customer_key ORDER BY month_start) previous_month FROM active)
SELECT month_start,count(*) active_buyers,
count(*) FILTER(WHERE previous_month IS NULL) first_observed,
count(*) FILTER(WHERE datediff('month',previous_month,month_start)=1) consecutive_active,
count(*) FILTER(WHERE datediff('month',previous_month,month_start)>1) reactivated
FROM seq GROUP BY 1 ORDER BY 1;
