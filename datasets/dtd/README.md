# Describable Textures Dataset

## Source and scope

The Describable Textures Dataset (DTD) is included through the [Voxel51 distribution on Hugging Face](https://huggingface.co/datasets/Voxel51/Describable-Textures-Dataset). The [original project](https://www.robots.ox.ac.uk/~vgg/data/dtd/) was developed by M. Cimpoi, S. Maji, I. Kokkinos, S. Mohamed and A. Vedaldi.

The indexed collection contains 5,640 images in 47 texture categories, with 120 images per category. The source revision is recorded in `source.json`.

## Files

| File | Description |
| --- | --- |
| `images.csv` | Image paths and texture labels derived from source filename prefixes |
| `categories.csv` | Image count for each texture category |
| `source.json` | Source revision and provenance |
| `download.py` | Reproducible download and local inventory generation |
| `requirements.txt` | Downloader dependency |

## Dataset archive and verification

The [GitHub Release](https://github.com/samihaabedanur/Fitwell-AI/releases/tag/dataset-dtd-e850d7c773fa) contains `dtd-voxel51-e850d7c773fa.tar.gz` (625,925,910 bytes), upstream metadata, attribution and a per-image SHA-256 inventory. A separate checksum file records the archive hash.

The image index was checked for unique paths, category counts and consistency with the category table. The [archival workflow](https://github.com/samihaabedanur/Fitwell-AI/actions/runs/41854398789) completed image retrieval and presence checks before packaging.

## Reproduction

The following commands are executed from the repository root:

```bash
python -m pip install -r datasets/dtd/requirements.txt
python datasets/dtd/download.py
```

Downloaded files are written to `datasets/dtd/local_data/`, which is excluded from Git tracking. A limited download and an index-only validation are also supported:

```bash
python datasets/dtd/download.py --limit 5
python datasets/dtd/download.py --check-index
```

## Analysis and limitations

[Notebook 01](../../notebooks/01_dtd_analysis.ipynb) examines category balance and index consistency. DTD labels describe visual texture attributes rather than material composition. For example, a marbled appearance does not establish a marble substrate.

The committed index does not assign evaluation splits. Benchmarking requires the original DTD protocols or a separately documented partition. The Hugging Face viewer's collection naming is not used as an evaluation protocol. Dataset integration has not resulted in model training.

## Licence and citation

The Hugging Face card records the licence as `other`; the original project describes research use. Dataset photographs retain their original rights and are not relicensed under Fitwell's software licence.

```bibtex
@InProceedings{cimpoi14describing,
  author = {M. Cimpoi and S. Maji and I. Kokkinos and S. Mohamed and A. Vedaldi},
  title = {Describing Textures in the Wild},
  booktitle = {Proceedings of the IEEE Conference on Computer Vision and Pattern Recognition},
  year = {2014}
}
```

Distribution and packaging credit: Voxel51.
