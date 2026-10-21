-- Leadership: compare Jan-Nov with identical calendar boundaries, exclude partial December.
SELECT year(date_key) calendar_year,
sum(CASE WHEN line_status='sale' THEN amount_pence ELSE 0 END)/100.0 gross_gbp,
sum(amount_pence)/100.0 net_gbp,
count(DISTINCT CASE WHEN line_status='sale' THEN invoice_no END) orders
FROM mart.v_complete_lines WHERE month(date_key)<=11 AND year(date_key) IN (2010,2011)
GROUP BY 1 ORDER BY 1;
