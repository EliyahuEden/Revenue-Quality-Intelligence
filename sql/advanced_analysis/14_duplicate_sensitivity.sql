-- Governance: preserve source rows; compare deduplication as a sensitivity scenario.
SELECT sum(amount_pence)/100.0 retained_net_gbp,
sum(CASE WHEN duplicate_ordinal=1 THEN amount_pence ELSE 0 END)/100.0 deduplicated_net_gbp,
count(*) FILTER(WHERE duplicate_ordinal>1) repeated_rows
FROM mart.v_complete_lines;
