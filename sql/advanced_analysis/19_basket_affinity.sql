-- Merchandising: basket-level distinct presence avoids line fanout; top 40 products only.
WITH top_products AS (SELECT product_key FROM mart.v_complete_lines WHERE line_status='sale'
GROUP BY 1 ORDER BY count(*) DESC,product_key LIMIT 40),
b AS (SELECT DISTINCT invoice_no,product_key FROM mart.v_complete_lines
WHERE line_status='sale' AND product_key IN (SELECT product_key FROM top_products)),
freq AS (SELECT product_key,count(*) baskets FROM b GROUP BY 1),
pairs AS (SELECT a.product_key product_a,b.product_key product_b,count(*) pair_baskets
FROM b a JOIN b ON a.invoice_no=b.invoice_no AND a.product_key<b.product_key GROUP BY 1,2),
total AS (SELECT count(DISTINCT invoice_no)::DOUBLE n FROM mart.v_complete_lines WHERE line_status='sale')
SELECT p.*,p.pair_baskets/total.n support,p.pair_baskets::DOUBLE/fa.baskets confidence_a_to_b,
p.pair_baskets*total.n/(fa.baskets::DOUBLE*fb.baskets) lift
FROM pairs p JOIN freq fa ON p.product_a=fa.product_key JOIN freq fb ON p.product_b=fb.product_key
CROSS JOIN total WHERE pair_baskets>=50 ORDER BY lift DESC;
