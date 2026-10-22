# Reading the updated management dashboard

The Overview, Products and Sales quality pages now use **January-November 2011**. Comparisons use the same eleven months in 2010. This is different from the full two-year totals in the original study guide. December 2011 is incomplete and is excluded. The Customers page remains a full-history snapshot as of 1 December 2011; its simplified grid shows 2011 first-purchase groups and the next six calendar months.

## The overview in 30 seconds

| Metric | Jan-Nov 2011 | Comparison with Jan-Nov 2010 |
|---|---:|---:|
| Net merchandise value | GBP 8,590,689.43 | +2.2% |
| Sale invoices | 17,407 | -3.7% |
| Average gross value per invoice | GBP 510.01 | +6.9% |
| Cancellation value / gross sales | 3.2% | +0.7 percentage points |

Sales value grew modestly while invoice volume fell. Higher average gross invoice value accompanied the increase. Cancellation postings consumed a larger share of gross sales. These observations identify questions to investigate; they do not prove that pricing changes, promotions or a particular customer group caused them. Invoice count is not a measure of website traffic or customer purchase frequency by itself.

The two-year line chart compares the same months. Green is 2011 and muted gray-green is 2010. The cancellation chart uses orange for 2011. The market chart shows **absolute net sales change in GBP**, not percentage growth, for a fixed list of five historically major markets. Left of zero means lower net sales. The product chart ranks products by 2011 net merchandise value. Market filtering recalculates the figures and rankings; the five-market comparison list stays fixed. Click blank canvas to clear a chart selection. The page tabs lead to details.

Gross sales are before cancellation postings. Net merchandise value equals gross minus those postings. Average gross per invoice equals gross sales divided by distinct sale invoices. This does not establish profit or the effect of a campaign. The cancellation ratio is a value ratio, not a matched physical return rate. No target or profit data exists, so the report shows direction relative to last year rather than an invented overall health score.

## Customers

The 41.3% card is 1,458 eligible buyers purchasing again within 90 days divided by 3,533 buyers with fair follow-up. The 5,824 identified buyers card describes the full historical population. These populations are different.

Each cohort row is a first-observed-purchase month in 2011. Column 1 is the next calendar month, not the first purchase month. January 2011 / column 1 is 12 returning buyers divided by 72 original buyers = 16.7%. Each later column uses that original group's size. Customers can return after skipping a month; the percentages are not cumulative and should not be added. Darker cells mean more purchased. Blank cells mean the later month was not observed. November has no later observable month and therefore no visible row. The six-column view is a presentation choice; the complete cohort source remains available.

Customer groups remain full-history segments. Developing repeat means 2-4 invoices. Established means at least five, split into active (last purchase within 90 days) and dormant (more than 90 days). Single-purchase customers are split into recent first purchase and dormant using the same recency rule. A dormant label is a working definition, not proof of permanent loss.

## Products and sales quality

Product charts compare the leading ten products' net sales and cancellation value. The cancellation chart is limited to those top-selling products; it is not an all-product cancellation ranking. Short product labels improve reading; the source retains original descriptions and codes.

Sales quality reconciles GBP 8.88M gross minus GBP 287.0K cancellation postings to GBP 8.59M net. Its monthly chart compares cancellation values with 2010. In 2011, 13.5% of gross sales lacked a customer ID. Such sales remain in financial totals but cannot be assigned to customer cohorts. The duplicate-policy sensitivity is GBP 18.2K in this period; this is a scenario difference, not a verified correction or saving.

## Management priorities

1. Review dormant and lost purchasing accounts because invoice count fell. Determine which accounts and purchasing patterns explain the change before proposing an intervention.
2. Investigate cancellation reasons and original-invoice links because the cancellation ratio increased. Do not assume every posting represents a returned product.
3. Improve stable customer identity capture because anonymous sales limit customer analysis. Preserve unknown sales in financial reporting.

These are proposed actions. A real intervention would need an owner, operational data and an evaluation plan. The project does not claim realized commercial uplift.

## Theme and evidence

The Forest and Linen theme uses deep green, warm cream and restrained orange with Segoe UI. It is a custom portfolio identity. UCI's source does not name the retailer, so this is not represented as its official brand: https://archive.ics.uci.edu/dataset/502/online%2Bretail%2Bii

The model contains 45 DAX measures: 25 analytical measures plus 20 comparison and ranking measures. Native Desktop validation covers 684 manager metric comparisons, 135 cohort numerator/denominator/rate comparisons and 36 existing financial comparisons. All passed. All 10 Python tests passed. The conditional-cohort denominator was simplified to sum one cohort size per selected cohort/age; the cohort-age source key is unique. No total across different cohort ages is shown.
