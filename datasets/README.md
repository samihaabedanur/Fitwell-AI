# Fitwell Research Datasets

This folder contains datasets used for the Fitwell AI research project.

Research areas:
- Building material identification
- Embodied carbon and environmental impact
- Material pricing and availability
- Sustainable material alternatives

Dataset sources and licenses will be documented before uploading data.

## MatFuse samples

See [matfuse/](matfuse/) for five original sample materials (35 files), provenance, licence and an inventory. The full MatFuse training dataset is not included or published by the authors; this addition does not train the camera model.

## Describable Textures Dataset (DTD)

See [dtd/](dtd/) for an index of all 5,640 images across 47 texture categories and a pinned Python downloader for the Voxel51 Hugging Face dataset. Image bytes download locally, not into Git history. Texture labels are not verified material identities; no camera model has been trained with this addition.

## OpenSurfaces

See [opensurfaces/](opensurfaces/) for Release 0 provenance and instructions. The official ZIP and legacy helper are stored as GitHub Release assets by the upload workflow. Annotations are CC BY 4.0; images retain their individual licences. No camera training is performed.

## CSV tables and analysis notebooks

Open [the notebooks folder](../notebooks/) for four executed analysis notebooks with saved outputs. [dataset_catalog.csv](dataset_catalog.csv) summarises each source and its analysis files.

| Dataset | CSV tables | Notebook |
| --- | --- | --- |
| DTD | [Image index](dtd/images.csv), [category counts](dtd/categories.csv) | [DTD analysis](../notebooks/01_dtd_analysis.ipynb) |
| MatFuse | [Samples](matfuse/samples.csv), [file inventory](matfuse/files.csv) | [MatFuse analysis](../notebooks/02_matfuse_analysis.ipynb) |
| OpenSurfaces | [Archive inventory](opensurfaces/archive_inventory.csv), [material vocabulary](opensurfaces/materials.csv), [groups](opensurfaces/material_groups.csv), [photo licences](opensurfaces/photo_licenses.csv) | [OpenSurfaces analysis](../notebooks/03_opensurfaces_analysis.ipynb) |
| ÖKOBAUDAT | [Empty environmental input template](oekobaudat/environmental_records_template.csv); source observations are not present | [Input checks](../notebooks/04_oekobaudat_analysis.ipynb) |

These notebooks analyse available records; they do not train the camera. OpenSurfaces vocabulary counts are not material-frequency counts. No environmental measurements or model accuracy scores have been invented.
