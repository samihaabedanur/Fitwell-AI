"""FITWELL Material Finder v2
Click-to-segment -> material label -> vendor catalogue -> PBR maps for 3D.
Run locally:  python fitwell_app.py      Render: see render.yaml
"""
import base64, io, math, os, uuid
from collections import OrderedDict, Counter
from pathlib import Path

import numpy as np, pandas as pd
from PIL import Image
from flask import Flask, jsonify, request, send_from_directory
from scipy import ndimage as ndi
from skimage.color import rgb2lab
from skimage.segmentation import slic

ROOT = Path(__file__).parent
DATA = ROOT / "data"
app = Flask(__name__, static_folder="static")
PROJECT_LATLON = (41.3995, 2.2000)   # distance-to-site; change to your project site
MAX_SIDE = 1024
CACHE = OrderedDict()                # image_id -> session dict (LRU, 8 items)

# ---- optional hooks: adapt these two to YOUR existing files ----------------
try:   # Apple DMS: must return (HxW int class map, list of class names)
    from apple_dms import predict_dms          # TODO: match your function name
except Exception:
    predict_dms = None
try:   # your trained classifier from fitwell_training.ipynb
    from fitwell_model import predict_patch
    print("Using trained model: models/fitwell_materials.pt")
except Exception as e:
    print("Trained model not used, falling back to CLIP zero-shot:", e)
    predict_patch = None

# ---- one taxonomy for DMS / MINC / OpenSurfaces / DTD / catalogue ----------
TAXONOMY = {
    "wood": ["wood", "timber", "plywood", "bamboo", "parquet"],
    "brick": ["brick"],
    "concrete": ["concrete", "cement", "asphalt"],
    "stone": ["stone", "granite", "marble", "rock", "slate", "sandstone"],
    "metal": ["metal", "steel", "aluminium", "aluminum", "iron", "copper", "brass"],
    "glass": ["glass", "mirror", "window"],
    "ceramic": ["tile", "ceramic", "porcelain"],
    "plaster": ["plaster", "paint", "wall", "stucco", "gypsum", "painted"],
    "fabric": ["fabric", "carpet", "cloth", "textile", "wool", "leather"],
    "plastic": ["plastic", "rubber", "vinyl", "laminate"],
    "insulation": ["insulation", "foam", "cork"],
}
def unify(raw):
    r = str(raw).lower()
    for cat, keys in TAXONOMY.items():
        if any(k in r for k in keys):
            return cat
    return "other"

# ---- catalogue --------------------------------------------------------------
# data/materials.csv columns (rename in COLS if yours differ):
COLS = dict(name="name", category="category", vendor="vendor", vendor_url="vendor_url",
            price="price_eur_m2", gwp="gwp_kgco2e_m2", country="country", city="city",
            lat="lat", lon="lon", image="image", lead="lead_time_days", specs="specs")

def haversine(lat, lon):
    if pd.isna(lat) or pd.isna(lon): return None
    p1, p2 = math.radians(PROJECT_LATLON[0]), math.radians(lat)
    dl = math.radians(lon - PROJECT_LATLON[1]); dp = p2 - p1
    a = math.sin(dp/2)**2 + math.cos(p1)*math.cos(p2)*math.sin(dl/2)**2
    return round(6371*2*math.asin(math.sqrt(a)))

def load_catalog():
    f = DATA / "materials.csv"
    if f.exists():
        df = pd.read_csv(f).rename(columns={v: k for k, v in COLS.items()})
    else:  # demo rows so the app boots before your data is wired in
        df = pd.DataFrame([
            dict(name="Oak parquet", category="wood", vendor="Demo Timber", price=62, gwp=-9.1, city="Girona", country="ES", lat=41.98, lon=2.82),
            dict(name="Facing brick", category="brick", vendor="Demo Ceramics", price=48, gwp=14.0, city="Valencia", country="ES", lat=39.47, lon=-0.38),
            dict(name="Board-marked concrete", category="concrete", vendor="Demo Cement", price=55, gwp=38.0, city="Lyon", country="FR", lat=45.76, lon=4.84)])
    for c in COLS:
        if c not in df: df[c] = None
    df["id"] = range(len(df))
    df["category"] = [unify(c) if c else unify(n) for c, n in zip(df.category, df.name)]
    df["distance_km"] = [haversine(a, b) for a, b in zip(df.lat, df.lon)]
    return df

