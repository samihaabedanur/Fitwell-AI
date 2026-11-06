"""Live webcam material identification using the trained material model."""
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
NON_MATERIAL_LABELS = {
    "Animal skin", "Bone/teeth/horn", "Chalkboard/blackboard", "Clutter", "Fire",
    "Foliage", "Food", "Fur", "Hair", "Ice", "Leather", "Paper", "Photograph/painting",
    "Sand", "Skin/lips", "Sky", "Snow", "Soil/mud", "Water", "Wax",
}

def load_model(checkpoint, device):
    saved = torch.load(checkpoint, map_location=device, weights_only=True)
    model = deeplabv3_mobilenet_v3_large(weights=None, weights_backbone=None, num_classes=46, aux_loss=True)
    model.classifier[-1] = torch.nn.Conv2d(model.classifier[-1].in_channels, 46, 1)
    model.aux_classifier[-1] = torch.nn.Conv2d(model.aux_classifier[-1].in_channels, 46, 1)
    model.load_state_dict(saved["state_dict"]); model.to(device).eval()
    return model, saved.get("size", 256)

def load_impacts(path):
    if not path.is_file():
        return {}
    with path.open(newline="", encoding="utf-8-sig") as f:
        records = {}
        for row in csv.DictReader(f):
            records[row["material_name"].strip().casefold()] = row
        return records

def draw_impact_panel(frame, record, label):
    if not record:
        lines = [label, "Environmental information unavailable", "Try another material view"]
    else:
        lines = [label, f"Indicator: {record['impact_indicator']}", f"Value: {record['value']} {record['unit']}", f"Lifecycle: {record['lifecycle_module']}", f"Datasets: {record.get('dataset_count', 'n/a')}"]
    x, y, w, h = 24, max(8, frame.shape[0] - 154), min(frame.shape[1] - 48, 720), 138
    overlay = frame.copy(); cv2.rectangle(overlay, (x, y), (x + w, y + h), (15, 25, 25), -1); cv2.addWeighted(overlay, .9, frame, .1, 0, frame)
    for index, line in enumerate(lines):
        cv2.putText(frame, line, (x + 12, y + 19 + index * 22), cv2.FONT_HERSHEY_SIMPLEX, .36 if index else .44, (210, 255, 210) if index == 0 else (240, 240, 240), 1, cv2.LINE_AA)

