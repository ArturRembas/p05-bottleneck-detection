#!/usr/bin/env python3
"""EXP-02: Performance DFG (intervalli tra eventi) e controllo indipendente.

Da radice progetto: python scripts/exp02_performance_dfg.py
Argomento opzionale: percorso a un CSV con case_id, activity e timestamp.

ATTENZIONE: gli intervalli qui stimati non sono tempi di coda o processing time.
"""
from __future__ import annotations

import csv
import hashlib
import json
import math
from collections import defaultdict
from pathlib import Path
import statistics
import sys

import pandas as pd
import pm4py

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_INPUT = ROOT / "data" / "synthetic_manufacturing.csv"
RESULTS = ROOT / "results"

# Valori derivati manualmente dal dataset originale, in secondi.
# Utilizzati come regression test solo se l'hash del dataset non e' cambiato.
EXPECTED_MINUTES = {
    ("Taglio", "Fresatura"): 17.75,
    ("Fresatura", "Fresatura"): 42.0,
    ("Fresatura", "Saldatura"): 35.5,
    ("Saldatura", "Controllo"): 21.25,
}
EXPECTED_SHA256 = "ef401b927bb6347ffcc9697f1d2c878ed42b597792876d7f5d9135404c311c1d"


def load_data(path: Path) -> pd.DataFrame:
    if not path.is_file():
        raise FileNotFoundError(f"Dataset non trovato: {path}")
    df = pd.read_csv(path, dtype={"case_id": "string", "activity": "string"})
    required = {"case_id", "activity", "timestamp"}
    missing = required.difference(df.columns)
    if missing:
        raise ValueError(f"Mancano colonne obbligatorie: {sorted(missing)}")
    if df.empty or df[["case_id", "activity", "timestamp"]].isna().any().any():
        raise ValueError("Dataset vuoto o con campi obbligatori nulli")
    if (df["case_id"].str.strip() == "").any() or (df["activity"].str.strip() == "").any():
        raise ValueError("Case ID o attivita' vuoti")
    df["timestamp"] = pd.to_datetime(df["timestamp"], utc=True, errors="raise")
    return df.sort_values(["case_id", "timestamp"], kind="mergesort")


def manual_transition_durations(df: pd.DataFrame) -> dict[tuple[str, str], list[float]]:
    durations: dict[tuple[str, str], list[float]] = defaultdict(list)
    for _, case_events in df.groupby("case_id", sort=False):
        events = list(case_events[["activity", "timestamp"]].itertuples(index=False, name=None))
        for (activity_a, time_a), (activity_b, time_b) in zip(events, events[1:]):
            seconds = (time_b - time_a).total_seconds()
            if seconds < 0:
                raise ValueError("Intervallo negativo: verificare ordinamento e semantica dati")
            durations[(str(activity_a), str(activity_b))].append(float(seconds))
    return dict(durations)


def main() -> None:
    path = Path(sys.argv[1]).expanduser().resolve() if len(sys.argv) > 1 else DEFAULT_INPUT
    df = load_data(path)
    log = pm4py.format_dataframe(
        df, case_id="case_id", activity_key="activity", timestamp_key="timestamp"
    )
    performance, starts, ends = pm4py.discover_performance_dfg(
        log, perf_aggregation_key="mean"
    )
    manual = manual_transition_durations(df)
    if set(performance) != set(manual):
        raise AssertionError(
            f"Archi diversi tra PM4Py e controllo indipendente: "
            f"PM4Py={set(performance)}, manuale={set(manual)}"
        )

    rows = []
    for source, target in sorted(performance):
        values = manual[(source, target)]
        pm4py_mean_seconds = float(performance[(source, target)])
        manual_mean_seconds = statistics.mean(values)
        if not math.isclose(pm4py_mean_seconds, manual_mean_seconds, rel_tol=1e-9, abs_tol=1e-5):
            raise AssertionError(
                f"{source} -> {target}: PM4Py={pm4py_mean_seconds}s, "
                f"manuale={manual_mean_seconds}s"
            )
        rows.append({
            "source": source,
            "target": target,
            "occurrences": len(values),
            "pm4py_mean_seconds": round(pm4py_mean_seconds, 6),
            "pm4py_mean_minutes": round(pm4py_mean_seconds / 60, 6),
            "manual_mean_seconds": round(manual_mean_seconds, 6),
            "min_seconds": round(min(values), 6),
            "max_seconds": round(max(values), 6),
        })

    sha256 = hashlib.sha256(path.read_bytes()).hexdigest()
    regression = "not_applicable"
    if sha256 == EXPECTED_SHA256:
        actual = {(r["source"], r["target"]): r["pm4py_mean_minutes"] for r in rows}
        if actual != EXPECTED_MINUTES:
            raise AssertionError(f"Regression test non superato: {actual}")
        regression = "passed"

    RESULTS.mkdir(parents=True, exist_ok=True)
    output_csv = RESULTS / "exp02_performance_dfg.csv"
    with output_csv.open("w", newline="", encoding="utf-8") as out:
        writer = csv.DictWriter(out, fieldnames=list(rows[0]) if rows else [
            "source", "target", "occurrences", "pm4py_mean_seconds",
            "pm4py_mean_minutes", "manual_mean_seconds", "min_seconds", "max_seconds"
        ])
        writer.writeheader()
        writer.writerows(rows)

    output_json = RESULTS / "exp02_summary.json"
    summary = {
        "experiment": "EXP-02",
        "dataset": path.name,
        "dataset_sha256": sha256,
        "python": sys.version.split()[0],
        "pm4py": pm4py.__version__,
        "pandas": pd.__version__,
        "cases": int(df["case_id"].nunique()),
        "events": len(df),
        "method": "pm4py.discover_performance_dfg(perf_aggregation_key='mean')",
        "time_unit": "seconds (converted to minutes in CSV)",
        "metric_semantics": "mean elapsed time between consecutive event timestamps per DFG edge",
        "NOT_waiting_time": True,
        "manual_crosscheck": "passed",
        "default_dataset_regression": regression,
        "start_activities": {str(k): int(v) for k, v in starts.items()},
        "end_activities": {str(k): int(v) for k, v in ends.items()},
        "transitions": rows,
    }
    output_json.write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    print(f"Dataset: {path.name} | Eventi: {len(df)} | Casi: {summary['cases']}")
    print(f"Python {summary['python']} | PM4Py {summary['pm4py']} | Pandas {summary['pandas']}")
    print("Performance DFG: intervallo MEDIO fra timestamp consecutivi")
    for row in rows:
        print(f"  {row['source']} -> {row['target']}: "
              f"{row['pm4py_mean_minutes']:.2f} min (n={row['occurrences']})")
    print("Confronto indipendente PM4Py / pandas: OK")
    print(f"Regression test dataset originale: {regression}")
    print("ATTENZIONE: questi valori NON sono automaticamente tempi di attesa.")
    print(f"Output: {output_csv} e {output_json}")


if __name__ == "__main__":
    main()