CAT = load_catalog()

def clean(df):
    return df.astype(object).where(df.notna(), None).to_dict("records")

# ---- cheap texture/colour descriptor (works with zero training) --------------
def feat(img):
    im = img.convert("RGB").resize((96, 96))
    hsv = np.asarray(im.convert("HSV"), dtype=np.float32)
    h = np.histogramdd(hsv.reshape(-1, 3), bins=(8, 4, 4), range=((0, 256),)*3)[0].ravel()
    g = np.asarray(im.convert("L"), dtype=np.float32)
    gy, gx = np.gradient(g); mag = np.hypot(gx, gy)
    t = np.histogram(mag, bins=12, range=(0, 60))[0]
    ang = np.histogram(np.arctan2(gy, gx), bins=8, weights=mag, range=(-math.pi, math.pi))[0]
    v = np.concatenate([h/h.sum(), t/t.sum(), ang/(ang.sum()+1e-6)])
    return v / (np.linalg.norm(v) + 1e-9)

def build_index():
    f = DATA / "feats.npy"
    if f.exists():
        return np.load(f)
    out = []
    for p in CAT.image:
        try: out.append(feat(Image.open(DATA / str(p))))
        except Exception: out.append(np.zeros(8*4*4 + 12 + 8, dtype=np.float32))
    arr = np.stack(out); np.save(f, arr); return arr

FEATS = build_index()

def similar(img, category=None, k=8):
    sims = FEATS @ feat(img)
    ids = np.argsort(-sims)
    if category and category != "other":
        ids = [i for i in ids if CAT.category.iloc[i] == category]   # none in catalogue -> empty, not unrelated items
    rows = []
    for i in list(ids)[:k]:
        r = clean(CAT.iloc[[i]])[0]; r["similarity"] = round(float(sims[i]), 3); rows.append(r)
    return rows

# ---- zero-shot material recognition (CLIP): no training or catalogue needed ----
PROMPTS = {
    "wood": "natural wood", "brick": "red brick", "concrete": "grey concrete",
    "stone": "stone or marble", "metal": "brushed metal", "glass": "glass",
    "ceramic": "glazed ceramic tile", "plaster": "painted plaster wall",
    "fabric": "woven fabric textile or upholstery", "plastic": "plastic",
    "insulation": "foam insulation", "leather": "leather",
}
_clip = None; CLIP_ERR = None
def clip_classify(img):
    """PIL image -> (material, confidence) or None if transformers/torch are missing."""
    global _clip, CLIP_ERR
    try:
        if _clip is None:
            import torch
            from transformers import CLIPModel, CLIPProcessor
            name = "openai/clip-vit-base-patch32"       # ~600 MB, downloads on first use
            _clip = (CLIPModel.from_pretrained(name).eval(), CLIPProcessor.from_pretrained(name), torch)
        model, proc, torch = _clip
        texts = [f"a close-up photo of {d}" for d in PROMPTS.values()]
        inp = proc(text=texts, images=img, return_tensors="pt", padding=True)
        with torch.no_grad():
            p = model(**inp).logits_per_image.softmax(1)[0]
        i = int(p.argmax()); return list(PROMPTS)[i], float(p[i])
    except Exception as e:
        import traceback; traceback.print_exc()
        CLIP_ERR = f"{type(e).__name__}: {e}"[:300]; print("CLIP unavailable:", CLIP_ERR); return None

# ---- segmentation -----------------------------------------------------------
def segment(img):
    if predict_dms:
        try:
            lab, names = predict_dms(img)
            return np.asarray(lab).astype(np.int32), names, "dms"
        except Exception as e:
            print("DMS failed, using superpixels:", e)
    arr = np.asarray(img)
    return slic(arr, n_segments=250, compactness=12, start_label=0), None, "superpixel"

def png64(arr_rgba):
    b = io.BytesIO(); Image.fromarray(arr_rgba, "RGBA").save(b, "PNG")
    return "data:image/png;base64," + base64.b64encode(b.getvalue()).decode()

