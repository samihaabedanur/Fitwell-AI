---
title: Fitwell Model Server
emoji: 🔥
colorFrom: blue
colorTo: red
sdk: gradio
sdk_version: 6.32.0
python_version: '3.12'
app_file: app.py
pinned: false
license: mit
short_description: 'Material clustering'
---

# Fitwell model server (v8)

Upload a mood board (`mode=board`) or one material photo (`mode=single`).
Returns every material found, its samples, 5 matches from 3,246 CC0 materials, and a material passport for each match.

## Call it from a website (JavaScript)
```js
import { Client } from "@gradio/client";
const client = await Client.connect("HetaKalyani/fitwell-model-server");
const result = await client.predict("/analyze", { image: fileOrBlob, mode: "board" });
const data = result.data[0];   // { mode, width, height, materials: [...] }
```

## Call it from Python
```python
from gradio_client import Client, handle_file
c = Client("HetaKalyani/fitwell-model-server")
data = c.predict(handle_file("board.jpg"), "board", api_name="/analyze")
```

Pipeline: SAM (facebook/sam-vit-base) cuts samples, drops plain background → DINOv2-small + Fitwell head
(trained on MINC-2500 + MatSynth) → grouping per material type → search (0.5 Fitwell head + 0.5 DINOv2)
with colour re-ranking → CLIP object check ("Check: may include an object").

Model files (in `bundle/` or next to app.py): `fitwell_index.npz`, `fitwell_head_state.pt`, `passports.json`, `thumbs.zip`.

Data credits: MatSynth (CC0 subset), MINC-2500 (CC BY 4.0, Bell et al. 2015).
