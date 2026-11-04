# Describable Textures Dataset (DTD)

Source: https://huggingface.co/datasets/Voxel51/Describable-Textures-Dataset

Original research: https://www.robots.ox.ac.uk/~vgg/data/dtd/

## Included in Fitwell-AI

- `images.csv`: all 5,640 image paths, texture labels derived from filename prefixes, with downloads pinned to the revision in `source.json`.
- `categories.csv`: 47 texture categories, each with 120 image files.
- `source.json`: pinned Hugging Face revision and provenance.
- `download.py`: downloads images plus the mirror's metadata locally; records local SHA-256 hashes after downloading.
- `requirements.txt`: downloader dependency.

The image bytes are stored on GitHub as a Release archive rather than in Git history. The pinned upstream downloader remains available as an alternative.

## Download the full dataset from GitHub

Open [DTD dataset release](https://github.com/samihaabedanur/Fitwell-AI/releases/tag/dataset-dtd-e850d7c773fa) and download `dtd-voxel51-e850d7c773fa.tar.gz` under Assets (625,925,910 bytes, about 626 MB). Extract it using an archive tool; Windows users can use 7-Zip. It contains all 5,640 images, upstream metadata, per-image SHA-256 inventory and attribution. The accompanying `.sha256` file verifies the archive.

The successful [upload run](https://github.com/samihaabedanur/Fitwell-AI/actions/runs/41854398789) downloaded and checked all indexed images before packaging.

## Download in VS Code

From the root of your cloned Fitwell-AI repository:

```bash
python -m pip install -r datasets/dtd/requirements.txt
python datasets/dtd/download.py
```

Images are saved under `datasets/dtd/local_data/` with their original relative paths. This directory is ignored by Git. Internet access and several hundred MB of free storage are needed. The downloader does not require FiftyOne or a camera.

For a small download check:

```bash
python datasets/dtd/download.py --limit 5
```

Validate the committed index without installing packages or downloading images:

```bash
python datasets/dtd/download.py --check-index
```

## Use in Fitwell

DTD describes **texture appearance**, not material composition. A label such as `woven` is not equivalent to `fabric`; `marbled` does not establish that a surface is marble. Use it for texture research or auxiliary training, with separate verified labels for material identification. Adding this folder does not train the camera model.

## Evaluation splits

The original DTD research supplies multiple train/validation/test protocols. The Hugging Face viewer's `train` collection must not be treated as proof that all images belong in a training set. This integration does not assign evaluation splits. Use the original protocols for benchmarking and avoid moving the same image into multiple splits.

## Licence and attribution

The Hugging Face card labels the licence `other`; the original project describes research use. Fitwell-AI's repository licence does not relicense the dataset photographs. Follow the original dataset terms and image rights before redistribution or commercial use.

Original authors: M. Cimpoi, S. Maji, I. Kokkinos, S. Mohamed and A. Vedaldi. Hosting/packaging: Voxel51.

```bibtex
@InProceedings{cimpoi14describing,
  author = {M. Cimpoi and S. Maji and I. Kokkinos and S. Mohamed and A. Vedaldi},
  title = {Describing Textures in the Wild},
  booktitle = {Proceedings of the IEEE Conference on Computer Vision and Pattern Recognition},
  year = {2014}
}
```

## Verification status

The committed index was checked for 5,640 unique paths and 47 classes with 120 files each. The downloader passed Python compilation and index validation. A full download, image-presence check, per-image SHA-256 inventory and Release upload completed through GitHub Actions. Model training has not been run.
