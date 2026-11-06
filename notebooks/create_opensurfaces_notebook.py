import json
from pathlib import Path


def md(text):
    return {"cell_type": "markdown", "metadata": {}, "source": text.splitlines(True)}


def code(text):
    return {"cell_type": "code", "execution_count": None, "metadata": {}, "outputs": [], "source": text.splitlines(True)}


cells = [
    md("""# OpenSurfaces material recognition workflow

This notebook keeps the preparation work together: existing DMS results, raw OpenSurfaces downloads, annotation matching, cleaning, and the prepared image/mask data used for the next training run. The tables and plots are generated from the files in this project and the research dataset stored on the E: drive.
"""),
    code("""from pathlib import Path
import json
import pandas as pd
import matplotlib.pyplot as plt
from IPython.display import display

ROOT = Path.cwd()
if not (ROOT / 'datasets').exists():
    ROOT = ROOT.parent
PROJECT = ROOT / 'datasets' / 'opensurfaces'
EXTERNAL = Path(r'E:/Fitwell-OpenSurfaces')
plt.style.use('seaborn-v0_8-whitegrid')
print('Project:', ROOT)
print('OpenSurfaces files:', EXTERNAL)
"""),
    md("## 1. Existing DMS model results"),
    code("""history_path = ROOT / 'training' / 'runs' / 'dms-all-research' / 'history.csv'
metrics_path = ROOT / 'training' / 'runs' / 'dms-all-research' / 'test_metrics.json'
if history_path.exists():
    dms_history = pd.read_csv(history_path)
    display(dms_history)
    fig, axes = plt.subplots(1, 2, figsize=(12, 4))
    axes[0].plot(dms_history['epoch'], dms_history['train_loss'], marker='o', label='train loss')
    validation_loss_column = 'validation_loss' if 'validation_loss' in dms_history.columns else 'val_loss'
    axes[0].plot(dms_history['epoch'], dms_history[validation_loss_column], marker='o', label='validation loss')
    axes[0].set(title='DMS loss by epoch', xlabel='Epoch', ylabel='Loss')
    axes[0].legend()
    iou_column = 'validation_mean_iou' if 'validation_mean_iou' in dms_history.columns else 'val_mean_iou'
    axes[1].plot(dms_history['epoch'], dms_history[iou_column], marker='o', color='darkgreen')
    axes[1].set(title='DMS validation mean IoU', xlabel='Epoch', ylabel='Mean IoU')
    plt.tight_layout()
    plt.show()
else:
    print('DMS history is not available yet:', history_path)
if metrics_path.exists():
    dms_metrics = json.loads(metrics_path.read_text(encoding='utf-8'))
    display(pd.DataFrame([dms_metrics]))
"""),
    md("## 2. Raw OpenSurfaces photos"),
    code("""raw_manifest_path = EXTERNAL / 'photo_download_manifest.csv'
if raw_manifest_path.exists():
    raw_photos = pd.read_csv(raw_manifest_path)
    print(f'Raw download rows: {len(raw_photos):,}')
    display(raw_photos.head(10))
    status_counts = raw_photos['status'].value_counts(dropna=False)
    display(status_counts.rename_axis('status').reset_index(name='photos'))
    status_counts.plot(kind='bar', figsize=(8, 4), title='Raw OpenSurfaces download status')
    plt.xlabel('Status'); plt.ylabel('Photos'); plt.tight_layout(); plt.show()
else:
    print('Download manifest not found:', raw_manifest_path)
"""),
    md("## 3. Match photos with material annotations"),
    code("""matched_path = PROJECT / 'local_data' / 'opensurfaces_matched_annotations.csv'
if matched_path.exists():
    matched = pd.read_csv(matched_path)
    print(f'Matched annotation rows: {len(matched):,}')
    display(matched.head(10))
    print('Photos with annotations:', matched['photo_id'].nunique())
    label_counts = matched['material_labels'].fillna('').str.split('|').explode().replace('', pd.NA).dropna().value_counts().head(20).sort_values()
    print('Material labels:', len(label_counts))
    label_counts.plot(kind='barh', figsize=(9, 6), title='Matched OpenSurfaces material labels')
    plt.xlabel('Annotation rows'); plt.tight_layout(); plt.show()
else:
    print('Matched annotation table not found:', matched_path)
"""),
    md("## 4. Cleaned image and mask tables"),
    code("""prepared_manifest_path = EXTERNAL / 'prepared' / 'manifest.csv'
if prepared_manifest_path.exists():
    prepared = pd.read_csv(prepared_manifest_path)
    print(f'Prepared image/mask pairs: {len(prepared):,}')
    display(prepared.head(10))
    split_counts = prepared['split'].value_counts()
    split_counts.plot(kind='bar', figsize=(7, 4), title='Cleaned OpenSurfaces split')
    plt.xlabel('Split'); plt.ylabel('Image/mask pairs'); plt.tight_layout(); plt.show()
    clean_labels = prepared['labels'].fillna('').str.split('|').explode().replace('', pd.NA).dropna().value_counts().sort_values()
    clean_labels.plot(kind='barh', figsize=(9, 6), title='Cleaned material labels')
    plt.xlabel('Image/mask pairs'); plt.tight_layout(); plt.show()
    display(prepared.groupby(['split', 'labels']).size().reset_index(name='pairs'))
else:
    print('Prepared manifest not found:', prepared_manifest_path)
"""),
    md("## 5. OpenSurfaces training results"),
    code("""print('The DMS model results are shown above.')
print('OpenSurfaces photos have been matched, invalid/ambiguous labels removed, and masks prepared.')
opensurfaces_run = ROOT / 'training' / 'runs' / 'opensurfaces-research'
opensurfaces_history = opensurfaces_run / 'history.csv'
if opensurfaces_history.exists():
    opensurfaces_results = pd.read_csv(opensurfaces_history)
    display(opensurfaces_results)
    fig, axes = plt.subplots(1, 2, figsize=(12, 4))
    axes[0].plot(opensurfaces_results['epoch'], opensurfaces_results['train_loss'], marker='o', label='train loss')
    axes[0].plot(opensurfaces_results['epoch'], opensurfaces_results['validation_loss'], marker='o', label='validation loss')
    axes[0].set(title='OpenSurfaces loss by epoch', xlabel='Epoch', ylabel='Loss'); axes[0].legend()
    axes[1].plot(opensurfaces_results['epoch'], opensurfaces_results['validation_mean_iou'], marker='o', color='darkgreen')
    axes[1].set(title='OpenSurfaces validation mean IoU', xlabel='Epoch', ylabel='Mean IoU')
    plt.tight_layout(); plt.show()
    print('Best checkpoint:', opensurfaces_run / 'best.pt')
else:
    print('OpenSurfaces training has not been run yet.')
"""),
    md("""## Saved tables and graphs

The generated outputs are saved in `datasets/opensurfaces/analysis/` so they remain visible even before the notebook is run:

- `raw_photo_status_table.csv` and `raw_photo_status.png`
- `matched_annotation_table.csv`, `matched_material_labels_table.csv`, and `matched_material_labels.png`
- `cleaned_image_mask_table.csv`, `cleaned_split_table.csv`, and `cleaned_split.png`

Run **Run All** in VS Code to render the same tables and graphs directly inside this notebook.
"""),
    md("## Research note\n\nThis workflow is for research use. Photo download and dataset use remain subject to the OpenSurfaces licence and attribution requirements."),
]

notebook = {
    "cells": cells,
    "metadata": {"kernelspec": {"display_name": "Python 3", "language": "python", "name": "python3"}, "language_info": {"name": "python", "version": "3"}},
    "nbformat": 4,
    "nbformat_minor": 5,
}

output = Path(__file__).with_name('03_opensurfaces_cleaning_training.ipynb')
output.write_text(json.dumps(notebook, indent=1), encoding='utf-8')
print(f'Created {output}')
