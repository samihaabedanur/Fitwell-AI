# FITWELL Material Finder v2
1. Copy these files into your `fitwell-dms` folder (does not overwrite app.py). Put swatches + `materials.csv` in `data/`.
2. `pip install -r requirements.txt` then `python fitwell_app.py` -> http://localhost:5000
3. In `fitwell_app.py` adapt the two `TODO` imports (`predict_dms`, `predict_patch`) to your apple_dms.py / minc_predict.py.
4. Render: push to GitHub, New > Blueprint, it reads render.yaml. Commit `data/feats.npy` so startup is instant.
`materials.csv` columns: name, category, vendor, vendor_url, price_eur_m2, gwp_kgco2e_m2, country, city, lat, lon, image, lead_time_days, specs

5. Clean object selection: `pip install -r requirements-segment.txt` (MobileSAM; downloads ~40 MB on first click).
