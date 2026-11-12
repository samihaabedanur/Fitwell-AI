"""Inference adapter for the authors' CC0 Zero-Shot Material State Net."""
import sys
from pathlib import Path
import cv2
import numpy as np
import torch

ROOT = Path(__file__).resolve().parent
SOURCE = ROOT / "external" / "Zero-Shot-Material-State-Segmentation-Net"
if str(SOURCE) not in sys.path:
    sys.path.insert(0, str(SOURCE))
from Desnet import Net

WEIGHTS = ROOT / "models" / "zero-shot-material" / "Defult.torch"


def load_model():
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    model = Net(descriptor_depth=128)
    model.load_state_dict(torch.load(WEIGHTS, map_location=device))
    model.to(device).eval()
    return model, device


def prepare(image_path, max_size=700):
    image = cv2.imread(str(image_path))
    if image is None:
        raise ValueError(f"Could not read image: {image_path}")
    scale = min(1.0, max_size / max(image.shape[:2]))
    if scale < 1:
        image = cv2.resize(image, (round(image.shape[1] * scale), round(image.shape[0] * scale)), interpolation=cv2.INTER_AREA)
    return image


def descriptor_map(image, model):
    batch = np.expand_dims(image, 0)
    with torch.inference_mode():
        fmap = model.forward(batch, np.zeros_like(batch[:, :, :, 0]), TrainMode=False)
    return fmap[0].permute(1, 2, 0).detach().cpu()


def similarity_map(fmap, x, y, radius=10):
    h, w, _ = fmap.shape
    mask = torch.zeros((h, w), dtype=torch.float32)
    yy, xx = torch.meshgrid(torch.arange(h), torch.arange(w), indexing="ij")
    mask[((xx - x) ** 2 + (yy - y) ** 2) <= radius ** 2] = 1
    vectors = torch.nn.functional.normalize(fmap, dim=2)
    point = (vectors * mask[:, :, None]).sum((0, 1))
    point = torch.nn.functional.normalize(point, dim=0)
    similarity = (vectors * point).sum(2).numpy()
    return np.clip((similarity + 1) / 2, 0, 1)


def run(image_path, x, y, radius=10, max_size=700):
    image = prepare(image_path, max_size)
    model, device = load_model()
    fmap = descriptor_map(image, model)
    sim = similarity_map(fmap, x, y, radius)
    return image, sim, device
