"use client";
import { useEffect, useRef, useState } from "react";
import { analyse, wake, type Analysis } from "@/lib/api";
import Results from "./Results";

type Props = { mode: "board" | "single"; title: string; intro: string };

export default function Analyzer({ mode, title, intro }: Props) {
  const [file, setFile] = useState<File | null>(null);
  const [preview, setPreview] = useState<string | null>(null);
  const [over, setOver] = useState(false);
  const [busy, setBusy] = useState(false);
  const [awake, setAwake] = useState<boolean | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [result, setResult] = useState<Analysis | null>(null);
  const input = useRef<HTMLInputElement>(null);

  // Free servers sleep: ping on page load so it is warm by the time the user uploads.
  useEffect(() => { wake().then(setAwake); }, []);
  useEffect(() => () => { if (preview) URL.revokeObjectURL(preview); }, [preview]);

  function pick(f: File | undefined) {
    if (!f) return;
    if (!f.type.startsWith("image/")) { setError("Please choose an image file (JPG, PNG or WebP)."); return; }
    setError(null); setResult(null); setFile(f); setPreview(URL.createObjectURL(f));
  }

  async function run() {
    if (!file) return;
    setBusy(true); setError(null); setResult(null);
    try { setResult(await analyse(file, mode)); }
    catch (e) {
      setError(`Something went wrong: ${(e as Error).message}. If the server was asleep, wait a minute and try again.`);
    } finally { setBusy(false); }
  }

  function download() {
    if (!result) return;
    const blob = new Blob([JSON.stringify(result, null, 2)], { type: "application/json" });
    const a = document.createElement("a"); a.href = URL.createObjectURL(blob);
    a.download = `fitwell-${mode}-results.json`; a.click();
  }

  return (
    <section style={{ padding: "36px 0" }}>
      <div className="label">Upload</div>
      <h1 style={{ margin: "6px 0 8px" }}>{title}</h1>
      <p style={{ color: "var(--muted)", maxWidth: 680, marginTop: 0 }}>{intro}</p>

      <div className={`drop${over ? " on" : ""}`}
        onClick={() => input.current?.click()}
        onDragOver={(e) => { e.preventDefault(); setOver(true); }}
        onDragLeave={() => setOver(false)}
        onDrop={(e) => { e.preventDefault(); setOver(false); pick(e.dataTransfer.files[0]); }}>
        <input ref={input} type="file" accept="image/*" hidden onChange={(e) => pick(e.target.files?.[0])} />
        <strong>{file ? file.name : "Drop an image here, or click to choose"}</strong>
        <div style={{ color: "var(--muted)", fontSize: 14 }}>JPG, PNG or WebP, up to 10 MB</div>
        {preview && <div><img src={preview} alt="Your upload" /></div>}
      </div>

      <div style={{ display: "flex", gap: 12, alignItems: "center", marginTop: 16, flexWrap: "wrap" }}>
        <button className="btn" onClick={run} disabled={!file || busy}>
          {busy ? "Analysing…" : "Find materials"}
        </button>
        {result && <button className="btn light" onClick={download}>Download results (JSON)</button>}
        {awake === false && !busy && <span className="pill soft">Model server waking up, this can take a minute</span>}
      </div>

      {busy && <p className="status">Cutting out samples and searching 3,246 materials. This takes 20 to 60 seconds.</p>}
      {error && <p className="error">{error}</p>}
      {result && <Results data={result} />}
    </section>
  );
}
