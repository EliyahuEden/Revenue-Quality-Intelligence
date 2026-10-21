-- Grain: one physical source row. Preserve repeated lines: no true line key exists.
CREATE OR REPLACE TABLE staging.lines AS
WITH coverage AS (
 SELECT source_sheet,min(cast(invoice_ts AS DATE)) min_date,max(cast(invoice_ts AS DATE)) max_date
 FROM raw.lines GROUP BY 1
), typed AS (
 SELECT line_id, source_sheet, source_row,
 trim(invoice_no) invoice_no, upper(trim(stock_code)) stock_code,
 nullif(trim(description),'') description,
 try_cast(quantity AS BIGINT) quantity,
 try_cast(invoice_ts AS TIMESTAMP) invoice_ts,
 try_cast(unit_price AS DECIMAL(18,4)) unit_price,
 nullif(regexp_replace(trim(source_customer_id),'\.0$',''),'') source_customer_id,
 coalesce(nullif(trim(country),''),'Unknown') country
 FROM raw.lines
), flagged AS (
 SELECT *, starts_with(upper(invoice_no),'C') is_cancel_invoice,
 regexp_full_match(stock_code,'[0-9]{5}[A-Z]*') is_merchandise,
 EXISTS(SELECT 1 FROM coverage newer JOIN coverage current_part ON current_part.source_sheet=t.source_sheet
        WHERE newer.min_date>current_part.min_date
        AND cast(t.invoice_ts AS DATE) BETWEEN newer.min_date AND newer.max_date) is_superseded_partition,
 count(*) OVER (PARTITION BY source_sheet,invoice_no,stock_code,description,quantity,invoice_ts,unit_price,source_customer_id,country) duplicate_group_size,
 row_number() OVER (PARTITION BY source_sheet,invoice_no,stock_code,description,quantity,invoice_ts,unit_price,source_customer_id,country ORDER BY line_id) duplicate_ordinal
 FROM typed t
)
SELECT *,
 CASE WHEN is_superseded_partition THEN 'overlap_partition'
      WHEN invoice_no IS NULL OR invoice_ts IS NULL OR quantity IS NULL OR unit_price IS NULL THEN 'invalid_type_or_key'
      WHEN unit_price < 0 THEN 'negative_price'
      WHEN unit_price = 0 THEN 'zero_price'
      WHEN quantity = 0 THEN 'zero_quantity'
      WHEN NOT is_merchandise THEN 'non_merchandise'
      WHEN is_cancel_invoice AND quantity < 0 THEN 'cancellation'
      WHEN NOT is_cancel_invoice AND quantity > 0 THEN 'sale'
      ELSE 'sign_exception' END line_status,
 cast(round(quantity * unit_price * 100,0) AS BIGINT) amount_pence,
 CASE WHEN source_customer_id IS NULL THEN 'UNKNOWN'
 ELSE substr(sha256('retail-portfolio-v1:' || source_customer_id),1,16) END customer_key
FROM flagged;
