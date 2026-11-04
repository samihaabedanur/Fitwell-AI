# Dense Material Segmentation

## Source and research role

Source: https://github.com/apple-aiml-research/ml-dms-dataset

Paul Upchurch and Ransen Niu. **A Dense Material Segmentation Dataset for Indoor and Outdoor Scene Parsing.** ECCV 2022. https://arxiv.org/abs/2207.10614

DMS is included as a source of dense material annotations for the segmentation component of Fitwell AI.

## Repository contents

| File or directory | Description |
| --- | --- |
| `taxonomy.csv` | Original label IDs, names, semantic flags, model membership and sRGB colours |
| `model_classes.csv` | Mapping between the pretrained model's 46 output channels and dataset label IDs |
| `downloads.csv` | Official archive URLs and resource descriptions |
| `archive_summary.csv` | Measured directory-level file counts and uncompressed sizes |
| `source.json` | Source revision and licence references |
| `upstream/` | Unmodified source code, taxonomy, environment, README and notices |
| `download.py` | Local archive download and ZIP-integrity validation |

The taxonomy contains 57 entries. The sample inference model uses 46 output classes; dataset label IDs and model-channel indexes therefore require explicit mapping.

## Dataset archive

The [fused-label release](https://github.com/samihaabedanur/Fitwell-AI/releases/tag/dataset-dms-v1-labels) contains the original ZIP (660,365,654 bytes), a file inventory, directory summary, attribution and checksums. ZIP integrity was verified during archival.

The training, validation and test label directories contain 24,251, 10,138 and 10,168 files respectively. These values describe archive contents, rather than recognition performance.

RGB photographs are obtained separately from Open Images. The optional raw-polygon and pretrained-model archives are listed in `downloads.csv` but are not stored as release assets.

## Reproduction

From the repository root:

```bash
python datasets/dms/download.py --resource fused_labels
```

The downloader also supports `--resource pretrained_model` and `--resource raw_polygons`. Files are written to `datasets/dms/local_data/`. Extraction and inference are separate operations.

The original sample scripts are retained in `upstream/` with their environment specification. Their relative taxonomy references require execution from that directory. Their preparation procedures include image-dimension and orientation checks. GPU execution of the original code has not been validated within this integration.

## Analysis and training status

[Notebook 05](../../notebooks/05_dms_analysis.ipynb) presents the taxonomy, channel mapping and archive statistics. The separate [training directory](../../training/) contains a preliminary preparation and fine-tuning pipeline. End-to-end training and integration of a custom model into the browser camera remain pending.

## Licensing

Dataset annotations are licensed under [CC BY-NC 4.0](https://creativecommons.org/licenses/by-nc/4.0/), requiring attribution and non-commercial use. The sample code and pretrained model are governed by the Apple licence retained in `upstream/LICENSE.txt`, together with the original acknowledgements.

Photograph rights are separate from annotation and software rights. The root repository licence does not supersede these terms. Commercial use requires an appropriate review of the applicable data and model permissions.
