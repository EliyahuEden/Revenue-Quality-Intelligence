# Retail management dashboard: research, data fit and design decisions

Prepared 22 October 2026. This document records the reasoning behind the revised native Power BI report. It distinguishes published guidance, our design choices and observations from the historical dataset. The assumed users are a commercial manager, a finance manager and a CRM/account manager; no interviews with this retailer's managers have been conducted.

## What a manager should be able to decide

A useful management report connects a business question to a comparison, the largest contributors and a next investigation. A headline value alone does not establish whether performance is good. This dataset has no budget, margin or agreed targets, so the report evaluates direction against the same months last year and exposes risks; it does not invent an overall health score.

| Management question | Evidence available here | Report response | Appropriate next step |
|---|---|---|---|
| Is sales value growing, and is purchasing activity supporting it? | Invoice dates, distinct invoices, quantities and prices, cancellation postings | Net value, invoice count, gross value per invoice and cancellation ratio, all with an equal-period comparison | Investigate which accounts, markets and products explain the difference |
| What numerically explains the change? | The same financial components in both periods | An exact three-part decomposition of net-value change | Separate invoice-volume concerns from changes in average invoice value and cancellation postings |
| Which markets matter to growth? | Customer-country field and transaction values | Largest absolute market movements across the full country dimension; accompanying current value and growth | Review material declines and understand large gains before allocating resources |
| How dependent are we on a small customer base? | Stable IDs for identified buyers and historical gross purchases | Top-decile share, cumulative concentration curve, value by customer segment | Review continuity and service needs of important accounts |
| Which inactive customers deserve account research? | Historical invoice counts, last-purchase dates and gross purchases | Established dormant buyer count and their past gross value | Investigate circumstances and seasonality before deciding on outreach |
| Do first-observed customer groups buy again? | Identified purchase history and sufficiently long observation windows | Mature 90-day repeat rate, monthly cohort grid and comparable fully observed 2011 cohort rates | Investigate onboarding and customer-type differences; evaluate interventions with new treatment data |
| Which products improved or deteriorated? | SKU-level sales and cancellation postings in both periods | Largest monetary gains and declines, with both years and sales-history status on hover | Review assortment, availability and customer demand before making changes |
| Where should finance investigate cancellation exposure? | Negative merchandise postings with dates, values and product codes | Monthly posting values and the largest cancellation-value products across the whole assortment | Obtain original-invoice links, reasons and operational explanations |

These decisions are our application of the research to the available data, not claims that every organization wants an identical dashboard.

## Research used and how it changed the build

