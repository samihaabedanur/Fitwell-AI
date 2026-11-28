"""Fitwell model server (Gradio + ZeroGPU): upload an image, get every material with matches, groups and passports."""
import json
import spaces
import gradio as gr
import gradio_client.utils as gcu
from pipeline import Fitwell

# Work around a Gradio/pydantic bug ("argument of type 'bool' is not iterable") when building the API page
_orig_schema = gcu._json_schema_to_python_type
def _safe_schema(schema, defs=None):
    return "Any" if isinstance(schema, bool) else _orig_schema(schema, defs)
gcu._json_schema_to_python_type = _safe_schema

model = Fitwell(points_per_side=32)


@spaces.GPU(duration=90)
def analyze(image, mode="board"):
    if image is None:
        raise gr.Error("Please upload an image.")
    result = model.analyse(image, mode=mode if mode in ("board", "single") else "board")
    return json.dumps(result)


with gr.Blocks(title="Fitwell model server") as demo:
    gr.Markdown("# Fitwell model server\nMood board: every material on the board. Single: one material photo. "
                "Returns 5 matches from 3,246 CC0 materials, each with a material passport.")
    with gr.Row():
        with gr.Column():
            image = gr.Image(type="pil", label="Mood board or material photo")
            mode = gr.Radio(["board", "single"], value="board", label="Mode")
            run = gr.Button("Find materials", variant="primary")
        out = gr.Code(language="json", label="Materials, matches and passports (JSON)")
    run.click(analyze, inputs=[image, mode], outputs=out, api_name="analyze")

if __name__ == "__main__":
    demo.queue(max_size=20).launch()
