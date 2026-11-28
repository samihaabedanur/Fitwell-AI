"""Fitwell material pipeline (v8), CPU or GPU.

board mode : SAM cuts every sample -> DINOv2 + Fitwell head -> group per type -> search + colour -> passport
single mode: one centre crop of a single material photo -> same search
"""
import io, json, base64, zipfile, os
import numpy as np, torch, torch.nn as nn, torch.nn.functional as Fn
import torchvision.transforms as T
from PIL import Image
from transformers import AutoModel, pipeline as hf_pipeline
from sklearn.cluster import AgglomerativeClustering
from skimage.color import rgb2lab

BUNDLE = os.environ.get("FITWELL_BUNDLE") or ("bundle" if os.path.isdir("bundle") else ".")
DEV = "cuda" if torch.cuda.is_available() else "cpu"
W = 0.5                    # 0.5 * Fitwell head + 0.5 * DINOv2
FLAG_BELOW = 0.40          # CLIP material probability under this -> "Check: may include an object"
AGREE_MIN = 0.5           # Fitwell model type agreement under this -> also "Check"
MATERIAL = ["a close-up photo of a material sample", "a flat texture of fabric, wood, stone, tile or metal",
            "a wall or floor surface"]
OBJECT = ["a lamp", "a plant, leaves or flowers", "dried grass or a feather", "a chair, sofa or table",
          "a vase, bowl or cup", "a tap, faucet or sink", "text, a logo or a brand label",
          "a printed card or label with writing", "a person or hand", "a ball of yarn or thread"]


class Head(nn.Module):
    def __init__(s):
        super().__init__()
        s.enc = nn.Sequential(nn.Linear(768, 256), nn.ReLU(), nn.Linear(256, 32))
        s.dec = nn.Sequential(nn.Linear(32, 256), nn.ReLU(), nn.Linear(256, 768))


