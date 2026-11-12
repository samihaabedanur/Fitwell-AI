"""Download OpenSurfaces photos referenced by the extracted metadata."""
import argparse, csv, json, time
from pathlib import Path
from urllib.request import Request, urlopen
from urllib.error import HTTPError, URLError

ROOT = Path(__file__).resolve().parent
META = ROOT / "local_data/extracted/opensurfaces/photos.photo.json"
OUT = ROOT / "local_data/images"

def main():
    p = argparse.ArgumentParser(); p.add_argument("--start", type=int, default=0); p.add_argument("--limit", type=int, default=100); p.add_argument("--delay", type=float, default=.2); p.add_argument("--output", type=Path, default=Path("datasets/opensurfaces/local_data"))
    a = p.parse_args(); output_root = a.output.resolve(); out = output_root / "images"; out.mkdir(parents=True, exist_ok=True)
    photos = json.loads(META.read_text(encoding="utf-8"))
    rows = []
    for item in photos[a.start:a.start + a.limit]:
        fields = item["fields"]; image_id = item["pk"]; relative = fields.get("image_orig", ""); target = out / f"{image_id}.jpg"; url = "http://labelmaterial.s3.amazonaws.com/" + relative
        status = "existing" if target.exists() else "failed"; error = ""
        if not target.exists():
            try:
                request = Request(url, headers={"User-Agent": "Fitwell-AI research downloader"})
                with urlopen(request, timeout=60) as response: target.write_bytes(response.read())
                status = "downloaded"
            except (HTTPError, URLError, OSError) as exc:
                error = str(exc); status = "failed"
            time.sleep(a.delay)
        rows.append({"photo_id": image_id, "image_path": str(target), "source_url": url, "status": status, "error": error})
        print(image_id, status)
    manifest = output_root / "photo_download_manifest.csv"
    if manifest.exists():
        with manifest.open(newline="", encoding="utf-8") as f:
            previous = list(csv.DictReader(f))
        combined = {int(row["photo_id"]): row for row in previous}
        combined.update({int(row["photo_id"]): row for row in rows})
        rows = [combined[key] for key in sorted(combined)]
    with manifest.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=rows[0]); writer.writeheader(); writer.writerows(rows)
    print("Manifest:", manifest)

if __name__ == "__main__": main()
