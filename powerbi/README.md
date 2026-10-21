# Power BI report

Open `RevenueQuality.pbix` in Power BI Desktop to view the report with its imported data. Open `RevenueQuality.pbip` to edit the native text-based report and semantic model sources.

Nine imported tables, seven single-direction relationships, 25 explicit DAX measures and five pages. Power Query uses typed CSV imports. Financial measures enforce complete periods. Lifecycle and cohort tables are disconnected snapshots to preserve their observation windows.

## Refresh on another computer

1. Run `python scripts/pipeline.py` from the repository root to create `data/exports`.
2. In Desktop, choose **Transform data → Manage parameters** and set **DataFolder** to the absolute path of `data/exports`.
3. Close and apply, refresh, and save.

Alternatively run `python scripts/build_powerbi.py` after the pipeline. Close Desktop first. This regenerates the PBIP with the current source path and replaces manual layout edits. It does not update the PBIX; save that through Desktop after validation.

## Files

- `RevenueQuality.pbix`: portable report with imported data (approximately 23.5 MB).
- `RevenueQuality.pbip`, `.Report`, `.SemanticModel`: native project sources.
- `dax_measures/measures.dax`: readable measure definitions installed by the builder.
- `expected_measure_values.json`: independent SQL baselines for nine year/country contexts.
- `native_validation.json`, `validation.md`: verification results and scope.
- `screenshots`: actual Power BI Desktop previews of all five pages.

Local viewing does not require an account. Service publishing is a separate deployment step.

## Design and interpretation

The five pages are Sales overview, Customer return, Product drivers, Trust the numbers and Next decisions. The leading card has the strongest contrast; compact K/M notation makes amounts easier to scan. Native cohort-cell shading indicates monthly purchase activity, not causal improvement. Blank cohort cells are future/unobserved periods.

The five-market chart uses a fixed full-history country list; its amounts follow filters. Product bars use the existing DAX product-rank measure to show ranks up to 10 in the selected context. The details table remains available for all products. Customer segments are fixed as of 1 December 2011 and are disconnected from transaction-date/country filters.

`scripts/design_report.py` generates the native visual definitions and is called by `scripts/build_powerbi.py`. Regeneration replaces report layout definitions; save manual changes before regenerating. It also preserves a previous definition tree in the operating system temporary directory.

Design references: [Microsoft dashboard guidance](https://learn.microsoft.com/en-us/power-bi/create-reports/service-dashboards-design-tips), [Store Sales sample](https://learn.microsoft.com/en-us/power-bi/create-reports/sample-store-sales), [Data Stories Gallery](https://community.fabric.microsoft.com/category/pbi_comm_galleries/discussions/datastoriesgallery). These informed hierarchy and interaction design; no sample assets or data were imported.
