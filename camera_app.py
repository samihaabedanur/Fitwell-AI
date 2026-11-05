"""Live webcam material identification using the trained DMS segmentation model."""
import argparse, csv
from pathlib import Path
import cv2
import numpy as np
import torch
from torchvision.models.segmentation import deeplabv3_mobilenet_v3_large
from torchvision.transforms.functional import normalize, to_tensor

# Continuous material filter: keep the live view focused on interior surfaces.
MATERIAL_FILTER = {
    "Brickwork", "Ceramic", "Concrete", "Glass", "Metal", "Mirror",
    "Paint/plaster/enamel", "Tile", "Wallpaper", "Wood",
    "Stone, natural", "Stone, polished", "Asphalt", "Ceiling tile",
    "Engineered stone", "Carpet/rug", "Fabric/cloth", "Cork/corkboard",
}

def load_model(checkpoint, device):
    saved = torch.load(checkpoint, map_location=device, weights_only=True)
    model = deeplabv3_mobilenet_v3_large(weights=None, weights_backbone=None, num_classes=46, aux_loss=True)
    model.classifier[-1] = torch.nn.Conv2d(model.classifier[-1].in_channels, 46, 1)
    model.aux_classifier[-1] = torch.nn.Conv2d(model.aux_classifier[-1].in_channels, 46, 1)
    model.load_state_dict(saved["state_dict"]); model.to(device).eval()
    return model, saved.get("size", 256)

def main():
    p = argparse.ArgumentParser(); p.add_argument("--checkpoint", type=Path, default=Path("training/runs/dms-expanded/best.pt")); p.add_argument("--camera", type=int, default=0); p.add_argument("--confidence", type=float, default=.35); p.add_argument("--every", type=int, default=3)
    a = p.parse_args(); repo = Path(__file__).resolve().parent; checkpoint = (repo / a.checkpoint).resolve()
    if not checkpoint.is_file(): raise SystemExit(f"Checkpoint not found: {checkpoint}")
    with (repo / "datasets/dms/model_classes.csv").open(newline="", encoding="utf-8") as f: names = {int(r["model_channel"]): r["material_name"] for r in csv.DictReader(f)}
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu"); print(f"Loading {checkpoint.name} on {device}..."); model, size = load_model(checkpoint, device)
    cap = cv2.VideoCapture(a.camera)
    if not cap.isOpened(): raise SystemExit("Could not open camera. Check camera index and permissions.")
    frame_no, mask = 0, None
    try:
        while True:
            ok, frame = cap.read()
            if not ok: break
            frame_no += 1
            if frame_no % max(1, a.every) == 0:
                rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB); small = cv2.resize(rgb, (size, size), interpolation=cv2.INTER_LINEAR)
                image = normalize(to_tensor(small), [.485, .456, .406], [.229, .224, .225]).unsqueeze(0).to(device)
                with torch.inference_mode():
                    probs = torch.softmax(model(image)["out"][0], dim=0); confidence, prediction = probs.max(0)
                mask = (prediction.cpu().numpy(), confidence.cpu().numpy())
            if mask is not None:
                prediction, confidence = mask; prediction = cv2.resize(prediction.astype(np.uint8), (frame.shape[1], frame.shape[0]), interpolation=cv2.INTER_NEAREST); confidence = cv2.resize(confidence, (frame.shape[1], frame.shape[0]), interpolation=cv2.INTER_LINEAR)
                for channel in np.unique(prediction):
                    if channel not in names: continue
                    if names[int(channel)] not in MATERIAL_FILTER: continue
                    region = ((prediction == channel) & (confidence >= a.confidence)).astype(np.uint8); count, _, stats, _ = cv2.connectedComponentsWithStats(region, 8)
                    for x, y, w, h, area in stats[1:]:
                        if area < frame.shape[0] * frame.shape[1] * .015: continue
                        label = names[int(channel)]; cv2.rectangle(frame, (x, y), (x+w, y+h), (92, 255, 120), 2); (tw, th), _ = cv2.getTextSize(label, cv2.FONT_HERSHEY_SIMPLEX, .65, 2); cv2.rectangle(frame, (x, max(0, y-th-12)), (x+tw+12, y), (92, 255, 120), -1); cv2.putText(frame, label, (x+6, y-7), cv2.FONT_HERSHEY_SIMPLEX, .65, (20, 35, 0), 2, cv2.LINE_AA)
            cv2.putText(frame, "Fitwell AI | Q/Esc to quit", (15, 30), cv2.FONT_HERSHEY_SIMPLEX, .7, (255,255,255), 2, cv2.LINE_AA); cv2.imshow("Fitwell AI - Material Camera", frame)
            if cv2.waitKey(1) & 0xFF in (ord("q"), 27): break
    finally: cap.release(); cv2.destroyAllWindows()

if __name__ == "__main__": main()
