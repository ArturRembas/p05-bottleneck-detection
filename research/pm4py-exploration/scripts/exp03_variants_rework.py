#!/usr/bin/env python3
"""
P05 - EXP-03: Varianti e attività ripetute
PM4Py Exploration

Obiettivi:
- Identificare le varianti del processo
- Individuare attività ripetute nello stesso caso
- Confrontare PM4Py con un calcolo indipendente Pandas
- Verificare i risultati attesi sul dataset sintetico
"""

from collections import Counter
from numbers import Integral
from pathlib import Path
import json
import platform

import pandas as pd
import pm4py


ROOT = Path(__file__).resolve().parents[1]
DATASET = ROOT / "data" / "synthetic_manufacturing.csv"
RESULTS = ROOT / "results"
RESULTS.mkdir(exist_ok=True)


def main():
    print("=" * 60)
    print("P05 - EXP-03: Varianti e attività ripetute")
    print("=" * 60)

    # 1. Caricamento e preparazione
    df = pd.read_csv(
        DATASET,
        dtype={"case_id": str, "activity": str}
    )

    df["timestamp"] = pd.to_datetime(
        df["timestamp"], utc=True, errors="raise"
    )

    log = pm4py.format_dataframe(
        df,
        case_id="case_id",
        activity_key="activity",
        timestamp_key="timestamp"
    )

    n_cases = df["case_id"].nunique()

    print(f"\nDataset: {DATASET.name}")
    print(f"Eventi: {len(df)} | Casi: {n_cases}")
    print(f"Python: {platform.python_version()}")
    print(f"PM4Py: {pm4py.__version__}")
    print(f"Pandas: {pd.__version__}")

    # 2. Varianti con PM4Py
    raw_variants = pm4py.get_variants_as_tuples(log)

    variants = Counter({
        tuple(key): (
            int(value)
            if isinstance(value, Integral)
            else len(value)
        )
        for key, value in raw_variants.items()
    })

    # 3. Verifica indipendente con Pandas
    ordered = (
        df.assign(_row=range(len(df)))
        .sort_values(
            ["case_id", "timestamp", "_row"],
            kind="stable"
        )
    )

    case_sequences = (
        ordered.groupby("case_id")["activity"]
        .agg(tuple)
    )

    independent_variants = Counter(case_sequences.tolist())

    assert variants == independent_variants, (
        "ERRORE: varianti PM4Py e Pandas differenti"
    )

    # 4. Analisi attività ripetute con PM4Py
    pm_rework = {
        str(activity): int(count)
        for activity, count in
        pm4py.get_rework_cases_per_activity(log).items()
    }

    # 5. Verifica indipendente delle ripetizioni
    repetitions = (
        ordered.groupby(["case_id", "activity"])
        .size()
        .reset_index(name="occurrences")
    )

    repetitions = repetitions[
        repetitions["occurrences"] > 1
    ].copy()

    repetitions["extra_occurrences"] = (
        repetitions["occurrences"] - 1
    )

    independent_rework = {
        str(activity): int(count)
        for activity, count in
        repetitions.groupby("activity")["case_id"].nunique().items()
    }

    assert pm_rework == independent_rework, (
        "ERRORE: ripetizioni PM4Py e Pandas differenti"
    )

    # 6. Test di regressione sul dataset originale
    expected_variants = Counter({
        ("Taglio", "Fresatura", "Saldatura", "Controllo"): 3,
        (
            "Taglio", "Fresatura", "Fresatura",
            "Saldatura", "Controllo"
        ): 1
    })

    assert len(df) == 17
    assert n_cases == 4
    assert variants == expected_variants
    assert pm_rework == {"Fresatura": 1}
    assert set(repetitions["case_id"]) == {"P004"}

    # 7. Risultati
    variant_rows = []

    print("\nVARIANTI DEL PROCESSO")
    for sequence, count in sorted(
        variants.items(),
        key=lambda item: (-item[1], item[0])
    ):
        percentage = 100 * count / n_cases
        description = " -> ".join(sequence)

        print(
            f"  {description}: "
            f"{count} casi ({percentage:.1f}%)"
        )

        variant_rows.append({
            "variant": description,
            "cases": count,
            "percentage": round(percentage, 2)
        })

    print("\nATTIVITA' RIPETUTE")
    if pm_rework:
        for activity, count in sorted(pm_rework.items()):
            print(f"  {activity}: {count} casi")
    else:
        print("  Nessuna ripetizione rilevata")

    for _, row in repetitions.iterrows():
        print(
            f"  Caso {row['case_id']}: "
            f"{row['activity']} eseguita "
            f"{row['occurrences']} volte"
        )

    # 8. Esportazione
    pd.DataFrame(variant_rows).to_csv(
        RESULTS / "exp03_variants.csv",
        index=False
    )

    repetitions.to_csv(
        RESULTS / "exp03_case_repetitions.csv",
        index=False
    )

    summary = {
        "experiment": "EXP-03",
        "dataset": DATASET.name,
        "events": len(df),
        "cases": n_cases,
        "python_version": platform.python_version(),
        "pm4py_version": pm4py.__version__,
        "pandas_version": pd.__version__,
        "variants": variant_rows,
        "repeated_activities": pm_rework,
        "independent_check": "passed",
        "regression_test": "passed",
        "interpretation_limit": (
            "Una ripetizione non dimostra automaticamente "
            "una rilavorazione dovuta a un difetto."
        )
    }

    with open(
        RESULTS / "exp03_summary.json",
        "w",
        encoding="utf-8"
    ) as f:
        json.dump(
            summary,
            f,
            indent=2,
            ensure_ascii=False
        )

    print("\nConfronto indipendente PM4Py/Pandas: OK")
    print("Regression test dataset originale: passed")
    print(
        "ATTENZIONE: ripetizione osservata non equivale "
        "automaticamente a rilavorazione."
    )
    print(f"Output salvati in: {RESULTS}")


if __name__ == "__main__":
    main()