**1. Microsoft: dashboard design.** Its guidance starts with audience and decisions, gives headline metrics context, recommends a single-screen overview, consistent periods and purposeful chart choices. Application: four comparative cards above charts; one period statement per management page; no decorative gauges without real targets. [Source](https://learn.microsoft.com/en-us/power-bi/create-reports/service-dashboards-design-tips)

**2. Microsoft: Retail Analysis sample.** The official example compares current and prior-year performance and explores variance by time and business dimension. Application: the report now moves from executive direction to market and product contributors. Our data does not include the example's stores, districts or margin fields, so those measures are not imitated. [Source](https://learn.microsoft.com/en-us/power-bi/create-reports/sample-retail-analysis)

**3. Tableau Blueprint: visual best practices.** It emphasizes a clear purpose, meaningful context and predictable interaction. Application: question-led page titles, informative chart headings, explicit units and denominators, market selectors and supporting hover detail. Headline conclusions remain visible without hovering. Lines show monthly trends; signed bars show gains and declines; a shaded grid shows purchasing across cohort age. [Source](https://help.tableau.com/current/blueprint/en-gb/bp_visual_best_practices.htm)

**4. Tableau: effective dashboards.** It recommends limiting views and using color to enhance analysis. Application: each detailed page has two main analytical views rather than many small charts; the overview uses four views because it must cover direction, drivers, markets and cancellation pressure together. The consistent theme is forest green, cream and restrained orange. [Source](https://www.tableau.com/blog/best-practices-for-building-effective-dashboards)

**5. Shopify: customer reports.** Its documented customer analysis includes order history, repeat customers, cohorts and RFM-related views. Application: separate customer-value concentration from repeat-purchase analysis, and retain explicit observation windows. Our definitions are those documented for this source, not assumed to reproduce Shopify's reports. [Source](https://help.shopify.com/en/manual/reports-and-analytics/shopify-reports/report-types/default-reports/customers-reports)

**6. Shopify: sales reports.** Its glossary distinguishes gross sales, sales reversals, net sales and gross profit. Application: clearly distinguish positive merchandise sales, cancellation postings and net merchandise value. We do not rename every cancellation a product return, and we do not present net value as profit. Average invoice value here is gross merchandise sales divided by distinct sale invoices. [Source](https://help.shopify.com/en/manual/reports-and-analytics/shopify-reports/report-types/default-reports/sales-report)

**7. Salesforce: sales reporting glossary.** It treats order count, units and average order value as distinct quantities and separately defines financial deductions. Application: cards say “sales invoices” and “gross value per invoice”; a million source lines is not described as a million orders. [Source](https://help.salesforce.com/s/articleView?id=commerce.rt_cms_reports_sales_reporting_glossary.htm&language=en_US&type=5)

**8. ONS: retail sales value and volume.** Official retail reporting distinguishes value from volume. Application: we do not interpret higher money per invoice as proof of a price increase or stronger physical demand. Product mix, quantities per invoice and prices can all contribute; this project is not an inflation-adjusted retail volume index. [Source](https://www.ons.gov.uk/businessindustryandtrade/retailindustry/datasets/retailsales/current)

**9. Microsoft: report accessibility.** Application: use text labels and signed values alongside color, descriptive titles and a consistent page structure. Green and orange support interpretation rather than being the only way to distinguish gains and declines. This is a design application, not a claim that a formal accessibility audit was completed. [Source](https://learn.microsoft.com/en-us/power-bi/create-reports/desktop-accessibility-creating-reports)

## What our data can and cannot support

The source contains invoice identifiers, product codes and descriptions, quantities, unit prices, invoice dates, customer IDs and countries. It is a real historical dataset from an unnamed UK giftware retailer; many buyers are wholesalers. The public publisher does not identify an official brand to copy. [UCI source](https://archive.ics.uci.edu/dataset/502/online%2Bretail%2Bii)

We can calculate merchandise value, invoice volume, gross value per invoice, cancellation posting value, customer concentration, observed repeat purchasing and historical dormancy. We can rank material product and market changes. Missing identities stay in financial totals and are excluded from customer identity analysis.

| Attractive KPI that is not justified here | Missing evidence |
|---|---|
| Profit, gross margin or contribution margin | Product, fulfillment and operating costs |
| Conversion rate or abandoned checkout rate | Visits, sessions and checkout events |
| Customer acquisition cost or advertising return | Marketing spend, attribution and acquisition events |
| Inventory turnover or stockout diagnosis | Stock balances, receipts and availability history |
| Delivery service level | Promised and actual delivery dates |
| Budget attainment or RAG performance status | Approved targets and tolerances |
| Matched product return rate | Verified links from cancellation to original sale and return reasons |
| Predictive lifetime value or permanent churn | Adequate future observations and a validated predictive/contractual definition |

The report does not silently substitute a convenient transaction metric for any of these missing concepts.

## Findings that changed the visualization choices

The equal-period comparison uses January-November 2011 against January-November 2010. December 2011 is incomplete. Net merchandise value rose from GBP 8,406,439.65 to GBP 8,590,689.43: +GBP 184,249.78, or +2.19%. Sale invoices fell from 18,077 to 17,407, while average gross invoice value rose from GBP 477.28 to GBP 510.01.

The growth decomposition is an arithmetic identity:

`Net change = (invoices2011 - invoices2010) × grossPerInvoice2010 + invoices2011 × (grossPerInvoice2011 - grossPerInvoice2010) - (cancellations2011 - cancellations2010)`

This produces approximately **-GBP 319,778 from invoice count**, **+GBP 569,647 from gross value per invoice**, and **-GBP 65,619 from increased cancellation postings**. The components sum to the observed net-value change. The convention applies the invoice-count change first at the 2010 average, then values the invoice-value change at 2011 count. A different ordering would allocate the interaction differently. This explains the arithmetic, not the commercial causes or a pure price effect.

The previous fixed five-market view missed **Australia's +GBP 106,675.50** net change, the largest market gain. The revised ranking considers every market and selects by absolute GBP movement. The overview displays six movements; Markets displays eight. This avoids presenting a historically large market list as if it captured the growth story.

The previous product cancellation chart considered only top-selling products. Across the entire assortment, storage-jar SKU **23166 has GBP 77,479.64 of 2011 cancellation postings**. It belongs in a finance investigation even though it was absent from that restricted chart. Its original-invoice context and reasons remain unknown.

A currently large seller can also be declining: SKU **85123A is down GBP 47,441.57**, and SKU **22423 is down GBP 17,789.37** in net value. Conversely, a large increase with no 2010 sales may reflect a newly observed assortment item. Product hover detail distinguishes absent comparison-window sales from sales in both periods.

Customer dependence is material: the top 583 of 5,824 identified buyers (top decile rounded upward) generated **63.46%** of identified-buyer historical gross. The 536 established dormant buyers have **GBP 1,727,506.63** in past gross purchases. Those figures justify account research; they do not establish future revenue at risk or recoverable value.

## How to read the six pages

1. **Executive:** read the four comparisons, then the monthly trend, three arithmetic drivers, largest market movements and cancellation ratio over time. The net-growth chart title changes with the selected market.
2. **Markets:** compare monetary gains/declines and their current sales base. Absolute change identifies materiality; percentages provide context and are blank where the old net baseline is zero. Hover for invoice growth and cancellation exposure. The table total aggregates only the eight displayed markets, not all company sales.
3. **Customer value:** read concentration and established-dormant past value, then compare the concentration curve and value by segment. The diagonal is an equal-share reference, not a target. The curve ranks buyers by observed historical gross.
4. **Repeat buying:** the headline 90-day KPI uses all eligible historical cohorts. The monthly grid shows 2011 cohorts; M+1 means the next calendar month. Its percentages are monthly, not cumulative. Blank cells are unobserved future periods. The adjacent 90-day chart compares fully observed January-August 2011 cohorts and exposes their sample sizes on hover.
5. **Products:** compare the six largest net-value gains and declines, not only current sales leaders. Hover for SKU, original description, both years, cancellation ratio and comparison-window sales status.
6. **Cancellations:** inspect posting timing and the six largest product posting values across the whole assortment. The ratio relates current-window postings to current-window gross and is not a matched physical-return rate.

Management pages use Jan-Nov 2011 with equal prior-year comparisons. Customer pages deliberately use the fixed 1 December 2011 snapshot and are labeled separately. Market selections are local to their page; a selection in Executive does not silently filter a disconnected customer snapshot.

## Quality standard

The report uses native Power BI visuals and DAX. Validation checks the existing financial and cohort results, new bridge components across market/month contexts, concentration points, selected product and country rankings and mature cohort numerators and denominators. The SQL expectations are independent of the DAX implementation. Visual review checks for truncated titles, missing charts, hidden small values, unreadable tables and unwanted scroll bars.

The evidence supports an interview discussion about analytical judgment: choosing comparisons, documenting populations, exposing material exceptions, separating arithmetic from causality and resisting attractive metrics that the data cannot support.
