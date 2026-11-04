# OpenSurfaces — Release 0

## Source

Project: https://opensurfaces.cs.cornell.edu/

Publication and download documentation: https://opensurfaces.cs.cornell.edu/publications/opensurfaces/

OpenSurfaces provides region-level annotations for the study of surface appearance and material recognition.

## Repository contents

| File | Description |
| --- | --- |
| `materials.csv` | Material vocabulary, including source identifiers and status fields |
| `material_groups.csv` | Original group definitions |
| `photo_licenses.csv` | Licence definitions from the release metadata |
| `archive_inventory.csv` | File-level archive inventory |
| `source.json` | Source and storage references |

The vocabulary tables were derived from the original Release 0 JSON records. Source fields and identifiers are retained. Inactive or ambiguous entries are not equivalent to usable training categories, and vocabulary size does not measure material frequency.

## Dataset archive

The [GitHub Release](https://github.com/samihaabedanur/Fitwell-AI/releases/tag/dataset-opensurfaces-release-0) contains the original ZIP archive (1,175,026,542 bytes), the upstream processing helper, provenance, an inventory and SHA-256 checksums. The [archival workflow](https://github.com/samihaabedanur/Fitwell-AI/actions/runs/41856852494) verified ZIP integrity before upload.

Official source files:

- https://labelmaterial.s3.amazonaws.com/release/opensurfaces-release-0.zip
- https://labelmaterial.s3.amazonaws.com/release/process_opensurfaces_release_0.py

Checksums document the bytes archived by the project workflow; they are not independent publisher-supplied checksums.

## Processing and analysis

[Notebook 03](../../notebooks/03_opensurfaces_analysis.ipynb) examines the archive inventory and annotation vocabularies. Its storage figures describe file sizes rather than the distribution of material surfaces.

The archive and helper are preserved as distributed. The legacy helper has not been executed within this integration and may require adaptation for current Python environments. Retrieval of associated photographs, preparation of image-mask pairs and verification of annotation quality remain separate processing stages. The archive is not treated as a complete collection of full-resolution photographs.

## Licence and citation

Annotations are distributed under [Creative Commons Attribution 4.0 International](https://creativecommons.org/licenses/by/4.0/). Photographs retain their individual licences.

Sean Bell, Paul Upchurch, Noah Snavely and Kavita Bala. **OpenSurfaces: A Richly Annotated Catalog of Surface Appearance.** ACM Transactions on Graphics (SIGGRAPH), 32(4), 2013.

No material-recognition model has been trained or deployed through this dataset integration.
