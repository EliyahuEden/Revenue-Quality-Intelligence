# Data access and attribution

Chen, D. (2012). *Online Retail II* [Dataset]. UCI Machine Learning Repository. DOI: https://doi.org/10.24432/C5CG6D. [Official source](https://archive.ics.uci.edu/dataset/502/online+retail+ii). [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/). Adapted by type normalization, key pseudonymization, classification and aggregation. No creator endorsement implied.

Raw workbook and Parquet cache are not committed. Run `python scripts/pipeline.py` to acquire the official source; no credential required. `data/raw/`, `data/warehouse/` and `data/exports/` are Git-ignored. Prepared Power BI CSVs are available locally in `data/exports/`, retaining this attribution. Analysis/output CSVs are derived aggregates or pseudonymous records; Git excludes the raw workbook, database and large exports.

The two sheets overlap on 1â€“9 December 2010; 22,523 earlier-partition rows are superseded after verified multiset equality. Raw/staging preserve these records with an audit status. Source records end on 9 December 2011. Core reporting uses complete months through November 2011. A row is an invoice **line**, not necessarily an order or a unique customer purchase. Product descriptions can vary, identities can be absent, and C invoice prefix indicates cancellation rather than physical return confirmation. Read the KPI contract before using exported values.
