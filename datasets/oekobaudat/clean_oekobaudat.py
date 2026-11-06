"""Clean the official ÖKOBAUDAT CSV and create research audit outputs."""
import json
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pandas as pd

ROOT = Path(__file__).resolve().parent
RAW = ROOT / "environmental_records.csv"
OUT = ROOT / "analysis"
REQUIRED = ["UUID", "Version", "Name (en)", "Kategorie (en)", "Typ", "Bezugseinheit", "Modul", "GWPtotal (A2)", "URL"]


def main():
    if not RAW.exists():
        raise SystemExit(f"Missing {RAW}; download the official ÖKOBAUDAT CSV first.")
    OUT.mkdir(exist_ok=True)
    raw = pd.read_csv(RAW, sep=";", dtype=str, encoding="cp1252", low_memory=False)
    missing = [c for c in REQUIRED if c not in raw.columns]
    if missing:
        raise SystemExit(f"Missing required columns: {missing}")
    cleaned = raw[REQUIRED].copy()
    before = len(cleaned)
    for col in ["UUID", "Version", "Name (en)", "Kategorie (en)", "Typ", "Bezugseinheit", "Modul", "URL"]:
        cleaned[col] = cleaned[col].fillna("").astype(str).str.strip()
    cleaned["gwp_total_kg_co2e"] = pd.to_numeric(cleaned["GWPtotal (A2)"].str.replace(",", ".", regex=False), errors="coerce")
    missing_values_removed = int((cleaned["Name (en)"].eq("") | cleaned["Bezugseinheit"].eq("") | cleaned["gwp_total_kg_co2e"].isna()).sum())
    cleaned = cleaned[(cleaned["Name (en)"] != "") & (cleaned["Bezugseinheit"] != "") & cleaned["gwp_total_kg_co2e"].notna()]
    before_dedup = len(cleaned)
    cleaned = cleaned.drop_duplicates(["UUID", "Version", "Modul", "Bezugseinheit", "gwp_total_kg_co2e"])
    cleaned["material_category"] = cleaned["Kategorie (en)"].str.replace("'", "", regex=False).str.split("/").str[0].str.strip()
    cleaned = cleaned[["UUID", "Version", "Name (en)", "material_category", "Typ", "Bezugseinheit", "Modul", "gwp_total_kg_co2e", "URL"]]
    cleaned.to_csv(ROOT / "environmental_records_clean.csv", index=False)

    report = {
        "source": "ÖKOBAUDAT 2024-II CSV export",
        "rows_before_cleaning": int(before),
        "rows_after_cleaning": int(len(cleaned)),
        "rows_removed": int(before - len(cleaned)),
        "duplicate_rows_removed": int(before_dedup - len(cleaned)),
        "missing_required_values_removed": missing_values_removed,
        "material_categories": int(cleaned["material_category"].nunique()),
        "lifecycle_modules": cleaned["Modul"].value_counts().to_dict(),
        "dataset_types": cleaned["Typ"].value_counts().to_dict(),
        "gwp_unit_counts": cleaned["Bezugseinheit"].value_counts().to_dict(),
    }
    (OUT / "cleaning_report.json").write_text(json.dumps(report, indent=2, ensure_ascii=False), encoding="utf-8")
    cleaned["material_category"].value_counts().head(20).sort_values().plot(kind="barh", title="ÖKOBAUDAT cleaned records by category")
    plt.xlabel("Records"); plt.tight_layout(); plt.savefig(OUT / "records_by_category.png", dpi=160); plt.close()
    cleaned["Modul"].value_counts().head(20).sort_values().plot(kind="barh", title="ÖKOBAUDAT cleaned lifecycle modules")
    plt.xlabel("Records"); plt.tight_layout(); plt.savefig(OUT / "records_by_lifecycle_module.png", dpi=160); plt.close()
    cleaned["gwp_total_kg_co2e"].clip(lower=cleaned["gwp_total_kg_co2e"].quantile(.01), upper=cleaned["gwp_total_kg_co2e"].quantile(.99)).plot(kind="hist", bins=40, title="ÖKOBAUDAT GWP-total distribution (1st–99th percentile)")
    plt.xlabel("GWP-total, kg CO2e per source unit"); plt.tight_layout(); plt.savefig(OUT / "gwp_total_distribution.png", dpi=160); plt.close()
    print(json.dumps(report, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
