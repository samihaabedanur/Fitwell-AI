"""Optional Replicate-backed interior redesign for Fitwell.

This adapter keeps the remote image-generation call separate from Fitwell's
material-recognition model. Set REPLICATE_API_TOKEN before using it.
"""
from __future__ import annotations

import argparse
import os
from pathlib import Path
from typing import Any


DEFAULT_MODEL = "adirik/interior-design"


def _output_bytes(output: Any) -> bytes:
    """Read a Replicate output object, URL, or byte payload."""
    if isinstance(output, bytes):
        return output
    if hasattr(output, "read"):
        return output.read()
    if isinstance(output, (list, tuple)):
        if not output:
            raise RuntimeError("Replicate returned no generated image")
        return _output_bytes(output[0])
    if isinstance(output, str):
        import urllib.request
        with urllib.request.urlopen(output, timeout=120) as response:
            return response.read()
    if hasattr(output, "url"):
        return _output_bytes(output.url())
    raise TypeError(f"Unsupported Replicate output type: {type(output)!r}")


def redesign_room(
    image_path: str | Path,
    prompt: str,
    output_path: str | Path,
    *,
    model: str = DEFAULT_MODEL,
) -> Path:
    """Generate a redesign from one room image and save it locally."""
    token = os.environ.get("REPLICATE_API_TOKEN", "").strip()
    if not token:
        raise RuntimeError("Set REPLICATE_API_TOKEN before requesting a redesign")

    try:
        import replicate
    except ImportError as exc:
        raise RuntimeError(
            "Install the optional redesign dependency with: pip install replicate"
        ) from exc

    image = Path(image_path)
    if not image.is_file():
        raise FileNotFoundError(image)
    destination = Path(output_path)
    destination.parent.mkdir(parents=True, exist_ok=True)

    client = replicate.Client(api_token=token)
    with image.open("rb") as source:
        result = client.run(model, input={"image": source, "prompt": prompt})
    destination.write_bytes(_output_bytes(result))
    return destination


def main() -> None:
    parser = argparse.ArgumentParser(description="Redesign a room image through Replicate")
    parser.add_argument("image", type=Path)
    parser.add_argument("prompt")
    parser.add_argument("--output", type=Path, default=Path("outputs/redesign.png"))
    parser.add_argument("--model", default=DEFAULT_MODEL)
    args = parser.parse_args()
    saved = redesign_room(args.image, args.prompt, args.output, model=args.model)
    print(f"Saved redesign to {saved.resolve()}")


if __name__ == "__main__":
    main()
