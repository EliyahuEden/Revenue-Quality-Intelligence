# Native Power BI verification

The research-based report contains six pages, nine imported core tables, two small calculated axes, seven relationships and 69 DAX measures. All measures evaluate in Power BI Desktop's local Analysis Services engine.

- 684 existing management metric comparisons passed across 36 month/market contexts.
- 135 monthly-cohort numerator, denominator and rate checks passed.
- 36 existing financial comparisons passed.
- 225 new checks passed: exact growth decomposition and driver-axis values, ten concentration points and references, fixed customer measures, eight-market ranking, product gain/decline/cancellation rankings and mature 2011 cohort rates.
- Total: **1,080 numerical checks passed**. All 10 Python tests passed. All native source files passed the Microsoft JSON schemas.

Native visual review includes dynamic executive titles, gains/declines with explicit signs, complete six- and eight-market selections, customer concentration, repeat-buying windows, SKU-specific product movers and cancellation products across the full assortment. Product tooltip fields are measures so they do not change the grouping grain. Short product labels include SKU to preserve uniqueness. No custom visual or HTML renderer is required.

[Native results](native_validation.json), [research SQL expectations](research_expected_values.json), [existing comparison expectations](manager_expected_values.json), [cohort expectations](cohort_expected_values.json). These checks cover specified contexts, not every possible click path. No deployment to Power BI Service, scheduled refresh, target attainment or achieved commercial impact is claimed.

## Saved native report

Desktop saved the six-page PBIX with Executive as its opening page. Archive integrity passed, all 91 visual containers use native types, and the imported DataModel is embedded. [File verification and SHA-256](pbix_verification.json). Six portfolio previews were captured from the revised native report.
