# OpenSurfaces — Release 0

Original project: https://opensurfaces.cs.cornell.edu/
Download and licence documentation: https://opensurfaces.cs.cornell.edu/publications/opensurfaces/

## Dataset files

The official Release 0 is distributed as a ZIP archive (approximately 1.1 GB). The authors provide a separate helper to retrieve images and process annotations. Do not assume this ZIP includes every full-resolution photo.

Our GitHub workflow `.github/workflows/store-opensurfaces.yml` downloads the unmodified original ZIP and helper, verifies the ZIP's CRCs, creates a file inventory and SHA-256 checksums, and uploads them to a repository Release.

The [OpenSurfaces — official Release 0](https://github.com/samihaabedanur/Fitwell-AI/releases/tag/dataset-opensurfaces-release-0) archive is now available on GitHub. The [upload workflow](https://github.com/samihaabedanur/Fitwell-AI/actions/runs/41856852494) downloaded the original ZIP (1,175,026,542 bytes), passed the ZIP CRC check, and uploaded six assets. Download `opensurfaces-release-0.zip`, the helper, provenance and checksums under Assets. Large files are Release assets rather than Git-tracked files.

Official downloads:
- https://labelmaterial.s3.amazonaws.com/release/opensurfaces-release-0.zip
- https://labelmaterial.s3.amazonaws.com/release/process_opensurfaces_release_0.py

## Local use

Extract the ZIP into a separate data directory. Read the helper's documentation before using it: it is legacy upstream code and may require compatibility changes for modern Python. This integration does not execute it, download all associated photos, or generate training-ready masks automatically. Large local files should not be committed to Git.

OpenSurfaces includes annotated material regions useful for investigating segmentation and recognition. Review labels, quality flags, photo licences and train/test separation before using the annotations. No training was performed and the browser camera remains unchanged.

## Licence and attribution

Annotations: **Creative Commons Attribution 4.0 International** — https://creativecommons.org/licenses/by/4.0/
Photos: each photo has its own licence. The annotation licence and Fitwell's software licence do not replace image rights.

Please credit Sean Bell, Paul Upchurch, Noah Snavely and Kavita Bala, **OpenSurfaces: A Richly Annotated Catalog of Surface Appearance**, ACM Transactions on Graphics (SIGGRAPH), volume 32, number 4, 2013.

## Verify

The Release includes `SHA256SUMS.txt` and `archive_inventory.json`. Checksums establish which downloaded bytes were archived; they are computed by Fitwell's workflow, not independently supplied upstream checksums.
