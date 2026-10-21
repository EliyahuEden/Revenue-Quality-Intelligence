-- Merchandising: price variation may reflect quantity tiers, not price elasticity.
SELECT product_key,count(*) sale_lines,count(DISTINCT unit_price) price_points,
quantile_cont(unit_price,.1) p10_price,median(unit_price) median_price,
quantile_cont(unit_price,.9) p90_price
FROM mart.v_complete_lines WHERE line_status='sale' GROUP BY 1 HAVING count(*)>=100
ORDER BY price_points DESC;
