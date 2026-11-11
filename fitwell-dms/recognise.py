"""Fitwell inference wrapper. Preprocessing follows Apple's inference.py."""
import argparse
import json
import math
from pathlib import Path
import numpy as np
from PIL import Image, ImageOps
import torch

ROOT = Path(__file__).resolve().parent
IDS = [1,2,3,4,5,6,7,8,9,10,11,12,13,15,16,17,18,19,20,21,23,24,26,27,29,30,32,33,34,35,36,37,38,39,41,43,44,46,47,48,49,50,51,52,53,56]
TAXONOMY = json.loads((ROOT / 'taxonomy.json').read_text())
NAMES = [TAXONOMY['names'][i] for i in IDS]
COLORS = np.array([TAXONOMY['srgb_colormap'][i] for i in IDS], dtype=np.uint8)

def load_model():
    device = 'cuda' if torch.cuda.is_available() else 'cpu'
    model = torch.jit.load(str(ROOT / 'models/DMS46_v1.pt'), map_location=device).eval()
    return model, device

def predict(path, model, device):
    image = ImageOps.exif_transpose(Image.open(path)).convert('RGB')
    scale = min(512 / image.height, 512 / image.width)
    image = image.resize((math.ceil(image.width*scale), math.ceil(image.height*scale)), Image.Resampling.LANCZOS)
    pixels = np.array(image)
    tensor = torch.from_numpy(pixels.copy()).permute(2,0,1).float() / 255
    tensor = (tensor - torch.tensor([.485,.456,.406])[:,None,None]) / torch.tensor([.229,.224,.225])[:,None,None]
    with torch.inference_mode():
        output = model(tensor.unsqueeze(0).to(device))
        mask = output[0].cpu()[0,0].numpy().astype(np.uint8)
    if mask.shape != pixels.shape[:2]:
        mask = np.array(Image.fromarray(mask).resize(image.size, Image.Resampling.NEAREST))
    colored = Image.fromarray(COLORS[mask])
    overlay = Image.blend(image, colored, .45)
    counts = np.bincount(mask.ravel(), minlength=46)
    summary = [{'material':NAMES[i], 'image_area_percent':round(float(counts[i]/mask.size*100),2)} for i in np.argsort(counts)[::-1] if counts[i]]
    return image, mask, overlay, summary

def save_results(path, model, device, output_dir):
    image, mask, overlay, summary = predict(path, model, device)
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    stem = Path(path).stem
    image.save(output_dir / f'{stem}_original.png')
    Image.fromarray(mask).save(output_dir / f'{stem}_mask.png')
    overlay.save(output_dir / f'{stem}_overlay.png')
    (output_dir / f'{stem}_materials.json').write_text(json.dumps(summary, indent=2))
    return image, mask, overlay, summary

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('image')
    parser.add_argument('--output', default=str(ROOT/'results'))
    args = parser.parse_args()
    model, device = load_model()
    *_, summary = save_results(args.image, model, device, args.output)
    print(json.dumps({'device':device,'materials':summary}, indent=2))
