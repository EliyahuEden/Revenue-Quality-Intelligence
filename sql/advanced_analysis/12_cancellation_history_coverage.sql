-- Reconciliation coverage diagnostic only: existence is not exact return attribution.
WITH c AS (SELECT *,EXISTS(SELECT 1 FROM mart.fact_invoice_line s WHERE s.line_status='sale'
AND s.customer_key=c.customer_key AND s.product_key=c.product_key AND s.unit_price=c.unit_price
AND s.invoice_ts<c.invoice_ts) prior_sale_exists
FROM mart.v_complete_lines c WHERE line_status='cancellation' AND customer_key<>'UNKNOWN')
SELECT prior_sale_exists,count(*) cancellation_lines,-sum(amount_pence)/100.0 cancellation_gbp
FROM c GROUP BY 1;
