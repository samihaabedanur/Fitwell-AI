# Fitwell

## Material camera

A camera-only experiment using a pretrained CLIP image–text model with browser-side region classification and texture tracking. It is not trained on this repository's datasets. Boxes indicate sampled areas, not exact surface boundaries; labels are unverified suggestions.

### Open on a phone

Enable GitHub Pages once: **Settings → Pages → Deploy from a branch → main → /docs → Save**. Then use the website URL shown in Pages settings. Open in Safari or Chrome, allow camera access, and wait for the first model download (approximately 150 MB). Tap a surface to prioritise it. No ChatGPT account is required.

### Files

- `docs/index.html`: standalone material camera, ready for GitHub Pages.
- `docs/.nojekyll`: serves the app as static HTML.
- `datasets/`: existing research datasets, retained unchanged.

### Local development

Open `docs/index.html` through a localhost web server such as VS Code Live Server. A phone needs an HTTPS-hosted page for camera access; opening the HTML attachment directly is not a supported phone deployment.

Model: `Xenova/clip-vit-base-patch32`, loaded with Transformers.js. The browser downloads code/model assets from jsDelivr and Hugging Face. Camera frames are processed locally and are not uploaded by this app. Model quality and device performance vary, and physical-camera accuracy has not been validated.

Anyone can use the public demo. To grant teammates code-editing access, the owner can invite their GitHub usernames under Settings → Collaborators.
