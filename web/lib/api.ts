import { Client } from "@gradio/client";

/** Hugging Face Space that runs the Fitwell model, as "username/space-name" */
export const MODEL_SPACE = process.env.NEXT_PUBLIC_MODEL_SPACE || "HetaKalyani/fitwell-model-server";

export type Passport = {
  name: string; category: string; tags: string; source: string; link: string;
  license: string; physical_size: string; description: string;
};
/** thumb is a small image as a data: URL, ready for <img src> */
export type Match = { lib_index: number; score: number; category: string; thumb: string; passport: Passport };
export type Sample = { box: [number, number, number, number]; image: string };
export type Material = {
  type: string; flagged: boolean; label: string;
  material_confidence: number; type_agreement: number;
  samples: Sample[]; matches: Match[];
};
export type Analysis = { mode: "board" | "single"; width: number; height: number; materials: Material[] };

/** Shrink big photos in the browser before upload (faster, and the server uses 1024 px anyway). */
async function shrink(file: File, max = 1600): Promise<Blob> {
  const bmp = await createImageBitmap(file);
  const s = Math.min(1, max / Math.max(bmp.width, bmp.height));
  if (s === 1 && file.size < 3_000_000) return file;
  const c = document.createElement("canvas");
  c.width = Math.round(bmp.width * s); c.height = Math.round(bmp.height * s);
  c.getContext("2d")!.drawImage(bmp, 0, 0, c.width, c.height);
  return await new Promise<Blob>((ok) => c.toBlob((b) => ok(b!), "image/jpeg", 0.9));
}

let clientPromise: Promise<Client> | null = null;
function client() {
  if (!clientPromise) clientPromise = Client.connect(MODEL_SPACE);
  return clientPromise;
}

export async function analyse(file: File, mode: "board" | "single"): Promise<Analysis> {
  const c = await client();
  const res = await c.predict("/analyze", { image: await shrink(file), mode });
  const out = (res.data as unknown[])[0];
  return (typeof out === "string" ? JSON.parse(out) : out) as Analysis;
}

/** Connecting also wakes a sleeping Space. */
export async function wake(): Promise<boolean> {
  try { await client(); return true; } catch { clientPromise = null; return false; }
}

/** "['wood', 'oak']" (as stored in the MatSynth metadata) -> ["wood", "oak"] */
export function parseTags(t: string): string[] {
  if (!t) return [];
  return t.replace(/^\[|\]$/g, "").split(",").map((s) => s.trim().replace(/^'|'$/g, "")).filter(Boolean);
}

export function sizeText(v: string): string {
  const n = parseFloat(v);
  return Number.isFinite(n) ? `${n} cm sample width` : "Not given";
}
