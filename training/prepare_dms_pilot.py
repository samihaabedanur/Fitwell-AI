"""Retrieve a small, checked DMS photo subset. Dataset: CC BY-NC 4.0."""
import argparse
import csv
import gzip
import importlib.util
import json
import time
from urllib.error import HTTPError
from pathlib import Path
from urllib.request import Request, urlopen

from PIL import Image, ImageOps
import numpy as np


def inside(root, relative):
    path = (root / relative).resolve()
    if not path.is_relative_to(root.resolve()):
        raise ValueError('Path is outside dataset directory')
    return path


class RateLimited(Exception):
    pass


def download_original(url, destination, delay):
    """Reuse complete downloads and stop immediately on server rate limits."""
    if destination.is_file():
        return
    time.sleep(delay)
    partial = destination.with_suffix('.part')
    try:
        with urlopen(Request(url, headers={'User-Agent': 'Fitwell-research-pilot/1.0'}), timeout=30) as response, partial.open('wb') as f:
            total = 0
            while chunk := response.read(1024 * 1024):
                total += len(chunk)
                if total > 60 * 1024 * 1024:
                    raise ValueError('Original exceeds 60 MB download limit')
                f.write(chunk)
        partial.replace(destination)
    except HTTPError as error:
        if error.code == 429:
            wait = error.headers.get('Retry-After', 'not specified') if error.headers else 'not specified'
            raise RateLimited(f'HTTP 429: server rate limit; Retry-After: {wait}. Stop and retry later.') from error
        raise
    finally:
        partial.unlink(missing_ok=True)


COLUMNS = ['split', 'image_id', 'image_path', 'label_path', 'source_url', 'source_license', 'status', 'detail']


def save_manifest(path, rows):
    temporary = path.with_suffix('.tmp')
    with temporary.open('w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=COLUMNS)
        writer.writeheader()
        writer.writerows(rows.values())
    temporary.replace(path)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--data', type=Path, required=True)
    parser.add_argument('--train', type=int, default=200)
    parser.add_argument('--validation', type=int, default=50)
    parser.add_argument('--test', type=int, default=25)
    parser.add_argument('--delay', type=float, default=2.0, help='Seconds between new photo requests (minimum 1)')
    args = parser.parse_args()
    if not np.isfinite(args.delay) or args.delay < 1:
        parser.error('--delay must be finite and at least 1 second')
    if min(args.train, args.validation, args.test) < 1:
        parser.error('All split limits must be positive')
    root = args.data.resolve()
    repo = Path(__file__).resolve().parents[1]
    spec = importlib.util.spec_from_file_location('dms_image_checks', repo / 'datasets/dms/upstream/check_images.py')
    checks = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(checks)
    with gzip.open(root / 'info.json.gz', 'rt', encoding='utf-8') as f:
        records = json.load(f)
    if not isinstance(records, list):
        raise ValueError('Expected the DMS info.json.gz list')
    limits = {'train': args.train, 'validation': args.validation, 'test': args.test}
    attempted = dict.fromkeys(limits, 0)
    manifest = root / 'pilot_manifest.csv'
    outcomes = {}
    if manifest.is_file():
        with manifest.open(newline='', encoding='utf-8') as f:
            for previous in csv.DictReader(f):
                outcomes[(previous['split'], previous['image_id'])] = previous
    seen = set()
    originals = root / 'pilot_originals'
    originals.mkdir(exist_ok=True)
    for item in records:
        parts = Path(item['image_path']).parts
        split = next((s for s in limits if s in parts), None)
        if split is None or attempted[split] >= limits[split]:
            continue
        attempted[split] += 1
        image_path = inside(root, item['image_path'])
        label_path = inside(root, item['label_path'])
        url = item['openimages_metadata'].get('OriginalURL', '')
        image_id = str(item['openimages_metadata'].get('ImageID') or image_path.stem)
        row = {'split': split, 'image_id': image_id, 'image_path': str(image_path.relative_to(root)), 'label_path': str(label_path.relative_to(root)), 'source_url': url, 'source_license': item['openimages_metadata'].get('License', ''), 'status': '', 'detail': ''}
        try:
            if image_id in seen:
                raise ValueError('Duplicate image ID across selected records')
            seen.add(image_id)
            if not label_path.is_file():
                raise FileNotFoundError('Matching mask not found')
            if not image_path.exists():
                if not url.startswith(('https://', 'http://')):
                    raise ValueError('Original image URL missing')
                original = originals / f'{split}_{image_path.stem}.img'
                download_original(url, original, args.delay)
                with Image.open(original) as source:
                    image = ImageOps.exif_transpose(source).convert('RGB')
                with Image.open(label_path) as label:
                    target_size = label.size
                if abs((image.width / image.height) / (target_size[0] / target_size[1]) - 1) > .01:
                    raise ValueError('Aspect ratio does not match mask; inspect manually')
                image = image.resize(target_size, Image.Resampling.LANCZOS)
                image_path.parent.mkdir(parents=True, exist_ok=True)
                image.save(image_path, quality=95)
            with Image.open(image_path) as image, Image.open(label_path) as label:
                if image.size != label.size:
                    raise ValueError('Image and mask dimensions differ')
                if np.asarray(label).ndim != 2:
                    raise ValueError('Expected a single-channel mask')
            _, descriptor = checks.rotation_descriptor(str(image_path))
            if not checks.rotation_descriptor_match(descriptor, np.asarray(item['rotation_descriptor']), 50, 5, 30):
                raise ValueError('Orientation/content check failed; inspect manually')
            row['status'] = 'accepted'
        except RateLimited as e:
            row['status'], row['detail'] = 'excluded', str(e)
            outcomes[(split, image_id)] = row
            save_manifest(manifest, outcomes)
            print(str(e), flush=True)
            print('Progress saved. No more requests were sent. Rerun the same command later; downloaded files will be reused.', flush=True)
            break
        except Exception as e:
            row['status'], row['detail'] = 'excluded', str(e)
        outcomes[(split, image_id)] = row
        save_manifest(manifest, outcomes)
        print(split, attempted[split], row['status'], image_path.name, flush=True)
    save_manifest(manifest, outcomes)
    print('Manifest:', manifest)
    for split in limits:
        n = sum(r['status'] == 'accepted' and r['split'] == split for r in outcomes.values())
        print(split, 'accepted:', n, 'attempted:', attempted[split])
    print('Excluded rows are not used for training. Review image licences before use.')


if __name__ == '__main__':
    main()
