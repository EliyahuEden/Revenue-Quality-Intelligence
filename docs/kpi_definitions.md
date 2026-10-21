# KPI contract

Primary time window: **2009-12-01 inclusive to 2011-12-01 exclusive**. The raw audit includes all source records through 2011-12-09. Currency is nominal GBP. All line values round `quantity × DECIMAL unit price × 100` to integer pence; no binary floating-point accumulation defines finance totals. Sources contain invoice records, not cash settlement or an audited revenue ledger.

|KPI|Numerator / denominator|Scope / caution|
|---|---|---|
|Gross merchandise sales|Sum amount_pence of sale lines /100|Positive units, positive price, merchandise code, non-C invoice; includes unidentified customers|
|Cancellation postings|Negative sum amount_pence of cancellation lines /100|Negative units, positive price, merchandise code, C-prefixed invoice; reported as positive reduction|
|Net merchandise value|Gross − cancellation postings|Proxy from postings, not IFRS revenue or profit|
|Cancellation value ratio|Cancellation GBP / gross GBP|Posting-period ratio; not a matched return/customer probability; can exceed 100%|
|Sale invoices|Distinct sale invoice numbers in context|An invoice with several selected products counts once; single customer/country/calendar date contract checked. Order time is earliest line timestamp; source has 82 multi-timestamp invoices, maximum 9-minute span.|
|Gross AOV|Gross GBP / sale invoices|Under product filters, selected-product sales per invoice containing selected products, not whole-basket AOV|
|Known buyers|Distinct non-UNKNOWN sale customers|Before cutoff; customer analyses exclude anonymous activity|
|Anonymous gross share|Gross of UNKNOWN / all-customer gross|DAX intentionally removes customer filter for denominator; country/date/product context retained|
|Top-decile concentration|Known-customer gross of top ceil(10%×N) buyers / known-customer gross|Retrospective full-window ranking; ties split deterministically, no future targeting claim|
|90-day repeat purchase|Eligible customers with a second order within 90 calendar-day boundaries / eligible customers|First observed purchase >=2010-03-01; first date +90 <=2011-11-30; null second order means no observed repeat. Same-day distinct invoice can qualify. Day-based, not exact 2,160-hour elapsed duration.|
|Monthly purchase retention|Distinct cohort buyers purchasing at age m / full cohort size|Monthly activity, not consecutive retention/survival; a buyer may reactivate. Future cells omitted, observed inactive cells zero.|
|Recency|Days from last purchase date to 2011-12-01|Fixed snapshot; executive date filters must not recompute it implicitly|
|Established dormant|>=5 orders and recency>90 days|Transparent analyst threshold, not a verified churn label|
|RFM quintiles|NTILE(5) ranks over recency/frequency/gross|Equal-size bins split ties by key. Used for exploration; headline segment uses explicit rules.|
|Duplicate sensitivity|Retained core net − deduplication-scenario core net|After verified partition-overlap removal, exact equality across original eight fields within the same partition defines repeat groups. Remaining-line policy sensitivity, not confirmed error correction.|
|Basket lift|Pair baskets × all baskets / (A baskets × B baskets)|Distinct invoice/SKU presence, top 40 frequent SKUs and >=50 pair support; hypothesis generation, not incremental sales proof|
|Robust daily exception score|0.6745×(net−median)/MAD|Full-history retrospective screen, threshold abs(z)>5; no live detector evaluation and seasonal confounding remains|

Country stays on transactions because an observed customer can have more than one country. No synthetic customer-country overwrite or unreliable SCD history is introduced. Product names use the latest observed description for display; price remains on each fact row. No campaign attribution, funnel conversion, profit, CAC, subscription churn, predictive LTV or achieved intervention uplift can be measured here.
