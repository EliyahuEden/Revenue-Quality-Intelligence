-- Merchandising: rank gross contributors without inventing product categories.
WITH p AS (SELECT product_key,
sum(CASE WHEN line_status='sale' THEN amount_pence ELSE 0 END)/100.0 gross_gbp,
-sum(CASE WHEN line_status='cancellation' THEN amount_pence ELSE 0 END)/100.0 cancellation_gbp,
sum(amount_pence)/100.0 net_gbp FROM mart.v_complete_lines GROUP BY 1)
SELECT p.*,d.product_name,dense_rank() OVER(ORDER BY gross_gbp DESC) revenue_rank,
gross_gbp/sum(gross_gbp) OVER() gross_share FROM p JOIN mart.dim_product d USING(product_key)
ORDER BY gross_gbp DESC;
