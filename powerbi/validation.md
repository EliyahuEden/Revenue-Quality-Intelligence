# Native Power BI verification

Verified in Microsoft Power BI Desktop 2.159.883.0 on 21 October 2026.

- The native PBIP opened with five populated report pages, nine imported tables and seven relationships.
- All 25 explicit DAX measures evaluated successfully in the running Desktop Analysis Services engine. Measures designed to require a single month or cohort age return blank outside that context.
- Gross sales, cancellation postings, net merchandise value and sale invoices matched independent SQL baselines in all nine combinations of year (all/2010/2011) and country (all/United Kingdom/Germany): **36 comparisons passed** with monetary tolerance below half a penny.
- Customer snapshot checks returned 5,824 buyers, 3,533 mature eligible buyers and 1,458 repeat buyers: a 41.268% repeat rate.
- All five native pages were inspected for populated visuals. Remaining text encoding and KPI precision defects were corrected in the source generator.
- The analytical layer passed 25 data contracts and all 10 pytest tests.

Machine-readable native results are in [native_validation.json](native_validation.json). These results establish native measure execution and selected filter-context parity; they are not an exhaustive check of every possible visual selection. GitHub Actions has not been run remotely. No Power BI Service publishing or scheduled refresh is claimed.

## Saved PBIX

`RevenueQuality.pbix` was saved through Desktop and its archive integrity checked. It contains all five pages, 119 visual containers and an embedded DataModel. The file is approximately 23.5 MB. [File verification and SHA-256](pbix_verification.json). Native screenshots show the saved report, including corrected currency text and KPI precision.

## Dashboard redesign

The five native pages use question titles, a consistent navy/teal/blue/coral palette, KPI hierarchy and short interpretation notes. Desktop inspection confirmed the cohort conditional colors, exact segment counts, top-ten product ranking, gross-to-net reconciliation and decision cards. All 25 measures and 36 financial comparisons passed again after applying the corrected semantic model. The PBIX was saved through Desktop with the Sales overview as its opening page; screenshots and file verification match this redesign.
