# First DMS training pilot in VS Code (Windows)

This setup fine-tunes a torchvision DeepLabV3-MobileNet model, initialised with pretrained segmentation weights, on DMS photo/mask pairs. It does not fine-tune Apple's TorchScript checkpoint. DMS annotations are CC BY-NC 4.0; original photos retain their licences. This is a non-commercial research pilot.

## 1. Open the repository

Clone Fitwell-AI if needed, then use File → Open Folder and select Fitwell-AI. If it is already cloned, use `git pull` after checking for local changes. All commands below run from the repository root in the VS Code terminal.

## 2. Create a Python environment

Use Python 3.11 for this guide. No PowerShell activation or execution-policy changes are necessary:

```powershell
py -3.11 -m venv .venv
.venv\Scripts\python.exe -m pip install --upgrade pip
.venv\Scripts\python.exe -m pip install -r training/requirements.txt
```

The first install downloads large ML packages. To use an NVIDIA GPU, use the official PyTorch installation selector for a matching CUDA installation: https://pytorch.org/get-started/locally/ . GPU availability depends on the machine and installed build. This code falls back to CPU, which can be very slow.

```powershell
.venv\Scripts\python.exe -c "import torch; print('GPU available:', torch.cuda.is_available())"
```

## 3. Download and extract DMS labels

The downloader uses Python's standard library:

```powershell
.venv\Scripts\python.exe datasets/dms/download.py --resource fused_labels
.venv\Scripts\python.exe -m zipfile -e datasets/dms/local_data/dms_v1_labels.zip datasets/dms/local_data
```

Confirm that `datasets/dms/local_data/DMS_v1` contains `info.json.gz` and `labels/train`, `labels/validation`, `labels/test`.

## 4. Retrieve a small set of original photographs

```powershell
.venv\Scripts\python.exe training/prepare_dms_pilot.py --data datasets/dms/local_data/DMS_v1 --train 200 --validation 50 --test 25
```

This attempts the first 200 training, 50 validation and 25 test records from their official splits. It downloads originals from their recorded public URLs, keeps attribution/licence references, checks dimensions and the original DMS orientation descriptor, and writes `pilot_manifest.csv`. Missing URLs, moved photographs, aspect-ratio differences and failed orientation checks are logged and excluded. Downloads can take time and some original links may be unavailable.

Inspect the manifest and several photo/mask pairs visually. Continue only if both train and validation have accepted pairs. These first-record subsets are a plumbing pilot, not a balanced or representative benchmark. Do not interpret their results as final model quality. Increase the subset only after verifying this first run.

## 5. Train

```powershell
.venv\Scripts\python.exe training/train_dms.py --data datasets/dms/local_data/DMS_v1 --epochs 3 --size 256 --batch-size 2
```

The first run downloads pretrained torchvision weights. The script remaps dataset IDs to the 46 model channels, ignores unsupported labels, uses the accepted training records, evaluates on validation records, and saves the checkpoint with the best validation mean IoU. It freezes batch-normalisation statistics for this small-batch pilot. There are no claims that three epochs or these settings produce a useful production detector.

Outputs under `training/runs/dms-pilot/`:
- `best.pt`: PyTorch model checkpoint and label mapping.
- `history.csv`: actual training loss, validation loss and validation mean IoU per epoch.
- `validation_per_class.csv`: actual IoU for each model class, blank when absent from both predictions and targets.
- `validation_confusion_matrix.csv`: pixel-level confusion matrix.

Do not train against the test set or tune settings based on test performance. After freezing a chosen configuration, evaluate it once:

```powershell
.venv\Scripts\python.exe training/train_dms.py --data datasets/dms/local_data/DMS_v1 --size 256 --batch-size 2 --evaluate-test
```

Use the same `--size` and `--output` as the training run. Use only checkpoints you created or trust. The pilot metric includes classes present in targets or predictions; it is not an official reproduction of Apple's reported benchmark.

## 6. Plot your real training history

Run in a notebook using this environment:

```python
import pandas as pd
import matplotlib.pyplot as plt
history = pd.read_csv('training/runs/dms-pilot/history.csv')
history.plot(x='epoch', y=['train_loss', 'validation_loss'])
plt.show()
history.plot(x='epoch', y='validation_mean_iou')
plt.show()
```

## 7. Connect it to the camera (separate deployment work)

Saving `best.pt` does not update `docs/index.html`. The existing browser camera still uses CLIP. The trained model needs an inference API hosted on suitable compute, or a verified browser-compatible conversion. GitHub Pages cannot execute the PyTorch model. Camera integration, mobile performance testing, model export and hosting are not implemented by these scripts.

## Validation status

The scripts passed syntax checks, label-ID mapping checks and dataset-path boundary checks. This environment has no torch/torchvision runtime, so no end-to-end training or GPU test has been performed here. Original-image downloads and image/mask alignment must be verified on your machine. Do not treat the presence of training code as evidence that a model has already been trained.
