# Business assignment: protect revenue quality and customer continuity

This is an independent historical case study of the UK giftware retailer described by UCI. Leadership/stakeholder roles below are an analytical scenario, not evidence of employment, a real consulting engagement or actual management actions.

The retailer sells goods online to customers in multiple countries, including wholesalers. The commercial challenge is to understand growth while separating positive merchandise sales from cancellation postings, measuring repeat purchasing fairly and identifying account/assortment concentrations.

|Stakeholder|Decision|Evidence / KPI|
|---|---|---|
|Finance lead|Approve a common gross-to-net definition and exception policy|Gross sales, cancellation postings, net merchandise value, exclusions bridge|
|Commercial lead|Prioritize account research and base-market service|Known-customer concentration, market mix, account dormancy|
|CRM lead|Define follow-up windows and design a future intervention|Mature 90-day repeat rate, interval distribution, cohort retention|
|Merchandising lead|Review assortment and cancellation hotspots|SKU concentration, price dispersion, basket affinity|
|Data/BI lead|Approve reliable self-service reports|Identity coverage, key integrity, lineage, duplicate sensitivity|

## Questions connected to decisions

|#|Question|Decision|Analysis files|
|---:|---|---|---|
|1|How much does cancellation posting value separate gross from net?|Report both values to finance|01, 21|
|2|Is Januaryâ€“November growth supported by equal windows?|Approve like-for-like reporting|02, 16|
|3|Which calendar periods warrant investigation?|Triage retrospective exceptions|03, 20|
|4|Which countries drive sales and cancellation burden?|Prioritize operational market review|04|
|5|How concentrated are identified customer purchases?|Review high-value account service|05|
|6|Which dormant customer types deserve different research?|Separate onboarding from reactivation|06|
|7|What is repeat purchasing within a fully observed 90 days?|Set a credible baseline before testing CRM|07, 22|
|8|How does active purchase retention differ by cohort age?|Avoid immature-cohort comparisons|08|
|9|What intervals characterize customers who do repeat?|Investigate useful follow-up timing|09|
|10|Which products dominate gross/net value and cancellations?|Investigate SKU correction/assortment issues|10, 11|
|11|Can cancellation postings be connected to prior history?|Request original-invoice references|12|
|12|How much financial activity cannot be attributed to customers?|Prioritize source identity quality|13|
|13|How sensitive are totals to deduplication policy?|Approve a line-key contract|14|
|14|Does first-basket breadth associate with repeat purchasing?|Develop an intervention hypothesis|17|
|15|Which products co-occur more often than expected?|Research candidate bundles, then test|19|

Hypotheses are exploratory: customer concentration may reflect wholesale demand; first-basket breadth may proxy intent; large cancellations may reflect corrections; geography may reflect distribution reach. The dataset can identify patterns and prioritize investigation, but cannot verify these mechanisms or measure the effect of recommendations.

Deliverables: tested SQL/Python warehouse, audit bridge, 24 decision-oriented analyses, 10 evidence-linked findings, a five-page native Power BI report and reproducible setup. No campaign ROI, profit, CAC or full lifetime value is estimated.
