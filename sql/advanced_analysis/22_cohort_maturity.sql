-- Governance: expose censoring exclusions rather than calling unobserved buyers churned.
SELECT after_warmup,fully_observed_90d,count(*) customers,sum(gross_pence)/100.0 gross_gbp
FROM mart.customer_lifecycle GROUP BY 1,2 ORDER BY 1,2;
