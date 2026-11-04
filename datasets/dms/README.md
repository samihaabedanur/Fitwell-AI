# Dense Material Segmentation (DMS)

Original: https://github.com/apple-aiml-research/ml-dms-dataset

Paul Upchurch and Ransen Niu, **A Dense Material Segmentation Dataset for Indoor and Outdoor Scene Parsing**, ECCV 2022. https://arxiv.org/abs/2207.10614

## Included here

- `taxonomy.csv`: every label ID, original name, short name, semantic-label flag, model membership and sRGB colour.
- `model_classes.csv`: exact output-channel to label-ID mapping for the 46-class pretrained model, extracted from upstream inference.py. Do not confuse channel indexes with dataset label IDs.
- `downloads.csv`: the three official archive links and their roles.
- `upstream/`: unmodified original sample code, taxonomy, environment, README, licence and acknowledgements, pinned in `source.json`.
- `../../notebooks/05_dms_analysis.ipynb`: executed taxonomy analysis and graphs. No recognition-accuracy claims.
- `download.py`: optional local downloader with ZIP integrity checks.

## Dataset archive on GitHub

The official **fused-label ZIP** is stored in [DMS — fused material segmentation labels](https://github.com/samihaabedanur/Fitwell-AI/releases/tag/dataset-dms-v1-labels). It is 660,365,654 bytes (about 660 MB), with a verified ZIP CRC check. The Release also contains a file inventory, directory summary, attribution and checksums. `archive_summary.csv` is included here for analysis. The recorded train, validation and test label directories contain 24,251, 10,138 and 10,168 files respectively; these are archive file counts, not accuracy measurements.

The RGB photographs are NOT bundled. Acquire the corresponding Open Images photos separately before preparing image/mask pairs. Do not treat label masks as colour training photos.

The optional raw-polygon archive and pretrained-model archive remain linked in `downloads.csv`; they are not duplicated as Release assets. Fused masks are the upstream-recommended archive for training/evaluation.

## Local download

```bash
python datasets/dms/download.py --resource fused_labels
```

Use `--resource pretrained_model` or `--resource raw_polygons` only if needed. Downloads save under `datasets/dms/local_data/`; extraction and inference are not run automatically.

## Original sample code

Read `upstream/README.md` and `upstream/environment.yaml` before installing its legacy GPU environment. The code has been copied, not GPU-tested here. Run the original scripts from their `upstream` directory so they find `taxonomy.json`. Original preparation checks image dimensions and orientation; run those checks before training or evaluation.

No model training, pretrained-model execution or browser-camera change has been performed as part of this dataset addition.

## Rights

Dataset annotations: **CC BY-NC 4.0**, non-commercial use with attribution: https://creativecommons.org/licenses/by-nc/4.0/

Sample code and model: Apple's separate licence, retained at `upstream/LICENSE.txt`, with its acknowledgements. RGB photos have separate Open Images/source licences. Fitwell's root licence does not override these terms. Do not assume this research resource is cleared for a commercial Fitwell product.
