# EcoHome Studio: application reference resources

## Source and scope

Source repository: https://github.com/kasimsuh/ecohome-studio

Recorded source revision: `ab640555f0c5f7bc63b0da9d5d46d5a6d5198f2f`.

EcoHome Studio is a home-design application rather than a published material-recognition dataset. Its repository contains configuration options, demonstration concepts, scoring rules and reference documents. No standalone dataset or CSV files were located at the recorded revision.

This directory provides derived factual option tables and an index of relevant source resources. The source application and document contents are not redistributed here.

## CSV exports

| File | Contents |
| --- | --- |
| `material_options.csv` | Six facade options and four roof-material options from the application schema |
| `design_options.csv` | Room, roof, orientation, upgrade-category and impact-level configuration values |
| `climate_options.csv` | Five application climate categories |
| `budget_options.csv` | Three application budget categories |
| `resource_inventory.csv` | Paths, types, sizes, source hashes and revision-specific links for 16 source files |
| `knowledge_sources.csv` | Index of five PDF documents and five local guidance notes |
| `source.json` | Provenance and processing scope |

Each exported option is marked `application_option`. These values are neither verified product records nor material-performance measurements. The PDF index records source filenames and locations without inferring unverified document titles or licences.

## Reproduction

The exporter uses Python's standard library and retrieves the schema, configuration and file listing from the recorded revision:

```bash
python datasets/ecohome-studio/export_csv.py
```

This regenerates the CSV tables. It does not download the PDF collection, run the source application, execute external code, or perform model training.

[Notebook 06](../../notebooks/06_ecohome_studio_analysis.ipynb) contains executed table checks and descriptive graphs. Counts refer to configuration options and indexed files, not to photographed materials or training observations.

## Interpretation

Source demonstration concepts and rule-based sustainability scores are not imported as empirical data. Environmental performance requires independently supported measurements and clearly defined units and system boundaries.

The indexed resources may inform application structure or a future document-retrieval workflow. They are not an image/label collection for visual recognition and have not been used to train the Fitwell camera.

## Attribution and permissions

Application source: `kasimsuh/ecohome-studio`. Documents and cited guidance retain their original authorship and rights.

No repository-wide licence file was located at the recorded revision. The font licence within the source repository does not establish permission for its application code or PDF collection. This integration therefore records references and derived factual configuration values rather than copying source prose, software or document files. Any subsequent redistribution requires review of the applicable permissions.
