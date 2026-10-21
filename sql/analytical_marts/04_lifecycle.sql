CREATE OR REPLACE TABLE mart.customer_lifecycle AS
WITH seq AS (
 SELECT *,row_number() OVER(PARTITION BY customer_key ORDER BY invoice_ts,invoice_no) order_sequence,
 lead(invoice_ts) OVER(PARTITION BY customer_key ORDER BY invoice_ts,invoice_no) next_order_ts
 FROM mart.fact_order
 WHERE customer_key <> 'UNKNOWN' AND date_key < cast(getvariable('cutoff') AS DATE)
)
SELECT customer_key,min(date_key) first_purchase_date,
 cast(date_trunc('month',min(date_key)) AS DATE) cohort_month,
 max(date_key) last_purchase_date,count(*) orders,sum(gross_pence) gross_pence,
 max(CASE WHEN order_sequence=1 THEN gross_pence END) first_order_pence,
 max(CASE WHEN order_sequence=1 THEN distinct_products END) first_order_breadth,
 max(CASE WHEN order_sequence=1 THEN country_key END) first_country,
 max(CASE WHEN order_sequence=1 THEN datediff('day',invoice_ts,next_order_ts) END) days_to_second_order,
 datediff('day',max(date_key),cast(getvariable('cutoff') AS DATE)) recency_days,
 min(date_key) >= cast(getvariable('warmup') AS DATE) after_warmup,
 min(date_key) + cast(getvariable('horizon') AS INTEGER) <= cast(getvariable('cutoff') AS DATE)-1 fully_observed_90d
FROM seq GROUP BY 1;

CREATE OR REPLACE TABLE mart.cohort_retention AS
WITH sizes AS (SELECT cohort_month,count(*) cohort_size FROM mart.customer_lifecycle GROUP BY 1),
 grid AS (
 SELECT s.*,age.month_age,
 cast(s.cohort_month + age.month_age * INTERVAL 1 MONTH AS DATE) activity_month
 FROM sizes s CROSS JOIN range(0,25) age(month_age)
 WHERE s.cohort_month + age.month_age * INTERVAL 1 MONTH < cast(getvariable('cutoff') AS DATE)
), active AS (
 SELECT c.cohort_month,cast(date_trunc('month',o.date_key) AS DATE) activity_month,
 count(DISTINCT o.customer_key) active_customers
 FROM mart.fact_order o JOIN mart.customer_lifecycle c USING(customer_key)
 WHERE o.date_key < cast(getvariable('cutoff') AS DATE) GROUP BY 1,2
)
SELECT g.*,coalesce(a.active_customers,0) active_customers,
 coalesce(a.active_customers,0)::DOUBLE/g.cohort_size retention_rate
FROM grid g LEFT JOIN active a USING(cohort_month,activity_month);

CREATE OR REPLACE TABLE mart.customer_segments AS
WITH scored AS (
 SELECT *,ntile(5) OVER(ORDER BY recency_days DESC,customer_key) r_score,
 ntile(5) OVER(ORDER BY orders,customer_key) f_score,
 ntile(5) OVER(ORDER BY gross_pence,customer_key) m_score
 FROM mart.customer_lifecycle
)
SELECT *,CASE WHEN orders>=5 AND recency_days<=90 THEN 'Established active'
 WHEN orders>=5 AND recency_days>90 THEN 'Established dormant'
 WHEN orders=1 AND recency_days<=90 THEN 'Recent first purchase'
 WHEN orders=1 THEN 'Single purchase dormant'
 ELSE 'Developing repeat' END segment
FROM scored;
