# Data quality and reconciliation

Contracts: 25/25 passed. Full-window diagnostics (core reporting stops before December 2011).

|Contract|Value|Expected|Pass|
|---|---:|---:|---|
|source_row_count|1067371.0|1067371|True|
|classification_conserves_rows|0.0|0|True|
|line_key_unique|0.0|0|True|
|overlap_rows_verified_by_multiset|0.0|0|True|
|no_invalid_source_timestamps|0.0|0|True|
|source_quantity_cast_loss|0.0|0|True|
|source_price_cast_loss|0.0|0|True|
|fact_reconciles_core|0.0|0|True|
|fact_grain_unique|0.0|0|True|
|dim_customer_referential_integrity|0.0|0|True|
|dim_product_referential_integrity|0.0|0|True|
|dim_country_referential_integrity|0.0|0|True|
|dim_date_referential_integrity|0.0|0|True|
|sale_sign_valid|0.0|0|True|
|cancellation_sign_valid|0.0|0|True|
|order_amount_reconciles|0.0|0|True|
|invoice_has_single_customer_country_date|0.0|0|True|
|cohort_rates_valid|0.0|0|True|
|cohort_age_zero_equals_size|0.0|0|True|
|future_cohort_cells_absent|0.0|0|True|
|no_unknown_lifecycle|0.0|0|True|
|dense_calendar_country_grain|0.0|0|True|
|monthly_bridge_agrees|0.0|0|True|
|raw_financial_bridge|0.0|0|True|
|source_vs_typed_pence|0.0|0|True|

## Observed anomalies

```json
{
  "invoice_timestamp_variants": 82,
  "superseded_overlap_rows": 22523,
  "max_invoice_timestamp_span_minutes": 9,
  "missing_customers": 243007,
  "missing_descriptions": 4382,
  "repeated_extra_rows": 12133,
  "unknown_countries": 0,
  "customer_country_changes": 14,
  "source_date_range": [
    "2009-12-01 07:45:00",
    "2011-12-09 12:50:00"
  ],
  "price_range": [
    "-53594.3600",
    "38970.0000"
  ],
  "quantity_range": [
    -80995,
    80995
  ],
  "stock_codes": 5131
}
```

|Classification|Rows|Signed GBP|
|---|---:|---:|
|sale|1,014,945|19,699,784.97|
|overlap_partition|22,523|377,488.45|
|cancellation|17,973|-719,656.34|
|zero_price|6,024|0.00|
|non_merchandise|5,901|88,309.61|
|negative_price|5|-158,676.14|

Policies: all physical rows retained in raw/staging. Missing identity maps to UNKNOWN and stays in financial totals, excluded from customer analyses. Verified overlapping partition copies are superseded after multiset validation. Within-partition exact repeats are retained because source has no reliable line key; deduplication is a labeled sensitivity. Zero/negative prices, non-merchandise codes, zero quantities and sign exceptions are excluded from core, visible in this bridge. Large valid wholesale lines remain. C-prefixed negative merchandise lines are cancellation postings, not proven returned goods. No country imputation; customer location stays on each transaction.
