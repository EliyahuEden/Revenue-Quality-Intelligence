-- CRM: allocate capacity using transparent lifecycle rules, not opaque clusters.
SELECT segment,count(*) customers,sum(gross_pence)/100.0 gross_gbp,avg(orders) avg_orders,
avg(recency_days) avg_recency FROM mart.customer_segments GROUP BY 1 ORDER BY gross_gbp DESC;
