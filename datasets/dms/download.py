"""Download an official DMS archive locally; verify it without executing its contents."""
import argparse
import csv
import hashlib
from pathlib import Path
from urllib.request import urlopen
import zipfile


def main():
    root = Path(__file__).resolve().parent
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--resource', choices=['fused_labels', 'pretrained_model', 'raw_polygons'], default='fused_labels')
    parser.add_argument('--output', type=Path, default=root / 'local_data')
    args = parser.parse_args()
    with (root / 'downloads.csv').open(newline='', encoding='utf-8') as f:
        resources = {row['resource']: row for row in csv.DictReader(f)}
    source = resources[args.resource]
    args.output.mkdir(parents=True, exist_ok=True)
    target = args.output / source['url'].rsplit('/', 1)[-1]
    partial = target.with_suffix('.zip.part')
    print('Downloading', source['url'])
    digest = hashlib.sha256()
    with urlopen(source['url'], timeout=120) as response, partial.open('wb') as out:
        while chunk := response.read(1024 * 1024):
            out.write(chunk)
            digest.update(chunk)
    with zipfile.ZipFile(partial) as archive:
        if not archive.infolist():
            raise RuntimeError('Empty archive')
        bad = archive.testzip()
        if bad:
            raise RuntimeError('Corrupt ZIP entry: ' + bad)
    partial.replace(target)
    target.with_suffix('.zip.sha256').write_text(digest.hexdigest() + '  ' + target.name + '\n')
    print('Verified:', target)
    print('No extraction, model execution or training was performed.')


if __name__ == '__main__':
    main()
