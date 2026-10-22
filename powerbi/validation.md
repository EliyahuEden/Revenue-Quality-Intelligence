# Native Power BI verification

The revised report contains five pages, nine imported tables, seven relationships and 45 DAX measures. All measures evaluated in Power BI Desktop's local Analysis Services engine.

- 684 comparison checks passed: 19 management metrics across 36 month/market contexts.
- 135 cohort checks passed: active buyers, original cohort size and repeat-month rate for all 45 observable cells in the displayed 2011 / six-month grid. The check uses the same grouped DAX query shape as a matrix, including the year filter.
- 36 base financial checks passed against independent SQL expectations.
- All 10 Python tests passed. All report definition files passed the Microsoft JSON schemas.

Desktop inspection covers the overview's distinct year colors, period labels, comparative KPI signs, readable product labels, larger cohort cells and the compact management action queue. Financial pages use Jan-Nov 2011; customer metrics use a historical snapshot. Conditional context behavior is documented in the [dashboard guide](../docs/dashboard_guide.md).

[Native comparison results](native_validation.json), [manager SQL expectations](manager_expected_values.json), [cohort SQL expectations](cohort_expected_values.json). No Power BI Service publication, scheduled refresh, target attainment or realized business impact is claimed.

## Saved report

The management PBIX was saved through Desktop with the Overview opening page. Archive integrity passed: five pages, 91 visual containers including text and layout elements, and an embedded imported DataModel. [SHA-256 and file verification](pbix_verification.json). Portfolio screenshots show the revised native pages.
