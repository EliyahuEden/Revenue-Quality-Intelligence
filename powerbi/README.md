# Power BI report

Open `RevenueQuality.pbix` in Power BI Desktop to view the report with its imported data. Open `RevenueQuality.pbip` to edit the native text-based report and semantic model sources.

Nine imported tables plus two calculated analytical axes, seven single-direction relationships, 69 explicit DAX measures and six pages. Power Query uses typed CSV imports. Financial measures enforce complete periods. Lifecycle and cohort tables are disconnected snapshots to preserve their observation windows.

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
- `screenshots`: actual Power BI Desktop previews of all six pages.

Local viewing does not require an account. Service publishing is a separate deployment step.


## Design and interpretation

The Forest and Linen theme uses native visuals with question-led titles, prior-year comparisons, signed contribution bars and supporting hover detail. Six pages separate Executive, Markets, Customer Value, Repeat Buying, Products and Cancellations. The country ranking considers all markets; the cancellation-product ranking considers the full assortment. Customer snapshots have explicit observation windows.

Read the [research rationale](../docs/dashboard_research.md) and [dashboard guide](../docs/dashboard_guide.md). `scripts/design_report.py` generates the native report source. The model has nine imported core tables and two small calculated axes (`growth_driver` and `customer_percentile`). After rebuilding source, apply external changes and refresh data in Desktop before saving a portable PBIX. The included PBIX already contains its model and data.
