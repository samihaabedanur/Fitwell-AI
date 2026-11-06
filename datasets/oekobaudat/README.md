# ÖKOBAUDAT

## Source

Source: https://www.oekobaudat.de/en/service/downloads.html

Referenced release: ÖKOBAUDAT 2024-II.

## Intended application

ÖKOBAUDAT is identified as a potential source of environmental product information for the material-information component of Fitwell AI. Environmental records would be associated with identified materials following product and unit verification.

## Available files and status

The source dataset has not been imported into this repository. `environmental_records_template.csv` defines an empty input structure; it contains no environmental observations.

[Notebook 04](../../notebooks/04_oekobaudat_analysis.ipynb) contains the input schema, cleaning process, cleaned table, quality report, graphs and environmental-impact review.

The official ÖKOBAUDAT CSV is used locally to create `environmental_lookup.csv`, a compact research lookup for the camera. The raw export is ignored because it is large; download it from the official source when rebuilding the lookup.

In the local camera, click a detected material box to view a source-backed GWP-total value, unit, lifecycle module and source record count. Values are representative lookup summaries, not a complete building LCA; material quantity, product specification and full lifecycle modules are still required for a project assessment.

## Cleaning outputs

Run `python clean_oekobaudat.py` from this directory to recreate the audit outputs:

- `environmental_records_clean.csv`: cleaned records with normalized numeric GWP-total values.
- `analysis/cleaning_report.json`: row counts, removed values, lifecycle modules and dataset types.
- `analysis/records_by_category.png`: cleaned records by material category.
- `analysis/records_by_lifecycle_module.png`: lifecycle-stage coverage.
- `analysis/gwp_total_distribution.png`: GWP-total distribution after outlier clipping for visualization.

## Data requirements

Imported records must retain their source identifiers, reference units, lifecycle modules, indicators and measurement units. Comparisons require consistent units and system boundaries. Source terms and attribution requirements must be recorded before data distribution.

ÖKOBAUDAT is intended for environmental information retrieval, rather than visual recognition training.
