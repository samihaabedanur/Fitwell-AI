"""Match downloaded OpenSurfaces photos to valid material-shape annotations."""
import csv, json
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parent
META = ROOT / "local_data/extracted/opensurfaces"
IMAGE_ROOT = Path(r"E:\Fitwell-OpenSurfaces")

with (IMAGE_ROOT / "photo_download_manifest.csv").open(encoding="utf-8") as f:
    photos = {int(r["photo_id"]): r for r in csv.DictReader(f) if r["status"] in {"downloaded", "existing"}}
substances = {int(x["pk"]): x["fields"] for x in json.loads((META / "shapes.shapesubstance.json").read_text(encoding="utf-8"))}
valid_labels = {k: v["name"] for k, v in substances.items() if v.get("active") and not v.get("fail") and v.get("name") not in {"I can't tell", "More than one material", "Not on list"}}
matched = defaultdict(list)
for shape in json.loads((META / "shapes.materialshape.json").read_text(encoding="utf-8")):
    f = shape["fields"]; photo_id = f.get("photo"); label = valid_labels.get(f.get("substance"))
    if photo_id in photos and label and not f.get("invalid") and f.get("segments"):
        matched[photo_id].append((shape["pk"], label, f.get("area"), f.get("image_bbox")))

rows = []
for photo_id, annotations in matched.items():
    labels = sorted({x[1] for x in annotations})
    rows.append({"photo_id": photo_id, "image_path": photos[photo_id]["image_path"], "annotation_count": len(annotations), "material_labels": "|".join(labels), "shape_ids": "|".join(str(x[0]) for x in annotations)})
out = ROOT / "local_data/opensurfaces_matched_annotations.csv"
with out.open("w", newline="", encoding="utf-8") as f:
    writer = csv.DictWriter(f, fieldnames=rows[0] if rows else ["photo_id", "image_path", "annotation_count", "material_labels", "shape_ids"]); writer.writeheader(); writer.writerows(sorted(rows, key=lambda x: x["photo_id"]))
print(f"Downloaded photos: {len(photos)}")
print(f"Photos with valid material annotations: {len(rows)}")
print(f"Valid material shapes matched: {sum(int(x['annotation_count']) for x in rows)}")
print(f"Wrote: {out}")
