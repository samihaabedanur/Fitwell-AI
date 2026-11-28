"use client";
import { useState } from "react";
import { type Analysis, type Match, type Material } from "@/lib/api";
import PassportModal from "./PassportModal";

function Group({ g, onOpen }: { g: Material; onOpen: (m: Match) => void }) {
  return (
    <div className="group">
      <div>
        <div style={{ display: "flex", gap: 8, alignItems: "center", marginBottom: 8, flexWrap: "wrap" }}>
          <strong style={{ fontSize: 18 }}>{g.type}</strong>
          {g.flagged && <span className="pill warn">Check: may include an object</span>}
        </div>
        <div className="samples">
          {g.samples.map((s, i) => <img key={i} src={s.image} alt={`Sample ${i + 1} on your upload`} />)}
        </div>
        <div style={{ color: "var(--muted)", fontSize: 13, marginTop: 8 }}>
          {g.samples.length} sample{g.samples.length > 1 ? "s" : ""} on your upload
        </div>
      </div>
      <div className="matches">
        {g.matches.map((m) => (
          <button key={m.lib_index} className="match" onClick={() => onOpen(m)}>
            <img src={m.thumb} alt={m.passport.name} loading="lazy" />
            <div><b>{m.passport.name}</b>{m.category} · {Math.round(m.score * 100)}% similar</div>
          </button>
        ))}
      </div>
    </div>
  );
}

export default function Results({ data }: { data: Analysis }) {
  const [open, setOpen] = useState<Match | null>(null);
  const clean = data.materials.filter((g) => !g.flagged);
  const flagged = data.materials.filter((g) => g.flagged);
  return (
    <section style={{ marginTop: 28 }}>
      <h2 style={{ marginBottom: 4 }}>
        {clean.length} material{clean.length === 1 ? "" : "s"} found
      </h2>
      <p style={{ color: "var(--muted)", marginTop: 0 }}>Click a match to open its material passport.</p>
      {clean.map((g, i) => <Group key={i} g={g} onOpen={setOpen} />)}
      {flagged.length > 0 && (
        <details className="flagged">
          <summary>{flagged.length} more cut-out{flagged.length > 1 ? "s" : ""} that may include an object</summary>
          {flagged.map((g, i) => <Group key={i} g={g} onOpen={setOpen} />)}
        </details>
      )}
      {data.materials.length === 0 && <p className="status">No material found. Try a closer or brighter photo.</p>}
      {open && <PassportModal m={open} onClose={() => setOpen(null)} />}
    </section>
  );
}
