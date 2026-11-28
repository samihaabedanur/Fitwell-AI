"use client";
import { useEffect } from "react";
import { parseTags, sizeText, type Match } from "@/lib/api";

export default function PassportModal({ m, onClose }: { m: Match; onClose: () => void }) {
  useEffect(() => {
    const k = (e: KeyboardEvent) => e.key === "Escape" && onClose();
    window.addEventListener("keydown", k); return () => window.removeEventListener("keydown", k);
  }, [onClose]);
  const p = m.passport;
  const tags = parseTags(p.tags);
  return (
    <div className="modal" onClick={onClose} role="dialog" aria-modal="true" aria-label={`Material passport: ${p.name}`}>
      <div className="card" onClick={(e) => e.stopPropagation()}>
        <img src={m.thumb} alt={p.name} />
        <div>
          <div className="label">Material passport</div>
          <h2 style={{ margin: "4px 0 2px" }}>{p.name}</h2>
          <span className="pill">{p.category}</span>
          <dl>
            <dt>Similarity</dt><dd>{Math.round(m.score * 100)}%</dd>
            <dt>Description</dt><dd>{p.description || "Not given"}</dd>
            <dt>Physical size</dt><dd>{sizeText(p.physical_size)}</dd>
            <dt>Source</dt><dd>{p.source || "Not given"}</dd>
            <dt>Licence</dt><dd>{p.license || "Not given"}</dd>
            <dt>Link</dt><dd>{p.link ? <a href={p.link} target="_blank" rel="noreferrer">{p.link}</a> : "Not given"}</dd>
          </dl>
          {tags.length > 0 && <div className="tags">{tags.map((t) => <span key={t} className="pill soft">{t}</span>)}</div>}
          <div style={{ marginTop: 18 }}><button className="btn" onClick={onClose}>Close</button></div>
        </div>
      </div>
    </div>
  );
}
