from pathlib import Path
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

OUT = Path(__file__).parent / 'analysis'
OUT.mkdir(exist_ok=True)
external = Path(r'E:/Fitwell-OpenSurfaces')

photos = pd.read_csv(external / 'photo_download_manifest.csv')
photos['status'].value_counts().rename_axis('status').reset_index(name='photos').to_csv(OUT / 'raw_photo_status_table.csv', index=False)
plt.figure(figsize=(7, 4)); photos['status'].value_counts().plot(kind='bar', title='OpenSurfaces raw photo status'); plt.xlabel('Status'); plt.ylabel('Photos'); plt.tight_layout(); plt.savefig(OUT / 'raw_photo_status.png', dpi=150); plt.close()

matched = pd.read_csv(Path(__file__).parent / 'local_data' / 'opensurfaces_matched_annotations.csv')
matched_table = matched[['photo_id', 'annotation_count', 'material_labels']]
matched_table.to_csv(OUT / 'matched_annotation_table.csv', index=False)
labels = matched['material_labels'].fillna('').str.split('|').explode().replace('', pd.NA).dropna().value_counts().rename_axis('material_label').reset_index(name='annotation_rows')
labels.to_csv(OUT / 'matched_material_labels_table.csv', index=False)
plt.figure(figsize=(9, 6)); labels.head(20).sort_values('annotation_rows').plot(kind='barh', x='material_label', y='annotation_rows', legend=False, title='Matched OpenSurfaces material labels'); plt.tight_layout(); plt.savefig(OUT / 'matched_material_labels.png', dpi=150); plt.close()

prepared = pd.read_csv(external / 'prepared' / 'manifest.csv')
prepared[['image_id', 'labels', 'split', 'status']].to_csv(OUT / 'cleaned_image_mask_table.csv', index=False)
prepared['split'].value_counts().rename_axis('split').reset_index(name='pairs').to_csv(OUT / 'cleaned_split_table.csv', index=False)
plt.figure(figsize=(7, 4)); prepared['split'].value_counts().plot(kind='bar', title='Cleaned OpenSurfaces image/mask split'); plt.xlabel('Split'); plt.ylabel('Pairs'); plt.tight_layout(); plt.savefig(OUT / 'cleaned_split.png', dpi=150); plt.close()

print('Created OpenSurfaces analysis tables and graphs in', OUT)