def main():
    p = argparse.ArgumentParser(); p.add_argument("--checkpoint", type=Path, default=Path("training/runs/dms-expanded/best.pt")); p.add_argument("--camera", type=int, default=0); p.add_argument("--image", type=Path, help="Analyze one image instead of opening the webcam"); p.add_argument("--confidence", type=float, default=.15); p.add_argument("--every", type=int, default=3)
    a = p.parse_args(); repo = Path(__file__).resolve().parent; checkpoint = (repo / a.checkpoint).resolve()
    if not checkpoint.is_file(): raise SystemExit(f"Checkpoint not found: {checkpoint}")
    with (repo / "datasets/dms/model_classes.csv").open(newline="", encoding="utf-8") as f: names = {int(r["model_channel"]): r["material_name"] for r in csv.DictReader(f)}
    impacts = load_impacts(repo / "datasets/oekobaudat/environmental_lookup.csv")
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu"); print(f"Loading {checkpoint.name} on {device}..."); model, size = load_model(checkpoint, device)
    image_path = None
    if a.image:
        requested = Path(a.image).expanduser()
        if not requested.is_absolute(): requested = repo / requested
        if requested.is_dir():
            choices = sorted(p for p in requested.iterdir() if p.suffix.lower() in {'.jpg', '.jpeg', '.png', '.bmp', '.webp'})
            if not choices: raise SystemExit(f"No supported images found in: {requested.resolve()}")
            requested = choices[0]
        image_path = requested.resolve()
    static_frame = cv2.imread(str(image_path)) if image_path else None
    if a.image and static_frame is None: raise SystemExit(f"Could not read image: {image_path}")
    if image_path: print(f"Loaded image: {image_path}")
    cap = None if a.image else cv2.VideoCapture(a.camera, cv2.CAP_DSHOW)
    if cap is not None and not cap.isOpened(): raise SystemExit("Could not open camera. Check camera index and permissions.")
    if cap is not None:
        cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
        cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)
    frame_no, mask, detections = 0, None, []
    selected = {"label": None}
    display_shape = {"width": 1280, "height": 720, "window_width": 1280, "window_height": 720}
    def on_click(event, x, y, flags, param):
        if event == cv2.EVENT_LBUTTONDOWN:
            frame_x = int(x * display_shape["width"] / max(1, display_shape["window_width"]))
            frame_y = int(y * display_shape["height"] / max(1, display_shape["window_height"]))
            for box_x, box_y, box_w, box_h, label in detections:
                if box_x <= frame_x <= box_x + box_w and box_y <= frame_y <= box_y + box_h:
                    selected["label"] = label
                    break
    window = "Fitwell AI - Material Camera"
    cv2.namedWindow(window, cv2.WINDOW_NORMAL)
    cv2.resizeWindow(window, 1280, 820)
    cv2.setMouseCallback(window, on_click)
    try:
        while True:
            if static_frame is not None:
                ok, frame = True, cv2.resize(static_frame.copy(), (1280, 720), interpolation=cv2.INTER_AREA)
            else:
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
                detections = []
                prediction, confidence = mask; prediction = cv2.resize(prediction.astype(np.uint8), (frame.shape[1], frame.shape[0]), interpolation=cv2.INTER_NEAREST); confidence = cv2.resize(confidence, (frame.shape[1], frame.shape[0]), interpolation=cv2.INTER_LINEAR)
                for channel in np.unique(prediction):
                    if channel not in names: continue
                    if names[int(channel)] in NON_MATERIAL_LABELS: continue
                    region = ((prediction == channel) & (confidence >= a.confidence)).astype(np.uint8); count, _, stats, _ = cv2.connectedComponentsWithStats(region, 8)
                    for x, y, w, h, area in stats[1:]:
                        if area < frame.shape[0] * frame.shape[1] * .003: continue
                        max_w, max_h = int(frame.shape[1] * .18), int(frame.shape[0] * .18)
                        if w > max_w or h > max_h:
                            center_x, center_y = x + w // 2, y + h // 2
                            w, h = min(w, max_w), min(h, max_h)
                            x, y = max(0, center_x - w // 2), max(0, center_y - h // 2)
                        label = names[int(channel)]; cv2.rectangle(frame, (x, y), (x+w, y+h), (120, 255, 150), 1); (tw, th), _ = cv2.getTextSize(label, cv2.FONT_HERSHEY_SIMPLEX, .30, 1); cv2.rectangle(frame, (x, max(0, y-th-6)), (x+tw+8, y), (120, 255, 150), -1); cv2.putText(frame, label, (x+4, y-4), cv2.FONT_HERSHEY_SIMPLEX, .30, (15, 35, 15), 1, cv2.LINE_AA)
                        detections.append((x, y, w, h, label))
                # If the prediction is fragmented, still show the strongest material region.
                if not detections:
                    candidates = []
                    for channel in np.unique(prediction):
                        label = names.get(int(channel))
                        if not label or label in NON_MATERIAL_LABELS: continue
                        region = ((prediction == channel) & (confidence >= a.confidence)).astype(np.uint8)
                        count, _, stats, _ = cv2.connectedComponentsWithStats(region, 8)
                        if count > 1:
                            best = stats[1:][np.argmax(stats[1:, cv2.CC_STAT_AREA])]
                            if best[cv2.CC_STAT_AREA] > 20: candidates.append((int(best[cv2.CC_STAT_AREA]), int(channel), best))
                    if candidates:
                        _, channel, best = max(candidates, key=lambda item: item[0])
                        x, y, w, h = [int(value) for value in best[:4]]
                        label = names[channel]
                        cv2.rectangle(frame, (x, y), (x + w, y + h), (120, 255, 150), 1)
                        cv2.putText(frame, label, (x + 4, max(16, y - 4)), cv2.FONT_HERSHEY_SIMPLEX, .30, (120, 255, 150), 1, cv2.LINE_AA)
                        detections.append((x, y, w, h, label))
            if selected["label"]:
                draw_impact_panel(frame, impacts.get(selected["label"].strip().casefold()), selected["label"])
            cv2.imshow(window, frame)
            _, _, display_width, display_height = cv2.getWindowImageRect(window)
            display_shape.update(width=frame.shape[1], height=frame.shape[0], window_width=display_width, window_height=display_height)
            if cv2.waitKey(30 if static_frame is not None else 1) & 0xFF in (ord("q"), 27): break
    finally:
        if cap is not None: cap.release()
        cv2.destroyAllWindows()

if __name__ == "__main__": main()
