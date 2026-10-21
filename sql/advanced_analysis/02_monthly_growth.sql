-- Leadership: separate monthly growth, comparable prior-year growth and seasonality.
WITH x AS (SELECT *,lag(net_pence) OVER(ORDER BY month_start) prev_month,
lag(net_pence,12) OVER(ORDER BY month_start) prev_year FROM mart.monthly_performance)
SELECT *,net_pence/nullif(prev_month,0)::DOUBLE-1 mom_growth,
net_pence/nullif(prev_year,0)::DOUBLE-1 yoy_growth FROM x ORDER BY month_start;
