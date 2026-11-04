# Dataset analysis notebooks

Open a notebook in VS Code with its Python and Jupyter extensions. Select a Python environment, then run:

```bash
python -m pip install -r notebooks/requirements.txt
```

Choose **Run All**. The notebooks locate the repository automatically from its root or a subfolder. CSV files are read from `datasets/`. Image archives are not downloaded automatically.

- `01_dtd_analysis.ipynb`: real category counts and image-index checks. Texture attributes are not material identities.
- `02_matfuse_analysis.ipynb`: five sample materials, tags and file-size analysis. Not the unreleased training set.
- `03_opensurfaces_analysis.ipynb`: official archive inventory and available annotation vocabularies. File sizes are not material-frequency statistics.
- `04_oekobaudat_analysis.ipynb`: missing-data check and an empty input schema. Add your real export as `datasets/oekobaudat/environmental_records.csv`; never treat template rows as observations.

Each notebook includes saved outputs from execution against the committed tables. None performs camera training or reports model accuracy. Existing datasets are preserved.

- `05_dms_analysis.ipynb`: DMS material taxonomy, 46-class model-channel mapping, and measured archive-directory file counts. Dataset is non-commercial; RGB photos are obtained separately.
