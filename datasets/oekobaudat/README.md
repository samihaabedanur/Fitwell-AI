# ÖKOBAUDAT

## Source

Source: https://www.oekobaudat.de/en/service/downloads.html

Referenced release: ÖKOBAUDAT 2024-II.

## Intended application

ÖKOBAUDAT is identified as a potential source of environmental product information for the material-information component of Fitwell AI. Environmental records would be associated with identified materials following product and unit verification.

## Available files and status

The source dataset has not been imported into this repository. `environmental_records_template.csv` defines an empty input structure; it contains no environmental observations.

[Notebook 04](../../notebooks/04_oekobaudat_analysis.ipynb) documents the input schema and checks for the availability of source records. Environmental comparison and carbon calculations remain pending acquisition and review of a suitable export.

## Data requirements

Imported records must retain their source identifiers, reference units, lifecycle modules, indicators and measurement units. Comparisons require consistent units and system boundaries. Source terms and attribution requirements must be recorded before data distribution.

ÖKOBAUDAT is intended for environmental information retrieval, rather than visual recognition training.
