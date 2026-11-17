#!/usr/bin/env python3
"""EXP-01: importa CSV, valida i campi e ricostruisce il DFG delle frequenze.

Esecuzione dalla cartella progetto: python scripts/exp01_dfg.py
Un file diverso può essere passato come primo argomento.
"""
from __future__ import annotations

import csv
import hashlib
import json
from pathlib import Path
import sys

import pandas as pd
import pm4py

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_INPUT = ROOT / "data" / "synthetic_manufacturing.csv"
RESULTS = ROOT / "results"


def main() -> None:
    path = Path(sys.argv[1]).expanduser().resolve() if len(sys.argv) > 1 else DEFAULT_INPUT
    if not path.is_file():
        raise FileNotFoundError(f"Dataset non trovato: {path}")

    df = pd.read_csv(path, dtype={"case_id": "string", "activity": "string"})
    required = {"case_id", "activity", "timestamp"}
    missing = required.difference(df.columns)
    if missing:
        raise ValueError(f"Colonne obbligatorie mancanti: {sorted(missing)}")
    if df.empty or df[["case_id", "activity", "timestamp"]].isna().any().any():
        raise ValueError("Dataset vuoto o con campi obbligatori nulli")
    if (df["case_id"].str.strip() == "").any() or (df["activity"].str.strip() == "").any():
        raise ValueError("Case ID o attività vuoti")
    # Converte i tempi in UTC; usa un ordinamento stabile nei casi a timestamp identico.
    df["timestamp"] = pd.to_datetime(df["timestamp"], utc=True, errors="raise")
    df = df.sort_values(["case_id", "timestamp"], kind="mergesort")

    log = pm4py.format_dataframe(
        df,
        case_id="case_id",
        activity_key="activity",
        timestamp_key="timestamp",
    )
    dfg, start_activities, end_activities = pm4py.discover_dfg(log)
    rows = [
        {"source": source, "target": target, "frequency": int(freq)}
        for (source, target), freq in sorted(dfg.items())
    ]

    RESULTS.mkdir(parents=True, exist_ok=True)
    path_csv = RESULTS / "exp01_dfg_frequency.csv"
    with path_csv.open("w", newline="", encoding="utf-8") as out:
        writer = csv.DictWriter(out, fieldnames=["source", "target", "frequency"])
        writer.writeheader()
        writer.writerows(rows)

    summary = {
        "experiment": "EXP-01",
        "dataset": path.name,
        "dataset_sha256": hashlib.sha256(path.read_bytes()).hexdigest(),
        "python": sys.version.split()[0],
        "pm4py": pm4py.__version__,
        "pandas": pd.__version__,
        "events": int(len(df)),
        "cases": int(df["case_id"].nunique()),
        "activities": sorted(df["activity"].unique().tolist()),
        "dfg_edges": len(rows),
        "starts": {str(k): int(v) for k,v in start_activities.items()},
        "ends": {str(k): int(v) for k,v in end_activities.items()},
        "method": "pm4py.discover_dfg",
        "interpretation": "frequenza delle transizioni direttamente successive, non tempo di attesa",
    }
    path_json = RESULTS / "exp01_summary.json"
    path_json.write_text(json.dumps(summary, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    print(f"Dataset: {path.name} | Eventi: {len(df)} | Casi: {summary['cases']}")
    print(f"Python {summary['python']} | PM4Py {summary['pm4py']} | pandas {summary['pandas']}")
    print("DFG (frequenze):")
    for row in rows:
        print(f"  {row['source']} -> {row['target']}: {row['frequency']}")
    print(f"Inizi: {summary['starts']} | Fini: {summary['ends']}")
    print(f"Output: {path_csv} e {path_json}")


if __name__ == "__main__":
    main()
