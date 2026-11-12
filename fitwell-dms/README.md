# Fitwell pretrained material recognition

Includes the original Apple DMS46 pretrained TorchScript model; no training required.

## Windows
1. Install Python 3.12 (python.org, including the Python launcher) if needed.
2. Extract the ZIP completely. Open this folder in VS Code.
3. Double-click START_WINDOWS.cmd. It creates a local virtual environment, installs dependencies, and opens the image scanner.
4. Choose a room photograph; click the coloured prediction to see its material name.

For VS Code debugging install Microsoft's Python and Python Debugger extensions, select .venv as the Python interpreter, then use the included launch configuration.

Command-line alternative after setup:
`.venv\Scripts\python.exe recognise.py images\your_room.jpg`

CPU inference is supported by this wrapper but can be slow. CUDA is selected automatically when available in the installed PyTorch build. Dependencies require an internet connection on first setup. The graphical viewer needs Tkinter (included with standard Windows Python).

Outputs: original image, material-index mask, coloured overlay and JSON with predicted image area per material. Area percentages are pixel proportions, not confidence scores or physical surface areas. This is an uploaded-image prototype; live camera and environmental product data are not integrated.

## Sources and reuse
Model and taxonomy: https://github.com/apple-aiml-research/ml-dms-dataset
Weights: https://docs-assets.developer.apple.com/ml-research/datasets/dms/dms46_v1.zip
Preprocessing and output indexing follow Apple's inference.py. See LICENSE-Apple.txt and ACKNOWLEDGMENTS.txt for upstream terms. Original dataset annotations are CC BY-NC 4.0; source photographs have separate licences. This package includes no training photographs.

Cite: Paul Upchurch and Ransen Niu, A Dense Material Segmentation Dataset for Indoor and Outdoor Scene Parsing, ECCV 2022.

Predictions describe visible material categories. They cannot establish product composition, embodied carbon, fire ratings or sustainability scores. Test on your own labelled room images before reporting performance.

## MINC Materials-23 classifier

This project also includes the locally downloaded Hugging Face model `prithivMLmods/Minc-Materials-23` in `models/minc-materials-23`. It is a 23-class SigLIP image classifier for individual material images or surface crops; it does not segment a whole room.

Run the command-line classifier:
`.venv\Scripts\python.exe minc_predict.py path\to\material_or_crop.jpg`

Run the desktop upload/crop interface:
`.venv\Scripts\python.exe minc_app.py`

Click **Open image** for a material photo or room photo. Drag a rectangle over a surface to classify the crop, or click **Classify whole image**. The model source is https://huggingface.co/prithivMLmods/Minc-Materials-23 and its repository lists the license as Apache-2.0. The downloaded model README is retained in `models/minc-materials-23/README.md`; follow the model card and license terms when redistributing. The Apple DMS files and interface remain separate.

## Zero-Shot Material State Similarity Net

The authors' source is included under `external/Zero-Shot-Material-State-Segmentation-Net`, with its original `README.md` and `LICENSE` preserved. The repository is CC0 1.0 Universal. The exact pretrained checkpoint linked by the authors (`Defult.torch`, 531,724,866 bytes) is stored at `models/zero-shot-material/Defult.torch`. The author links are retained in the external README: [pCloud](https://e.pcloud.link/publink/show?code=XZlQvMZzlpiakIEdXpB3lwC7kVX9HXnH5jk) and [Icedrive](https://icedrive.net/s/h44XCxwYa1ikAthT7vQF74w6B3W8). No substitute weights are used.

Launch the separate click-to-similarity interface:
`.venv\Scripts\python.exe zero_shot_app.py`

Click **Open room photo**, then click a surface. Bright areas in the similarity map are visually similar to the clicked material according to the zero-shot descriptor network; this map is not a material name or confidence score. The optional **Classify MINC crop around selected point** button runs the separate MINC-23 classifier on a small crop and prints its material name/scores separately. This network uses CPU if CUDA is unavailable and may take time on the first click.
