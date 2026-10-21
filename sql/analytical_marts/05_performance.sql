-- Dense day/country scaffold makes ROWS windows calendar-correct even on zero-sales days.
CREATE OR REPLACE TABLE mart.daily_country AS
WITH totals AS (
 SELECT date_key,country_key,
 sum(CASE WHEN line_status='sale' THEN amount_pence ELSE 0 END) gross_pence,
 -sum(CASE WHEN line_status='cancellation' THEN amount_pence ELSE 0 END) cancellation_pence,
 sum(amount_pence) net_pence,
 count(DISTINCT CASE WHEN line_status='sale' THEN invoice_no END) orders
 FROM mart.v_complete_lines GROUP BY 1,2
)
SELECT d.date_key,c.country_key,coalesce(t.gross_pence,0) gross_pence,
 coalesce(t.cancellation_pence,0) cancellation_pence,
 coalesce(t.net_pence,0) net_pence,coalesce(t.orders,0) orders
FROM mart.dim_date d CROSS JOIN mart.dim_country c
LEFT JOIN totals t USING(date_key,country_key)
WHERE d.is_complete_period;

CREATE OR REPLACE TABLE mart.monthly_performance AS
SELECT cast(date_trunc('month',date_key) AS DATE) month_start,
 sum(gross_pence) gross_pence,sum(cancellation_pence) cancellation_pence,
 sum(net_pence) net_pence,sum(orders) orders,
 sum(gross_pence)::DOUBLE/nullif(sum(orders),0)/100 aov_gbp
FROM mart.daily_country GROUP BY 1;