def region_mask(s, x, y, tol):
    lab = s["labels"]
    if s["mode"] == "dms":
        m = lab == lab[y, x]
    else:   # magic-wand on superpixels: grow by Lab distance from the clicked superpixel
        seed = s["lab"][lab == lab[y, x]].mean(0)
        smooth = ndi.uniform_filter(s["lab"], size=(5, 5, 1))
        m = np.linalg.norm(smooth - seed, axis=2) < tol
    comp, _ = ndi.label(m)
    return comp == comp[y, x] if comp[y, x] else lab == lab[y, x]

def crop_around(img, m, x, y):
    ys, xs = np.where(m)
    x0, x1, y0, y1 = xs.min(), xs.max(), ys.min(), ys.max()
    cx, cy = (x0+x1)//2 if (x1-x0) < 224 else x, (y0+y1)//2 if (y1-y0) < 224 else y
    h = min(112, max(48, max(x1-x0, y1-y0)//2))
    box = (max(cx-h, 0), max(cy-h, 0), min(cx+h, img.width), min(cy+h, img.height))
    crop = np.asarray(img).copy()
    crop[~m] = crop[m].mean(0).astype(np.uint8)       # blank out other materials
    return Image.fromarray(crop).crop(box)

# ---- object masks: MobileSAM (click -> clean object), magic-wand as fallback ----
_sam = None
def sam_mask(img, x, y):
    """One click -> object mask via MobileSAM (pip install ultralytics). None if unavailable."""
    global _sam
    try:
        if _sam is None:
            from ultralytics import SAM
            _sam = SAM("mobile_sam.pt")          # ~40 MB, downloads on first use
        r = _sam(np.asarray(img), points=[[int(x), int(y)]], labels=[1], verbose=False)
        m = r[0].masks.data[0].cpu().numpy() > 0.5
        if m.shape != (img.height, img.width):
            m = np.asarray(Image.fromarray(m.astype(np.uint8) * 255).resize(img.size, Image.NEAREST)) > 0
        return m
    except Exception as e:
        print("SAM unavailable, using magic-wand fallback:", repr(e)[:120])
        return None

def clean_mask(m, x, y):
    """Fill holes, drop specks, smooth the outline, keep only the clicked object."""
    m = ndi.binary_fill_holes(m)
    m = ndi.binary_opening(m, iterations=2)
    m = ndi.binary_closing(m, iterations=3)
    comp, _ = ndi.label(m)
    if comp[y, x]: m = comp == comp[y, x]
    m = ndi.gaussian_filter(m.astype(np.float32), 2.0) > 0.5
    return m

def get_mask(s, x, y, tol):
    m = sam_mask(s["img"], x, y); engine = "sam"
    if m is None or m.sum() < 50:
        m = region_mask(s, x, y, tol); engine = s["mode"]
    return clean_mask(m, x, y), engine

def inner_crop(img, m):
    """Largest square fully inside the object = pure material texture, no background."""
    dt = ndi.distance_transform_edt(m)
    cy, cx = np.unravel_index(dt.argmax(), dt.shape); r = int(dt.max() / 1.41)
    return img.crop((cx - r, cy - r, cx + r, cy + r)) if r >= 16 else None

# ---- PBR maps from a 2D photo (cheap SVBRDF estimate) -----------------------
def pbr_maps(img, category="other", size=512):
    im = img.convert("RGB").resize((size, size), Image.LANCZOS)
    a = np.asarray(im, dtype=np.float32) / 255
    g = a @ np.array([.299, .587, .114], dtype=np.float32)
    flat = ndi.gaussian_filter(g, size/8)
    albedo = np.clip(a / (flat[..., None] + 1e-3) * flat.mean(), 0, 1)     # de-light
    h = ndi.gaussian_filter(np.clip(g / (flat + 1e-3), 0, 2), 1.0)
    h = (h - h.min()) / (np.ptp(h) + 1e-6)
    gx, gy = ndi.sobel(h, 1), ndi.sobel(h, 0)
    n = np.dstack([-gx * 2.5, -gy * 2.5, np.ones_like(h)])
    n = n / np.linalg.norm(n, axis=2, keepdims=True) * .5 + .5
    sd = np.sqrt(np.maximum(ndi.uniform_filter(h**2, 9) - ndi.uniform_filter(h, 9)**2, 0))
    rough = np.clip(.95 - 3 * sd, .25, 1.0)
    if category == "metal": rough = np.clip(rough * .5, .15, .6)
    if category == "glass": rough = np.full_like(rough, .05)
    f = lambda x: "data:image/png;base64," + base64.b64encode(
        (lambda b: (Image.fromarray((x*255).astype(np.uint8)).save(b, "PNG"), b.getvalue())[1])(io.BytesIO())).decode()
    return dict(albedo=f(albedo), normal=f(n), roughness=f(rough), height=f(h),
                metalness=1.0 if category == "metal" else 0.0, opacity=0.25 if category == "glass" else 1.0)

# ---- routes -----------------------------------------------------------------
@app.get("/")
def home(): return send_from_directory("static", "index.html")

@app.get("/data/<path:p>")
def data_files(p): return send_from_directory(DATA, p)

@app.post("/api/segment")
def api_segment():
    img = Image.open(request.files["file"].stream).convert("RGB")
    img.thumbnail((MAX_SIDE, MAX_SIDE))
    labels, names, mode = segment(img)
    sid = uuid.uuid4().hex[:10]
    CACHE[sid] = dict(img=img, labels=labels, names=names, mode=mode,
                      lab=rgb2lab(np.asarray(img)))
    while len(CACHE) > 8: CACHE.popitem(last=False)
    return jsonify(image_id=sid, width=img.width, height=img.height, mode=mode)

@app.post("/api/pick")
def api_pick():
    j = request.get_json(); s = CACHE.get(j["image_id"])
    if not s: return jsonify(error="session expired, re-upload"), 410
    x = int(np.clip(j["x"], 0, s["img"].width-1)); y = int(np.clip(j["y"], 0, s["img"].height-1))
    m, engine = get_mask(s, x, y, float(j.get("tolerance", 14)))
    crop = inner_crop(s["img"], m)
    if crop is None: crop = crop_around(s["img"], m, x, y)
    how = None
    if s["mode"] == "dms":
        raw = s["names"][s["labels"][y, x]]; conf = 1.0; how = "Apple DMS"
    elif predict_patch:
        raw, conf = predict_patch(crop); how = "trained model"
    else:
        z = clip_classify(crop)
        if z: raw, conf = z; how = "CLIP zero-shot"
        else:   # last resort: vote over catalogue swatches
            top = similar(crop, k=10); votes = Counter()
            for r in top: votes[r["category"]] += max(r["similarity"], 0)
            tot = sum(votes.values())
            if tot > 0.05 and len(CAT) >= 20:   # voting over a few demo rows is meaningless
                raw, w = votes.most_common(1)[0]; conf = round(w / tot, 2); how = "swatch similarity (weak)"
            else:
                raw, conf, how = "unknown", 0.0, "no classifier available"
    cat = unify(raw)
    ov = np.zeros((*m.shape, 4), np.uint8); ov[~m] = (0, 0, 0, 115)       # dim everything else
    edge = ndi.binary_dilation(m, iterations=2) & ~ndi.binary_erosion(m, iterations=1)
    ov[edge] = (255, 255, 255, 255)                                         # crisp outline
    return jsonify(engine=engine, classifier=how, label=raw, category=cat, confidence=round(float(conf), 2),
                   area_pct=round(100*m.mean(), 1), mask=png64(ov),
                   matches=[] if raw == "unknown" else similar(crop, cat), pbr=pbr_maps(crop, cat),
                   note=CLIP_ERR if how in ("no classifier available", "swatch similarity (weak)") else None)

@app.get("/api/materials")
def api_materials():
    df = CAT
    q, cat = request.args.get("q", "").lower(), request.args.get("category")
    if q: df = df[df.name.fillna("").str.lower().str.contains(q) | df.vendor.fillna("").str.lower().str.contains(q)]
    if cat: df = df[df.category == cat]
    if request.args.get("max_price"): df = df[pd.to_numeric(df.price, errors="coerce") <= float(request.args["max_price"])]
    if request.args.get("max_gwp"): df = df[pd.to_numeric(df.gwp, errors="coerce") <= float(request.args["max_gwp"])]
    return jsonify(total=len(df), items=clean(df.head(60)), categories=sorted(CAT.category.unique()))

@app.post("/api/pbr/<int:mid>")
def api_pbr(mid):
    r = CAT.iloc[mid]
    return jsonify(pbr_maps(Image.open(DATA / str(r.image)), r.category))

if __name__ == "__main__":
    app.run(debug=True, port=int(os.environ.get("PORT", 5000)))
