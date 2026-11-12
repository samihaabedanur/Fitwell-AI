# Fitwell AI

Fitwell AI investigates material identification and material information workflows for architectural and interior design. The repository brings together a camera prototype, external research datasets, exploratory analysis and a preliminary segmentation-training pipeline.

## Project components

| Component | Location | Current scope |
| --- | --- | --- |
| Material camera | [docs/](docs/) | Browser-based material suggestions using pretrained CLIP and texture tracking |
| Research datasets | [datasets/](datasets/) | Source documentation, CSV tables, sample files and archived releases |
| Exploratory analysis | [notebooks/](notebooks/) | Six executed notebooks with descriptive tables and figures |
| Segmentation training | [training/](training/) | DMS preparation and pilot-training scripts; end-to-end execution pending |

The camera prototype classifies sampled image regions and overlays provisional labels. The boxes represent the regions examined rather than verified material boundaries. Recognition accuracy and mobile performance have not been systematically evaluated.

## Repository organisation

- `docs/index.html`: camera interface and browser-side recognition.
- `datasets/`: dataset-specific documentation, provenance and tabular exports.
- `notebooks/`: exploratory analyses of the available dataset records.
- `training/`: image preparation, label remapping and pilot segmentation training.
- `.github/workflows/`: dataset archival and integrity-verification workflows.

Large dataset archives are available through [GitHub Releases](https://github.com/samihaabedanur/Fitwell-AI/releases). Their contents and limitations are documented in the corresponding dataset directories.

## Reproducibility

Notebook dependencies are listed in `notebooks/requirements.txt`; training dependencies are listed separately in `training/requirements.txt`. The dataset source records identify upstream versions and licences. Third-party sample code is retained with its original notices.

The analysis notebooks describe dataset structure and coverage. They do not constitute training or evaluation of the camera prototype. Training scripts are available, but a completed training run and deployment of a custom material model have not been recorded.

## Trained live camera in VS Code

Run the trained checkpoint with a local webcam from the repository root:

```powershell
.venv\Scripts\python.exe -m pip install -r camera_requirements.txt
.venv\Scripts\python.exe camera_app.py
```

The window continuously filters for relevant interior materials, then draws a box and trained material name over each selected region.

Click a material box in the local camera window to see its ÖKOBAUDAT GWP-total lookup, unit, lifecycle module and source-record count. These are research summaries; a complete environmental assessment still depends on the product, quantity and full lifecycle modules.

## Camera prototype

The interface is served through GitHub Pages from the `main` branch and `/docs` directory. Camera access requires an HTTPS connection, or localhost during development, and browser permission.

The current recogniser is `Xenova/clip-vit-base-patch32`, loaded through Transformers.js. Model and runtime assets are retrieved from Hugging Face and jsDelivr. Camera frames are processed in the browser by the current implementation.

## Data rights

The repository licence applies to project code where applicable. External datasets, photographs, model weights and third-party code remain subject to their respective licences and attribution requirements. Dataset-specific terms are recorded in [datasets/](datasets/).
