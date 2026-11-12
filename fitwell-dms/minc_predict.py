"""Local inference for prithivMLmods/Minc-Materials-23."""
import argparse
from pathlib import Path
import torch
from PIL import Image, ImageOps
from transformers import AutoImageProcessor, AutoModelForImageClassification

ROOT = Path(__file__).resolve().parent
MODEL_DIR = ROOT / "models" / "minc-materials-23"


def load_model():
    device = "cuda" if torch.cuda.is_available() else "cpu"
    processor = AutoImageProcessor.from_pretrained(str(MODEL_DIR), local_files_only=True)
    model = AutoModelForImageClassification.from_pretrained(str(MODEL_DIR), local_files_only=True)
    return processor, model.to(device).eval(), device


def predict(image, processor, model, device, top_k=3):
    image = ImageOps.exif_transpose(image).convert("RGB")
    inputs = processor(images=image, return_tensors="pt")
    inputs = {key: value.to(device) for key, value in inputs.items()}
    with torch.inference_mode():
        logits = model(**inputs).logits
        scores = torch.softmax(logits, dim=-1)[0]
    values, indices = torch.topk(scores, k=top_k)
    return [(model.config.id2label[int(index)], float(value)) for value, index in zip(values, indices)]


def predict_path(path, top_k=3):
    processor, model, device = load_model()
    return predict(Image.open(path), processor, model, device, top_k)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Classify a material image or surface crop.")
    parser.add_argument("image", help="Path to a JPG, PNG, WebP, or other Pillow-readable image")
    args = parser.parse_args()
    processor, model, device = load_model()
    print(f"Device: {device}")
    for rank, (label, score) in enumerate(predict(Image.open(args.image), processor, model, device), 1):
        print(f"{rank}. {label}: {score:.2%}")
