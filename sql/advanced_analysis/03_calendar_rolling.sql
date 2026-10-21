-- Operations: 28 calendar-day average and cumulative sales, with zero-sale days.
WITH daily AS (SELECT date_key,sum(net_pence)/100.0 net_gbp FROM mart.daily_country GROUP BY 1)
SELECT *,avg(net_gbp) OVER(ORDER BY date_key ROWS BETWEEN 27 PRECEDING AND CURRENT ROW) rolling_28d,
sum(net_gbp) OVER(ORDER BY date_key) cumulative_net FROM daily ORDER BY date_key;