class Fitwell:
    def __init__(self, points_per_side=16):
        b = np.load(f"{BUNDLE}/fitwell_index.npz", allow_pickle=True)
        self.LIBV = b["LIBV"].astype(np.float32)
        self.LIB_LAB = b["LIB_LAB"]; self.ylib = b["ylib"].astype(str)
        self.TZ = b["TZ"].astype(np.float32); self.TY = b["TY"].astype(str)
        self.mu = b["mu"]; self.sd = b["sd"]
        self.NOWALL = self.TY != "Wallpaper"
        self.passports = json.load(open(f"{BUNDLE}/passports.json"))
        self.head = Head().to(DEV)
        self.head.load_state_dict(torch.load(f"{BUNDLE}/fitwell_head_state.pt", map_location=DEV))
        self.head.eval()
        half = DEV == "cuda"
        self.dino = AutoModel.from_pretrained("facebook/dinov2-small").to(DEV).eval()
        if half: self.dino = self.dino.half()
        dev_id = 0 if DEV == "cuda" else -1
        self.sam = hf_pipeline("mask-generation", model="facebook/sam-vit-base", device=dev_id)
        self.clip = hf_pipeline("zero-shot-image-classification",
                                model="openai/clip-vit-base-patch32", device=dev_id)
        self.pps = points_per_side
        self.norm = T.Compose([T.ToTensor(), T.Normalize([0.485, 0.456, 0.406], [0.229, 0.224, 0.225])])
        self.half = half
        self._thumbs = {}
        if not os.path.isdir(f"{BUNDLE}/thumbs") and os.path.exists(f"{BUNDLE}/thumbs.zip"):
            zipfile.ZipFile(f"{BUNDLE}/thumbs.zip").extractall(f"{BUNDLE}/thumbs")

    # ---------- features ----------
    @torch.no_grad()
    def feats(self, crops):
        x = torch.stack([self.norm(c) for c in crops]).to(DEV)
        if self.half: x = x.half()
        h = self.dino(pixel_values=x).last_hidden_state
        return torch.cat([h[:, 0], h[:, 1:].mean(1)], 1).float().cpu().numpy()

    @torch.no_grad()
    def enc(self, F):
        z = self.head.enc(torch.tensor((F - self.mu) / self.sd, dtype=torch.float32, device=DEV))
        return Fn.normalize(z, dim=1).cpu().numpy()

    @staticmethod
    def raw(F):
        return F / np.linalg.norm(F, axis=1, keepdims=True)

    def hyb(self, F):
        return np.concatenate([np.sqrt(W) * self.enc(F), np.sqrt(1 - W) * self.raw(F)], 1)

    def category(self, F, k=15):
        S = self.enc(F) @ self.TZ.T; S[:, ~self.NOWALL] = -9; out = []
        for row in S:
            vals, cnt = np.unique(self.TY[np.argpartition(-row, k)[:k]], return_counts=True)
            out.append((str(vals[cnt.argmax()]), float(cnt.max() / k)))
        return out

    # ---------- cutting samples ----------
    @staticmethod
    def edge_colour(arr):                       # colour of the board background (its edges)
        b = np.concatenate([arr[:8].reshape(-1, 3), arr[-8:].reshape(-1, 3),
                            arr[:, :8].reshape(-1, 3), arr[:, -8:].reshape(-1, 3)])
        return rgb2lab(np.median(b, 0)[None, None, :] / 255.)[0, 0]

    @staticmethod
    def is_background(crop, bg):                # plain AND the same colour as the board edge
        plain = np.asarray(crop.convert("L"), dtype=np.float32).std() < 10
        lab = rgb2lab(np.asarray(crop) / 255.).reshape(-1, 3).mean(0)
        return plain and np.linalg.norm(lab - bg) < 12

    def swatches(self, img, min_area=0.01, max_area=0.35, max_n=24):
        out = self.sam(img, points_per_batch=64, points_per_crop=self.pps)
        masks = sorted([np.array(m) for m in out["masks"]], key=lambda m: -m.sum())
        A = img.size[0] * img.size[1]; arr = np.array(img); bg = self.edge_colour(arr); kept, crops, boxes = [], [], []
        for m in masks:
            a = m.sum() / A
            if a < min_area or a > max_area: continue
            if any((m & k).sum() > 0.5 * m.sum() for k in kept): continue
            ys, xs = np.nonzero(m); box = None
            for lo, hi in [(20, 80), (30, 70), (38, 62)]:
                y0, y1 = np.percentile(ys, [lo, hi]).astype(int); x0, x1 = np.percentile(xs, [lo, hi]).astype(int)
                if y1 - y0 < 24 or x1 - x0 < 24: break
                if m[y0:y1, x0:x1].mean() >= 0.85: box = (y0, y1, x0, x1); break
            if box is None: continue
            y0, y1, x0, x1 = box
            crop = Image.fromarray(arr[y0:y1, x0:x1]).resize((224, 224))
            kept.append(m)
            if self.is_background(crop, bg): continue
            boxes.append([int(x0), int(y0), int(x1), int(y1)]); crops.append(crop)
            if len(crops) >= max_n: break
        return crops, boxes

    @staticmethod
    def centre_crop(img, frac=0.6):
        w, h = img.size; s = int(min(w, h) * frac)
        x0, y0 = (w - s) // 2, (h - s) // 2
        return img.crop((x0, y0, x0 + s, y0 + s)).resize((224, 224)), [x0, y0, x0 + s, y0 + s]

    def thumb(self, i, size=160):
        if i not in self._thumbs:
            self._thumbs[i] = to_b64(Image.open(f"{BUNDLE}/thumbs/{i}.jpg").convert("RGB"), size)
        return self._thumbs[i]

    # ---------- main ----------
    def analyse(self, img, mode="board", threshold=0.35, alpha=0.006, pool=40, top_k=5, bonus=0.05):
        img = img.convert("RGB")
        if max(img.size) > 1024: img.thumbnail((1024, 1024))
        if mode == "single":
            c, b = self.centre_crop(img); crops, boxes = [c], [b]
        else:
            crops, boxes = self.swatches(img)
            if not crops:                       # nothing cut out: treat as one material
                c, b = self.centre_crop(img); crops, boxes = [c], [b]
        F = self.feats(crops); R, V = self.raw(F), self.hyb(F); cats = self.category(F)
        pm = [sum(s["score"] for s in r if s["label"] in MATERIAL)
              for r in self.clip(crops, candidate_labels=MATERIAL + OBJECT)]
        if mode == "single": pm = [1.0]
        gid = np.zeros(len(crops), int); nxt = 0
        for c in sorted(set(cc for cc, _ in cats)):
            idx = [i for i, (cc, _) in enumerate(cats) if cc == c]
            sub = (AgglomerativeClustering(n_clusters=None, distance_threshold=threshold, metric="cosine",
                   linkage="average").fit_predict(R[idx]) if len(idx) > 1 else np.zeros(1, int))
            for i, s in zip(idx, sub): gid[i] = nxt + s
            nxt += int(max(sub)) + 1
        groups = []
        for g in sorted(set(gid)):
            idx = np.where(gid == g)[0]; mat = cats[idx[0]][0]
            agree = float(np.mean([cats[i][1] for i in idx]))
            q = V[idx].mean(0); q /= np.linalg.norm(q)
            S = self.LIBV @ q; cand = np.argsort(-S)[:pool]
            qlab = np.mean([rgb2lab(np.array(crops[i])[56:168, 56:168] / 255.).reshape(-1, 3).mean(0) for i in idx], 0)
            final = S[cand] - alpha * np.linalg.norm(self.LIB_LAB[cand] - qlab, axis=1) + bonus * (self.ylib[cand] == mat)
            best = cand[np.argsort(-final)[:top_k]]
            if agree < 0.6:
                mc = [self.ylib[b] for b in best]; mat = max(set(mc), key=mc.count)
            conf = float(np.mean([pm[i] for i in idx]))
            flagged = (conf < FLAG_BELOW or agree < AGREE_MIN) and mode != "single"
            groups.append({
                "type": mat,
                "flagged": bool(flagged),
                "label": "Check: may include an object" if flagged else mat,
                "material_confidence": round(conf, 2),
                "type_agreement": round(agree, 2),
                "samples": [{"box": boxes[i], "image": to_b64(crops[i])} for i in idx],
                "matches": [{"lib_index": int(b), "score": round(float(S[b]), 3), "category": str(self.ylib[b]),
                             "thumb": self.thumb(int(b)), "passport": self.passports[int(b)]} for b in best],
            })
        groups.sort(key=lambda g: (g["flagged"], -g["material_confidence"]))
        return {"mode": mode, "width": img.size[0], "height": img.size[1], "materials": groups}


def to_b64(im, size=160):
    im = im.copy(); im.thumbnail((size, size)); buf = io.BytesIO()
    im.save(buf, "JPEG", quality=80)
    return "data:image/jpeg;base64," + base64.b64encode(buf.getvalue()).decode()
