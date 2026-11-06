# Research datasets

This directory documents the external datasets selected for Fitwell AI. The collection supports material recognition, texture analysis, material representation and environmental information. Dataset acquisition, exploratory analysis and model training are recorded as separate stages.

## Dataset inventory

| Dataset | Repository contents | Research role |
| --- | --- | --- |
| [DTD](dtd/) | Index of 5,640 images, 47-category table, downloader and archived image release | Texture attributes |
| [MatFuse](matfuse/) | Five sample materials comprising 35 files, metadata and inventories | Material maps and synthetic material representation |
| [OpenSurfaces](opensurfaces/) | Release 0 archive, material vocabulary, group definitions, photo-licence table and file inventory | Material-region annotation and segmentation research |
| [DMS](dms/) | Fused-label archive, taxonomy, 46-class model mapping and original sample code | Dense material segmentation |
| [ÖKOBAUDAT](oekobaudat/) | Source reference and empty environmental-record template | Environmental information; source records not yet imported |

Large archives are stored under [GitHub Releases](https://github.com/samihaabedanur/Fitwell-AI/releases). The [dataset catalogue](dataset_catalog.csv) records the available analysis files and storage locations.

## CSV tables and notebooks

| Dataset | Principal CSV files | Analysis notebook |
| --- | --- | --- |
| DTD | [Image index](dtd/images.csv), [category counts](dtd/categories.csv) | [01 — DTD](../notebooks/01_dtd_analysis.ipynb) |
| MatFuse | [Sample metadata](matfuse/samples.csv), [file inventory](matfuse/files.csv) | [02 — MatFuse](../notebooks/02_matfuse_analysis.ipynb) |
| OpenSurfaces | [Materials](opensurfaces/materials.csv), [groups](opensurfaces/material_groups.csv), [photo licences](opensurfaces/photo_licenses.csv), [archive inventory](opensurfaces/archive_inventory.csv) | [03 — OpenSurfaces](../notebooks/03_opensurfaces_analysis.ipynb) |
| ÖKOBAUDAT | [Environmental records and cleaning outputs](oekobaudat/) | [04 — ÖKOBAUDAT cleaning and analysis](../notebooks/04_oekobaudat_analysis.ipynb) |
| DMS | [Taxonomy](dms/taxonomy.csv), [model classes](dms/model_classes.csv), [archive summary](dms/archive_summary.csv) | [05 — DMS](../notebooks/05_dms_analysis.ipynb) |

The notebooks contain executed descriptive analyses. Texture categories, material vocabulary entries and archive file counts represent different quantities and are reported accordingly. No environmental measurements are included in the ÖKOBAUDAT template.

## Processing status

The available work covers source collection, archive verification, metadata conversion and exploratory analysis. These activities do not update the camera model. A separate [DMS training pipeline](../training/) has been prepared; end-to-end training and camera deployment remain pending.

## Attribution and licensing

Source attribution, version references and applicable terms are documented within each dataset directory. Photograph and model licences may differ from annotation licences. The project licence does not supersede external data rights.

## Application reference: EcoHome Studio

[EcoHome Studio](ecohome-studio/) is indexed as an application reference rather than a labelled dataset. Six derived CSV tables record material and design options, climate and budget categories, and source-resource locations. [Notebook 06](../notebooks/06_ecohome_studio_analysis.ipynb) provides executed descriptive analysis. Source code, document contents and demonstration sustainability scores have not been imported as research observations.
