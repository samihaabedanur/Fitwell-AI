"""Create OpenSurfaces image/mask pairs from downloaded photos and polygons."""
import csv, json, random
from pathlib import Path
from PIL import Image, ImageDraw

ROOT = Path(__file__).resolve().parent; META = ROOT / 'local_data/extracted/opensurfaces'; IMAGE_ROOT = Path(r'E:\Fitwell-OpenSurfaces\images'); OUT = Path(r'E:\Fitwell-OpenSurfaces\prepared')
OUT.mkdir(parents=True, exist_ok=True)
with (Path('datasets/dms/model_classes.csv')).open(newline='', encoding='utf-8') as f: dms = {r['material_name'].lower(): int(r['label_id']) for r in csv.DictReader(f)}
aliases = {'brick': 'Brickwork', 'concrete': 'Concrete', 'glass': 'Glass', 'metal': 'Metal', 'mirror': 'Mirror', 'wood': 'Wood', 'tile': 'Tile', 'ceramic': 'Ceramic', 'asphalt': 'Asphalt', 'carpet': 'Carpet/rug', 'fabric': 'Fabric/cloth', 'paper': 'Paper', 'stone': 'Stone, natural', 'granite/marble': 'Stone, natural', 'painted': 'Paint/plaster/enamel'}
substances = {int(x['pk']): x['fields'] for x in json.loads((META / 'shapes.shapesubstance.json').read_text(encoding='utf-8'))}
shapes = json.loads((META / 'shapes.materialshape.json').read_text(encoding='utf-8'))
by_photo = {}
for item in shapes:
    f = item['fields']; raw = substances.get(f.get('substance'), {}).get('name', ''); key = aliases.get(raw.lower()); label = dms.get(key.lower()) if key else None
    if label and not f.get('invalid') and f.get('vertices') and f.get('triangles'): by_photo.setdefault(int(f['photo']), []).append((item['pk'], label, f['vertices'], f['triangles']))
rows = []
for image_path in IMAGE_ROOT.glob('*.jpg'):
    try: photo_id = int(image_path.stem); annotations = by_photo.get(photo_id, []); 
    except ValueError: continue
    if not annotations: continue
    with Image.open(image_path) as image: size = image.size
    mask = Image.new('L', size, 255); draw = ImageDraw.Draw(mask)
    used = set()
    for shape_id, label, vertices_raw, triangles_raw in annotations:
        try:
            values = list(map(float, vertices_raw.split(','))); vertices = list(zip(values[0::2], values[1::2]))
            triangle_values = list(map(int, triangles_raw.split(','))); triangles = list(zip(triangle_values[0::3], triangle_values[1::3], triangle_values[2::3]))
            for tri in triangles:
                points = [(int(vertices[i][0] * size[0]), int(vertices[i][1] * size[1])) for i in tri]
                draw.polygon(points, fill=label)
            used.add(label)
        except (ValueError, IndexError):
            continue
    if used:
        mask_path = OUT / f'{photo_id}.png'; mask.save(mask_path)
        rows.append({'image_id': photo_id, 'image_path': str(image_path), 'label_path': str(mask_path), 'labels': '|'.join(map(str, sorted(used))), 'status': 'accepted'})
random.Random(42).shuffle(rows); split_at = int(len(rows) * .8)
for i, row in enumerate(rows): row['split'] = 'train' if i < split_at else 'validation'
with (OUT / 'manifest.csv').open('w', newline='', encoding='utf-8') as f:
    writer = csv.DictWriter(f, fieldnames=['image_id','image_path','label_path','labels','split','status']); writer.writeheader(); writer.writerows(rows)
print('Prepared pairs:', len(rows), 'train:', sum(r['split']=='train' for r in rows), 'validation:', sum(r['split']=='validation' for r in rows))
print('Output:', OUT)
