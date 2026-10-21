-- CRM: revenue per known active buyer and new/repeat contribution at invoice time.
SELECT cast(date_trunc('month',o.date_key) AS DATE) month_start,
CASE WHEN cast(date_trunc('month',o.date_key) AS DATE)=c.cohort_month THEN 'First observed month' ELSE 'Later month' END lifecycle,
count(DISTINCT o.customer_key) buyers,count(*) orders,sum(o.gross_pence)/100.0 gross_gbp
FROM mart.fact_order o JOIN mart.customer_lifecycle c USING(customer_key)
WHERE o.date_key<cast(getvariable('cutoff') AS DATE) GROUP BY 1,2 ORDER BY 1,2;
