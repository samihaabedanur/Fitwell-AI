"""Fitwell API for hosted AI features.

Secrets are read only from environment variables. Never put API keys in the
website files or commit them to GitHub.
"""
from __future__ import annotations

import hmac
import os
import tempfile
from pathlib import Path

from flask import Flask, jsonify, request, send_file
from flask_cors import CORS

from fitwell_interior_design import redesign_room

app = Flask(__name__)
origins = os.environ.get("FITWELL_ALLOWED_ORIGINS", "http://localhost:8000")
CORS(app, resources={r"/api/*": {"origins": [item.strip() for item in origins.split(",")]}})


def authorized() -> bool:
    expected = os.environ.get("FITWELL_API_TOKEN", "")
    supplied = request.headers.get("X-Fitwell-Token", "")
    return bool(expected) and hmac.compare_digest(supplied, expected)


@app.get("/api/health")
def health():
    return jsonify({"ok": True, "features": {"replicate_redesign": bool(os.environ.get("REPLICATE_API_TOKEN"))}})


@app.post("/api/redesign")
def redesign():
    if not authorized():
        return jsonify({"error": "Unauthorized"}), 401
    upload = request.files.get("image")
    prompt = request.form.get("prompt", "modern sustainable interior")
    if upload is None or not upload.filename:
        return jsonify({"error": "Upload a room image in the image field"}), 400
    if not os.environ.get("REPLICATE_API_TOKEN"):
        return jsonify({"error": "REPLICATE_API_TOKEN is not configured"}), 503
    suffix = Path(upload.filename).suffix or ".jpg"
    with tempfile.TemporaryDirectory() as directory:
        source = Path(directory) / f"source{suffix}"
        output = Path(directory) / "redesign.png"
        upload.save(source)
        try:
            redesign_room(source, prompt, output)
        except Exception as error:
            app.logger.exception("Redesign failed")
            return jsonify({"error": str(error)}), 502
        return send_file(output, mimetype="image/png", download_name="fitwell-redesign.png")


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", "10000")))
