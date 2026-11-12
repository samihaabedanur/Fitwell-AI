"""Apple DMS46 material-recognition launcher.

This is a named entry point for the included Apple DMS model. The model path
is configured in recognise.py as models/DMS46_v1.pt.
Run with:
    .venv\Scripts\python.exe apple_dms.py
"""

from pathlib import Path
import runpy


if __name__ == "__main__":
    runpy.run_path(str(Path(__file__).with_name("app.py")), run_name="__main__")
