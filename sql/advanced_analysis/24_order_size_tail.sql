-- Operations: distinguish wholesale bulk orders and high-value outliers without deleting them.
SELECT count(*) orders,median(gross_pence)/100.0 median_order_gbp,
quantile_cont(gross_pence,.9)/100.0 p90_order_gbp,
quantile_cont(gross_pence,.99)/100.0 p99_order_gbp,max(gross_pence)/100.0 max_order_gbp,
median(distinct_products) median_products FROM mart.fact_order
WHERE date_key<cast(getvariable('cutoff') AS DATE);
