# Fitwell website (Next.js)

Pages: home, mood board upload, single material upload, link to the 2D to 3D planner.
It calls the Fitwell model server (`../model-server`, a Hugging Face Space).

## Run on your laptop
1. Install Node.js 20 (https://nodejs.org).
2. In this folder: `npm install`
3. Copy `.env.example` to `.env.local` and check `NEXT_PUBLIC_MODEL_SPACE`.
4. `npm run dev`, then open http://localhost:3000

## Deploy (Vercel, free)
Import the GitHub repo on vercel.com, set **Root Directory** to `web`, add the two variables from `.env.example`, deploy.
