# Executive analytical findings

Historical case study; observational results, not achieved employer impact. Reporting window: 1 December 2009–30 November 2011. Source through 9 December 2011 is retained for audit; incomplete December is excluded from headline analyses. Monetary figures are nominal GBP.

## 1. Gross sales need a cancellation bridge

**Observed:** Complete-month merchandise gross is £19,084,294.99; cancellation postings total £545,529.58 (2.86% of gross), leaving £18,538,765.41 net merchandise value.

**Evidence:** `01_executive_bridge; 21_quality_reconciliation` in `reports/query_results/` unless stated otherwise.

**Decision:** Finance should review the gross-to-net bridge monthly and reconcile exclusions against the ledger.

**Possible explanation:** Wholesale order corrections or reversals may explain part of the cancellation value.

**Limits:** Cancellation posting dates do not establish the original sale or physical returns. Net merchandise value is not accounting-recognized revenue or profit.

**Success measure:** Reconciliation difference in pence; cancellation-value ratio and documented exceptions.

## 2. Comparable periods change the growth discussion

**Observed:** January–November net merchandise value changes from £8,406,439.65 in 2010 to £8,590,689.43 in 2011 (+2.19%). Orders change from 18,077 to 17,407.

**Evidence:** `16_comparable_year_bridge; 02_monthly_growth` in `reports/query_results/` unless stated otherwise.

**Decision:** Use equal January–November windows for the management growth comparison.

**Possible explanation:** Order mix, volume and cancellation timing may contribute.

**Limits:** Only two historical annual cycles; no inflation adjustment, causal attribution or full December 2011.

**Success measure:** Comparable-window net value, orders and AOV, reviewed together.

## 3. Unidentified transactions limit CRM coverage

**Observed:** Anonymous merchandise sales contribute £2,472,599.19, or 12.96% of gross sales, while remaining included in finance KPIs.

**Evidence:** `13_anonymous_coverage` in `reports/query_results/` unless stated otherwise.

**Decision:** Audit checkout/customer capture and keep an explicit unknown bucket in financial reports.

**Possible explanation:** Guest orders or operational data capture practices may explain missing IDs.

**Limits:** Missingness may be non-random. Known-customer retention cannot describe anonymous buyers.

**Success measure:** Share of gross sales linked to a stable customer ID; no retrospective fabricated IDs.

## 4. Known-customer revenue is concentrated

**Observed:** The top 10% of 5,824 known buyers by observed gross sales generate 63.46% of known-customer gross sales.

**Evidence:** `05_customer_pareto` in `reports/query_results/` unless stated otherwise.

**Decision:** Prioritize a review of high-value account continuity and service needs.

**Possible explanation:** The publisher notes many wholesale customers, which may create a long value tail.

**Limits:** Ranked over the full observed period; this is a retrospective concentration measure and not a future targeting score.

**Success measure:** Revenue concentration and repeat-order continuity among approved account segments.

## 5. Repeat purchase has an explicit observation window

**Observed:** 1,458 of 3,533 eligible known buyers place a second order within 90 days (41.27%); eligibility begins March 2010 and requires 90 fully observed days before December 2011.

**Evidence:** `07_repeat_90d; 22_cohort_maturity` in `reports/query_results/` unless stated otherwise.

**Decision:** Use the mature 90-day rate as a CRM baseline; design a randomized outreach test only after obtaining consent and treatment data.

**Possible explanation:** Ordering cadence, customer type and assortment needs may explain non-repeat purchases.

**Limits:** First observed purchase may not be first-ever purchase. Warmup reduces but cannot remove left censoring. Non-repeat is not contractual churn.

**Success measure:** Pre-registered 90-day repeat rate, revenue/customer and cancellation guardrail in a future randomized test.

## 6. First-basket breadth is a useful research hypothesis

**Observed:** Month-standardized 90-day repeat-rate difference for 6+ first-order SKUs versus 1–5 SKUs is +11.33 percentage points (19 common cohorts). Descriptive 95% interval: +6.79 to +15.88 points.

**Evidence:** `17_first_basket_repeat; repeat_purchase_statistics.csv; statistical_method.json` in `reports/query_results/` unless stated otherwise.

**Decision:** Research whether basket breadth identifies different customer needs before testing recommendations or bundles.

**Possible explanation:** Wholesale intent or existing familiarity may influence both breadth and repeat buying.

**Limits:** Observational association, adjusted only for calendar cohort; not evidence that increasing basket breadth causes retention.

**Success measure:** Future randomized bundle experiment: repeat purchase, basket value and cancellation guardrails.

## 7. Dormancy contains distinct commercial cases

**Observed:** 1,263 buyers are single-purchase dormant; 536 are established dormant (at least five orders, last purchase over 90 days before cutoff), with £1,727,506.63 historical gross purchases.

**Evidence:** `06_segments` in `reports/query_results/` unless stated otherwise.

**Decision:** Separate first-purchase onboarding research from established-account reactivation review.

**Possible explanation:** Established buyers may pause seasonally; single purchasers may have one-time needs.

**Limits:** Segments are an as-of snapshot at 1 December 2011. Historical purchases are not recoverable revenue or forecast exposure.

**Success measure:** Subsequent repeat rate by preassigned segment in newly collected data.

## 8. Geography has a dominant base market

**Observed:** The United Kingdom contributes £16,282,882.08, or 85.32% of gross merchandise sales, across 35,440 sale invoices.

**Evidence:** `04_country_mix` in `reports/query_results/` unless stated otherwise.

**Decision:** Protect service quality in the base market; evaluate expansion with market-specific commercial costs.

**Possible explanation:** Retailer location and historical distribution relationships may drive this mix.

**Limits:** No acquisition, delivery costs or market-size denominator; this cannot establish geographic profitability or addressable market.

**Success measure:** Market gross/net value and cancellation ratio, with delivery and margin data added before investment.

## 9. Separate proven partition overlap from ambiguous line repeats

**Observed:** The two sheets repeat 22,523 rows over 1–9 December 2010; an eight-field multiset check verifies equal records and multiplicities, so the later partition is authoritative. Separately, removing 11,511 repeated core lines within authoritative partitions changes net merchandise value by £52,895.50 as a sensitivity.

**Evidence:** `14_duplicate_sensitivity` in `reports/query_results/` unless stated otherwise.

**Decision:** Request source-system line identifiers and retain the current auditable baseline until duplication is confirmed.

**Possible explanation:** Repeated identical lines could be duplicate ingestion or valid repeated invoice lines.

**Limits:** Partition overlap is verified and excluded from core. Remaining within-partition repeats lack a trustworthy line key; removing those is a scenario, not a verified correction.

**Success measure:** Duplicate key failures on future loads; finance reconciliation under an approved policy.

## 10. Cancellation history is incomplete evidence

**Observed:** 2,224 identified cancellation lines have no earlier sale with the same customer, SKU and price in the observed history, totaling £44,099.29.

**Evidence:** `12_cancellation_history_coverage` in `reports/query_results/` unless stated otherwise.

**Decision:** Investigate unmatched cancellations and obtain original-invoice references before calculating matched return rates.

**Possible explanation:** Pre-history sales, corrections, price changes or identifier errors may explain gaps.

**Limits:** An earlier matching-price sale also does not prove a match; quantities and original documents are not allocated.

**Success measure:** Share of cancellation value linked to a verified original invoice and approved reason.
