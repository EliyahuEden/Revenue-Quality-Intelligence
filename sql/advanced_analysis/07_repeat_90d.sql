-- CRM: compare equally observed first-purchase cohorts after a three-month warmup.
SELECT cohort_month,count(*) eligible_customers,
count(*) FILTER(WHERE days_to_second_order<=90) repeat_customers,
avg(CASE WHEN days_to_second_order<=90 THEN 1.0 ELSE 0 END) repeat_90d_rate
FROM mart.customer_lifecycle WHERE after_warmup AND fully_observed_90d
GROUP BY 1 ORDER BY 1;
