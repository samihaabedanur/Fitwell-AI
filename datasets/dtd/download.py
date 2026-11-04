"""Download the pinned Voxel51 DTD image dataset; no camera training is performed."""
import argparse
import csv
import hashlib
import json
from pathlib import Path


def validate_index(root):
    with (root / 'images.csv').open(newline='', encoding='utf-8') as f:
        rows = list(csv.DictReader(f))
    if len(rows) != 5640 or len({r['texture_label'] for r in rows}) != 47:
        raise ValueError('Expected 5,640 indexed images across 47 texture categories')
    if len({r['relative_path'] for r in rows}) != len(rows):
        raise ValueError('Duplicate image paths in index')
    return rows


def main():
    root = Path(__file__).resolve().parent
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, default=root / 'local_data')
    parser.add_argument('--limit', type=int, help='Download only the first N indexed images for a quick check')
    parser.add_argument('--check-index', action='store_true', help='Validate the index without downloading')
    args = parser.parse_args()
    rows = validate_index(root)
    if args.check_index:
        print('Index OK: 5,640 unique image paths; 47 categories')
        return
    if args.limit is not None and args.limit <= 0:
        parser.error('--limit must be positive')
    try:
        from huggingface_hub import snapshot_download
    except ImportError:
        raise SystemExit('Install first: python -m pip install -r requirements.txt')
    info = json.loads((root / 'source.json').read_text(encoding='utf-8'))
    selected = rows[:args.limit] if args.limit else rows
    patterns = ['README.md', 'metadata.json', 'samples.json', 'fiftyone.yml']
    patterns += [r['relative_path'] for r in selected] if args.limit else ['data/**']
    args.output.mkdir(parents=True, exist_ok=True)
    snapshot_download(repo_id=info['repo_id'], repo_type='dataset', revision=info['revision'],
                      local_dir=str(args.output), allow_patterns=patterns)
    checksums = []
    for row in selected:
        file = args.output / row['relative_path']
        if not file.is_file() or file.stat().st_size == 0:
            raise RuntimeError(f'Missing or empty image: {file}')
        with file.open('rb') as f:
            sha = hashlib.sha256(f.read()).hexdigest()
        checksums.append({**row, 'sha256': sha, 'size_bytes': file.stat().st_size})
    with (args.output / 'download_inventory.csv').open('w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=list(checksums[0]))
        writer.writeheader()
        writer.writerows(checksums)
    print(f'Checked {len(checksums)} downloaded images in {args.output.resolve()}')
    print('Texture labels are not material identities. No model has been trained.')


if __name__ == '__main__':
    main()
