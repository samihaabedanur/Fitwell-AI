# MatFuse sample materials

## Source and scope

Source repository: https://github.com/giuvecchio/matfuse

Recorded source revision: `a699a2187b44256cbe7d170b11ee3fad653e7683`

This directory contains the five sample materials distributed with MatFuse: `asphalt_floor`, `castle_brick`, `clean_pebbles`, `grey_roof` and `old_wood_floor`. The collection comprises 35 unmodified source files, totalling 2,148,395 bytes.

The full MatFuse training dataset is not included. The authors describe training sources based on Deschaintre et al. (2018) and Poly Haven, and identify [MatSynth](https://gvecchio.com/matsynth) as an alternative resource for broader material-generation research.

## File structure

Each sample includes diffuse, normal, roughness and specular maps, a sketch, a rendered preview and JSON metadata.

| File or directory | Description |
| --- | --- |
| `sample_materials/` | Original sample files |
| `samples.csv` | Sample identifiers, source tags, palettes and file references |
| `files.csv` | File sizes, Git blob hashes and source URLs |
| `source.json` | Provenance and collection scope |
| `LICENSE.upstream` | Original repository licence |

## Research use and analysis

The samples support examination of material-map structure, metadata and rendering representations. [Notebook 02](../../notebooks/02_matfuse_analysis.ipynb) reports the sample inventory and storage distribution.

MatFuse concerns material generation rather than direct scene classification. Its rendering maps represent distinct surface properties and are not interchangeable with RGB camera photographs. The five samples have not been used to train the Fitwell camera.

## Attribution and licence

Giuseppe Vecchio, Renato Sortino, Simone Palazzo and Concetto Spampinato. **MatFuse: Controllable Material Generation with Diffusion Models.** CVPR 2024, pp. 4429–4438.

- Paper: https://arxiv.org/abs/2308.11408
- Project: https://gvecchio.com/matfuse/
- Model weights, not included: https://huggingface.co/gvecchio/MatFuse

The upstream repository's MIT notice is retained unchanged. Separately distributed datasets and model weights remain subject to their own terms.
