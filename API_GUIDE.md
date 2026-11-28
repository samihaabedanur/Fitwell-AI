# Fitwell model server: how the website calls it

**Server:** https://huggingface.co/spaces/HetaKalyani/fitwell-model-server (free, GPU on demand)
**Address:** https://hetakalyani-fitwell-model-server.hf.space

Send one image, get back every material found on it, 5 similar materials for each, and a material passport for each match.

## 1. Install the client (once)
```bash
npm install @gradio/client
```

## 2. Call it (JavaScript / TypeScript, works in Next.js, React, plain JS)
```js
import { Client } from "@gradio/client";

const client = await Client.connect("HetaKalyani/fitwell-model-server");

// file = the File from an <input type="file"> (or a Blob)
// mode = "board" for a mood board, "single" for one material photo
const res = await client.predict("/analyze", { image: file, mode: "board" });
const data = JSON.parse(res.data[0]);
```
A call takes about 10 to 60 seconds (longer the first time, while the GPU wakes up). Show a loading message.

## 3. What comes back
```json
{
  "mode": "board", "width": 740, "height": 415,
  "materials": [
    {
      "type": "Fabric",                        // material type
      "flagged": false,                        // true = "Check: may include an object" (show these last, or hide them)
      "label": "Fabric",
      "material_confidence": 0.93,
      "samples": [ { "box": [x0, y0, x1, y1], "image": "data:image/jpeg;base64,..." } ],   // cut-outs from the upload
      "matches": [                             // 5 similar materials, best first
        {
          "score": 0.81,                       // similarity, 0 to 1
          "category": "Fabric",
          "thumb": "data:image/jpeg;base64,...",   // use directly in <img src>
          "passport": {
            "name": "Fabric 036", "category": "Fabric",
            "tags": "['clean', 'fabric', 'woven']",
            "source": "ambientcg", "link": "https://www.ambientcg.com/view?id=Fabric036",
            "license": "CC0", "physical_size": "nan", "description": ""
          }
        }
      ]
    }
  ]
}
```
- `samples[].image` and `matches[].thumb` are ready-to-use images (`<img src={...}>`).
- `box` is where the sample sits on the uploaded image, in pixels of the resized image (`width` × `height`).
- `physical_size` is "nan" when unknown. `tags` is a list written as text.
- Saving results to Supabase: store the whole JSON in a `jsonb` column.

## 4. Ready-made pages
`web/` in this repo is a Next.js version with upload, results and passport pop-up
(`web/components/Analyzer.tsx`, `Results.tsx`, `PassportModal.tsx`, `web/lib/api.ts`). Copy what you need.

## Limits
- Max image size 10 MB. Big photos are shrunk to 1024 px on the server.
- Free ZeroGPU has a daily GPU quota per account: fine for testing and demos.
