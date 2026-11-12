# Dataset analysis notebooks

The notebooks document exploratory analysis of the available Fitwell AI dataset resources. Saved outputs include source inventories, metadata tables and descriptive figures.

## Notebook index

| Notebook | Scope |
| --- | --- |
| [01 — DTD](01_dtd_analysis.ipynb) | Image-index consistency and texture-category balance |
| [02 — MatFuse](02_matfuse_analysis.ipynb) | Sample metadata, file counts and storage distribution |
| [03 — OpenSurfaces](03_opensurfaces_analysis.ipynb) | Archive inventory, material vocabulary and licence definitions |
| [04 — ÖKOBAUDAT](04_oekobaudat_analysis.ipynb) | Source checks, cleaning, tables, graphs and environmental-impact review |
| [05 — DMS](05_dms_analysis.ipynb) | Material taxonomy, model-channel mapping and archive statistics |
| [06 — EcoHome Studio](06_ecohome_studio_analysis.ipynb) | Application configuration tables and indexed reference resources |

The analyses distinguish texture attributes, material vocabulary entries, archive files and environmental records. These quantities are not treated as interchangeable measures of dataset coverage or recognition performance.

## Environment and execution

Dependencies are installed from the repository root:

```bash
python -m pip install -r notebooks/requirements.txt
```

The notebooks can be executed in VS Code with the Python and Jupyter extensions and the selected Python environment. Repository-relative CSV files are located automatically. Image archives are not downloaded during notebook execution.

## Reproducibility and limitations

All six notebooks include saved outputs from execution against the committed tables. The ÖKOBAUDAT notebook reports the absence of source measurements and does not present environmental estimates. Other figures describe the records available to each analysis.

Model optimisation, recognition benchmarking and browser deployment are outside the scope of these notebooks. Preliminary model-training scripts are documented separately in [training/](../training/).
