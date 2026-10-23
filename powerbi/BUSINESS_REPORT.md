# Business report revision

The main pages contain performance measures, comparisons, trends and exception queues. Definitions, data limitations and analytical validation stay in the supporting documentation. No targets, operating owners, achieved uplift or live feeds have been fabricated.

## Olist

Open Olist-Marketplace-Intelligence.pbix. Three main pages: Marketplace overview, Delivery operations and Service priorities; seller drillthrough is retained. Date, state and category slicers share synchronized groups. The reduction dropdown defaults to 20% and affects only the planning scenario. Scenario volume is held constant; it is not a forecast. Month-start date boundaries select whole purchase months.

The failed risk model, experiment instructions and recommendation essays are absent from the report canvas. Their evidence remains in the analytical project documents. The original metrics, 44 DAX measures and embedded historical snapshot are preserved. Refresh does not acquire new transactions. The Python generator now restores the reviewed native report template.

## RevenueQuality

Open RevenueQuality.pbix. Six pages: Revenue performance, Market performance, Customer value, Repeat purchasing, Product performance and Cancellation exposure. Comparable financial periods remain Jan-Nov 2011 versus Jan-Nov 2010; customer views retain the Dec 1, 2011 snapshot. Net merchandise value is gross less cancellation postings, not accounting revenue or margin. Cancellation / gross is an exposure ratio, not a matched return rate. Definitions of dormant/established customers and complete repeat cohorts remain in the project documentation.

Both PBIX files contain imported data and can be explored without the source CSV files. Editable RevenueQuality source retains the existing Desktop project data paths; to refresh on another machine, configure the exported CSV location. The business report source package includes the exports. Independent public-data project attribution remains in documentation.

## Verification

Native visual definitions validated with Microsoft's PBIR CLI: zero errors and zero warnings for both reports. Olist's 11 native DAX checks passed. RevenueQuality's 684 comparison checks, 135 cohort checks, 36 financial checks and 225 additional business checks passed. All main pages were rendered in Power BI Desktop, and the PBIX files were saved by Desktop with embedded DataModel content. Validation files accompany the editable source.
