# MatFuse sample materials

Source: https://github.com/giuvecchio/matfuse
Pinned source commit: `a699a2187b44256cbe7d170b11ee3fad653e7683`

## What is included

This folder includes the five sample materials shipped with the official MatFuse repository: asphalt_floor, castle_brick, clean_pebbles, grey_roof, old_wood_floor. The 35 original files (2,148,395 bytes) are copied unchanged under `sample_materials/`. Each material has diffuse, normal, roughness, specular and sketch PNGs, a rendered preview and metadata JSON. See `files.csv` for file sizes, Git blob hashes and pinned source URLs.

These are samples, **not the full MatFuse training dataset**. The authors' README states that the training data combined Deschaintre et al. (2018) materials with Poly Haven materials and is not planned for release. It recommends MatSynth for collecting a broader training dataset: https://gvecchio.com/matsynth

## Fitwell use

Use these files for studying material maps, previews, synthetic material workflows and future experiments. MatFuse generates material maps; it is not a ready-made live-camera material classifier. Adding these samples does not train or change the existing Fitwell camera. Rendering maps (such as normal and roughness) are not ordinary colour photographs and should not all be treated as interchangeable camera training images.

## Attribution and licence

MatFuse: Controllable Material Generation with Diffusion Models, Giuseppe Vecchio, Renato Sortino, Simone Palazzo and Concetto Spampinato, CVPR 2024, pp. 4429–4438.

Paper: https://arxiv.org/abs/2308.11408
Project: https://gvecchio.com/matfuse/
Weights (not included): https://huggingface.co/gvecchio/MatFuse

The upstream repository carries the MIT licence; its unmodified notice is retained in `LICENSE.upstream`. This notice does not establish licence terms for separately downloaded third-party datasets or model weights. Consult each source's terms before obtaining those resources.
