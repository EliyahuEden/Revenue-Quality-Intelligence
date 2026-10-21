-- Controller: all raw financial value remains visible even outside core merchandise.
SELECT line_status,count(*) row_count,sum(amount_pence)/100.0 signed_gbp,
count(*) FILTER(WHERE source_customer_id IS NULL) missing_customer_rows,
count(*) FILTER(WHERE description IS NULL) missing_description_rows
FROM staging.lines GROUP BY 1 ORDER BY row_count DESC;
