"""Loads models/fitwell_materials.pt (saved by fitwell_training.ipynb) for the web app."""
from pathlib import Path
import torch, torch.nn as nn
import torchvision.transforms as T
from torchvision.models import resnet18

_here = Path(__file__).parent
_path = next((p / "fitwell_materials.pt" for p in [_here / "models", _here.parent / "models"]
              if (p / "fitwell_materials.pt").exists()), None)
if _path is None:
    raise FileNotFoundError("fitwell_materials.pt not found - run fitwell_training.ipynb first")

_ck = torch.load(_path, map_location="cpu")
CLASSES = _ck["classes"]
MIN_CLASSES = 6   # a model that knows fewer materials than this is not reliable enough; the app falls back to CLIP
if len(CLASSES) < MIN_CLASSES:
    raise RuntimeError(f"trained model only knows {len(CLASSES)} materials ({', '.join(CLASSES)})")
_net = resnet18(); _net.fc = nn.Linear(512, len(CLASSES))
_net.load_state_dict(_ck["state"]); _net.eval()
_tf = T.Compose([T.Resize(176), T.CenterCrop(160), T.ToTensor(),
                 T.Normalize([.485, .456, .406], [.229, .224, .225])])

@torch.no_grad()
def predict_patch(img):
    """PIL image -> (material label, confidence)"""
    p = torch.softmax(_net(_tf(img.convert("RGB")).unsqueeze(0)), 1)[0]
    i = int(p.argmax()); return CLASSES[i], float(p[i])
