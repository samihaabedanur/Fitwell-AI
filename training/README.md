# DMS pilot training protocol

The pipeline is configured to fine-tune a torchvision DeepLabV3-MobileNet model, initialised with pretrained segmentation weights, on DMS photo/mask pairs. Apple's TorchScript checkpoint is not used as the optimisation target. DMS annotations are CC BY-NC 4.0; original photos retain their licences. This is a non-commercial research pilot.

## Repository and working directory

The protocol assumes a local checkout of Fitwell-AI. Commands are executed from the repository root. Updates can be retrieved with `git pull` after review of local changes.

## Python environment

The reference environment uses Python 3.11. The following Windows commands address the virtual-environment interpreter directly:

```powershell
py -3.11 -m venv .venv
.venv\Scripts\python.exe -m pip install --upgrade pip
.venv\Scripts\python.exe -m pip install -r training/requirements.txt
```

GPU availability depends on the hardware and PyTorch build. CUDA installation guidance is provided by the official PyTorch selector: https://pytorch.org/get-started/locally/ . CPU execution is supported with a substantial performance cost.

```powershell
.venv\Scripts\python.exe -c "import torch; print('GPU available:', torch.cuda.is_available())"
```

## Label archive preparation

The downloader uses Python's standard library:

```powershell
.venv\Scripts\python.exe datasets/dms/download.py --resource fused_labels
.venv\Scripts\python.exe -m zipfile -e datasets/dms/local_data/dms_v1_labels.zip datasets/dms/local_data
```

The extracted directory `datasets/dms/local_data/DMS_v1` must contain `info.json.gz` and `labels/train`, `labels/validation`, `labels/test`.

## Photograph retrieval and pair validation

```powershell
.venv\Scripts\python.exe training/prepare_dms_pilot.py --data datasets/dms/local_data/DMS_v1 --train 200 --validation 50 --test 25
```

The preparation script attempts the first 200 training, 50 validation and 25 test records from their official splits. It downloads originals from their recorded public URLs, keeps attribution/licence references, checks dimensions and the original DMS orientation descriptor, and writes `pilot_manifest.csv`. Missing URLs, moved photographs, aspect-ratio differences and failed orientation checks are logged and excluded. Availability of original image URLs may affect the accepted subset.

The manifest records accepted and excluded pairs. Visual review of representative image-mask pairs is required before optimisation. Both training and validation partitions must contain accepted records. Selection of the first records constitutes a functional pilot rather than a balanced or representative benchmark; larger experiments require a documented sampling strategy.

### Server rate limits and resuming

New photo requests are spaced by two seconds by default. Use `--delay 5` for a slower run. On HTTP 429, the script saves progress and stops immediately; the message includes the server's Retry-After header when supplied. Wait at least that interval before retrying. If no interval is supplied, retry later rather than repeatedly restarting.

Rerun the same preparation command to resume. Complete originals and prepared images are reused, image/mask checks still run, and existing manifest rows are retained and updated by split and image ID. Failed requests are not accepted as training data. Progress is saved after each processed row. Keep the manifest closed in spreadsheet applications while the script runs.

### Optional Open Images mirror

CVDF provides a public mirror of the Open Images bounding-box subset, resized to a maximum longest side of 1024 pixels. It does not contain every DMS photograph. The pilot can retrieve exact ImageIDs from this mirror instead of repeatedly requesting rate-limited originals:

```powershell
.venv\Scripts\python.exe training/prepare_dms_pilot.py --data datasets/dms/local_data/DMS_v1 --train 200 --validation 50 --test 25 --delay 5 --source cvdf
```

The downloader looks up the image ID across the mirror's train, validation and test directories; these source directories do not determine the DMS split. Existing DMS split assignments are preserved. Only HTTP 404 triggers a lookup in another source directory; rate limits and access errors stop or exclude the request. Download URLs are recorded separately from original attribution URLs in the manifest. The same dimension and orientation/content checks apply. Review accepted image/mask pairs visually. Unavailable or mismatched photographs remain excluded.

Source: https://github.com/cvdfoundation/open-images-dataset . Mirror lookup and stop behaviour have been checked with simulated responses; full recovery on the user's network has not been verified.

## Optimisation and validation

```powershell
.venv\Scripts\python.exe training/train_dms.py --data datasets/dms/local_data/DMS_v1 --epochs 3 --size 256 --batch-size 2
```

Pretrained torchvision weights are downloaded at initial execution. The script remaps dataset IDs to the 46 model channels, ignores unsupported labels, uses the accepted training records, evaluates on validation records, and saves the checkpoint with the best validation mean IoU. It freezes batch-normalisation statistics for this small-batch pilot. The three-epoch configuration is intended to verify pipeline operation; production suitability requires further experimentation and evaluation.

Expected outputs are written to `training/runs/dms-pilot/`:
- `best.pt`: PyTorch model checkpoint and label mapping.
- `history.csv`: training loss, validation loss and validation mean IoU per epoch.
- `validation_per_class.csv`: IoU for each model class, blank when absent from both predictions and targets.
- `validation_confusion_matrix.csv`: pixel-level confusion matrix.

The test partition is reserved for final evaluation after configuration selection. It is excluded from optimisation and hyperparameter selection:

```powershell
.venv\Scripts\python.exe training/train_dms.py --data datasets/dms/local_data/DMS_v1 --size 256 --batch-size 2 --evaluate-test
```

Evaluation requires the training run's `--size` and `--output` settings. Checkpoints must originate from a trusted source. The pilot metric includes classes present in the targets or predictions and is not a reproduction of Apple's published benchmark.

## Training-history visualisation

The following analysis reads the training-history file produced by a completed run:

```python
import pandas as pd
import matplotlib.pyplot as plt
history = pd.read_csv('training/runs/dms-pilot/history.csv')
history.plot(x='epoch', y=['train_loss', 'validation_loss'])
plt.show()
history.plot(x='epoch', y='validation_mean_iou')
plt.show()
```

## Deployment boundary

The browser camera in `docs/index.html` currently uses CLIP; checkpoint generation does not modify that application. The trained model needs an inference API hosted on suitable compute, or a verified browser-compatible conversion. GitHub Pages cannot execute the PyTorch model. Camera integration, mobile performance testing, model export and hosting are not implemented by these scripts.

## Implementation status

The scripts passed syntax checks, label-ID mapping checks and dataset-path boundary checks. End-to-end PyTorch execution and GPU training have not been validated. Image retrieval, alignment and runtime compatibility require verification in the target environment. The repository contains training code but no recorded completed training experiment.
