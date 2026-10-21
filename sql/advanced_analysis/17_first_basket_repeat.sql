-- Hypothesis: first basket breadth is associated with repeat, not a causal driver.
SELECT CASE WHEN first_order_breadth=1 THEN '1 SKU' WHEN first_order_breadth<=5 THEN '2-5 SKUs' ELSE '6+ SKUs' END breadth_group,
count(*) eligible_customers,count(*) FILTER(WHERE days_to_second_order<=90) repeat_customers,
avg(CASE WHEN days_to_second_order<=90 THEN 1.0 ELSE 0 END) repeat_90d_rate
FROM mart.customer_lifecycle WHERE after_warmup AND fully_observed_90d GROUP BY 1 ORDER BY 1;
