-- Account management: rank known customers and quantify revenue concentration.
WITH ranked AS (SELECT *,row_number() OVER(ORDER BY gross_pence DESC,customer_key) rn,
count(*) OVER() n,sum(gross_pence) OVER() total_gross FROM mart.customer_lifecycle)
SELECT *,sum(gross_pence) OVER(ORDER BY rn)::DOUBLE/total_gross cumulative_gross_share,
rn<=ceil(n*.1) in_top_decile FROM ranked ORDER BY rn;
