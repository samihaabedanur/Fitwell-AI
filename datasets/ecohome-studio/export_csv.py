"""Export factual option tables and a source-file index from a pinned EcoHome revision."""
import argparse
import csv
import json
import re
from pathlib import Path
from urllib.request import Request, urlopen

SOURCE = 'kasimsuh/ecohome-studio'
REVISION = 'ab640555f0c5f7bc63b0da9d5d46d5a6d5198f2f'


def read_url(url):
    with urlopen(Request(url, headers={'User-Agent': 'Fitwell-source-index/1.0'}), timeout=60) as response:
        return response.read().decode('utf-8')


def quoted(text):
    return re.findall(r'"([^"\\]*)"', text)


def parse_options(schema, constants):
    materials = []
    design = []
    for field in ['facadeMaterial', 'roofMaterial']:
        match = re.search(r'\b' + field + r':\s*z\.enum\(\[([^\]]+)\]\)', schema)
        if not match:
            raise ValueError('Missing source enum: ' + field)
        for value in quoted(match.group(1)):
            row = {'field': field, 'value': value, 'record_type': 'application_option', 'source_path': 'lib/domain/home-concept-schema.ts', 'source_revision': REVISION}
            materials.append(row)
    for field in ['floorPlanRoomTypeValues', 'roofTypeValues', 'openingWallValues', 'upgradeCategoryValues', 'impactLevelValues']:
        match = re.search(r'export const ' + field + r'\s*=\s*\[([^\]]+)\]', schema)
        if not match:
            raise ValueError('Missing source enum: ' + field)
        for value in quoted(match.group(1)):
            design.append({'field': field, 'value': value, 'record_type': 'application_option', 'source_path': 'lib/domain/home-concept-schema.ts', 'source_revision': REVISION})
    options = {}
    for field in ['climateOptions', 'budgetOptions']:
        start = constants.index('export const ' + field)
        end = constants.index('\n];', start)
        records = re.findall(r'\{\s*value:\s*"([^"]+)"\s*,\s*label:\s*"([^"]+)"', constants[start:end])
        if not records:
            raise ValueError('No configuration options found: ' + field)
        options[field] = [{'value':v, 'label':label, 'record_type':'application_option', 'source_path':'lib/domain/constants.ts', 'source_revision':REVISION} for v,label in records]
    return materials, design, options


def save(path, rows):
    if not rows:
        raise ValueError('Empty export: ' + str(path))
    with path.open('w', newline='', encoding='utf-8') as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0])); w.writeheader(); w.writerows(rows)


def build(output, schema, constants, tree):
    output.mkdir(parents=True, exist_ok=True)
    if tree.get('truncated'):
        raise ValueError('Incomplete source tree')
    materials, design, options = parse_options(schema, constants)
    assert len(materials) == 10
    save(output / 'material_options.csv', materials)
    save(output / 'design_options.csv', design)
    save(output / 'climate_options.csv', options['climateOptions'])
    save(output / 'budget_options.csv', options['budgetOptions'])
    selected = []
    app_paths = {'lib/domain/constants.ts', 'lib/domain/home-concept-schema.ts', 'lib/domain/mock-data.ts', 'lib/domain/sample-project.ts', 'lib/domain/sample-structured-home.ts', 'lib/domain/derive-report-metrics.ts'}
    for item in tree['tree']:
        p = item['path']
        if item['type'] != 'blob':
            continue
        kind = ('reference_pdf' if p.startswith('rag-docs/') and p.endswith('.pdf') else
                'guidance_note' if p.startswith('lib/rag/knowledge/') and p.endswith('.md') else
                'application_reference' if p in app_paths else None)
        if kind:
            selected.append({'path': p, 'resource_type': kind, 'size_bytes': item['size'], 'git_blob_sha':item['sha'], 'source_revision':REVISION, 'source_url': f'https://github.com/{SOURCE}/blob/{REVISION}/{p.replace(" ", "%20")}', 'copied_to_fitwell':False})
    save(output / 'resource_inventory.csv', selected)
    save(output / 'knowledge_sources.csv', [r for r in selected if r['resource_type'] in {'reference_pdf','guidance_note'}])
    print('Material options:', len(materials), '| Design options:', len(design), '| Indexed resources:', len(selected))
    print('Tables describe source application configuration; no measurements or training images are created.')


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--output', type=Path, default=Path(__file__).resolve().parent)
    a = p.parse_args()
    prefix = f'https://raw.githubusercontent.com/{SOURCE}/{REVISION}/'
    schema = read_url(prefix + 'lib/domain/home-concept-schema.ts')
    constants = read_url(prefix + 'lib/domain/constants.ts')
    tree = json.loads(read_url(f'https://api.github.com/repos/{SOURCE}/git/trees/{REVISION}?recursive=1'))
    build(a.output, schema, constants, tree)


if __name__ == '__main__':
    main()
