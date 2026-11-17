#!/usr/bin/env python3
"""P05 EXP-07 - Generalizzazione del rilevatore di code."""

from datetime import datetime, timedelta, timezone
from heapq import heapify, heappop, heappush
from pathlib import Path
import json
import math

import pandas as pd
import pm4py

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"
RESULTS = ROOT / "results"
DATA.mkdir(exist_ok=True)
RESULTS.mkdir(exist_ok=True)

BASE = datetime(2026, 10, 1, 8, tzinfo=timezone.utc)
N_CASES = 12
ARRIVAL_MIN = 7

# Queste configurazioni sono note soltanto al generatore.
SCENARIOS = {
    "A_cnc_critica": [
        ("Taglio", 4, 1),
        ("Fresatura CNC", 12, 1),
        ("Controllo", 3, 1),
    ],
    "B_taglio_critico": [
        ("Taglio", 12, 1),
        ("Fresatura CNC", 4, 1),
        ("Controllo", 3, 1),
    ],
    "C_lenta_senza_coda": [
        ("Taglio", 4, 1),
        ("Fresatura CNC", 20, 3),
        ("Controllo", 3, 1),
    ],
}

# Ground truth del benchmark, usata solo per la valutazione.
EXPECTED = {
    "A_cnc_critica": ["Fresatura CNC"],
    "B_taglio_critico": ["Taglio"],
    "C_lenta_senza_coda": [],
}


def generate(stations):
    pools = {}

    for name, duration, capacity in stations:
        machines = [
            (BASE, f"{name}-{i+1}")
            for i in range(capacity)
        ]
        heapify(machines)
        pools[name] = machines

    events = []

    for i in range(N_CASES):
        case_id = f"P{i+1:03d}"
        arrival = BASE + timedelta(minutes=i * ARRIVAL_MIN)

        for name, duration, capacity in stations:
            available, resource = heappop(pools[name])

            start = max(arrival, available)
            end = start + timedelta(minutes=duration)

            heappush(pools[name], (end, resource))

            events.append({
                "case_id": case_id,
                "activity": name,
                "queue_entry": arrival.isoformat(),
                "start_timestamp": start.isoformat(),
                "timestamp": end.isoformat(),
                "resource": resource,
            })

            arrival = end

    return pd.DataFrame(events)


def detect_queue_hotspots(raw):
    """Riceve solo dati degli eventi, senza configurazioni."""
    required = {
        "case_id", "activity", "queue_entry",
        "start_timestamp", "timestamp"
    }

    if not required.issubset(raw.columns):
        raise ValueError(
            f"Colonne mancanti: {required - set(raw.columns)}"
        )

    df = raw.copy()

    for col in ("queue_entry", "start_timestamp", "timestamp"):
        df[col] = pd.to_datetime(
            df[col], utc=True, errors="raise"
        )

    if df[list(("queue_entry", "start_timestamp", "timestamp"))].isna().any().any():
        raise ValueError("Timestamp mancanti")

    if not (
        (df["queue_entry"] <= df["start_timestamp"]) &
        (df["start_timestamp"] <= df["timestamp"])
    ).all():
        raise ValueError("Ordine temporale non valido")

    df["wait_min"] = (
        df["start_timestamp"] - df["queue_entry"]
    ).dt.total_seconds() / 60

    df["service_min"] = (
        df["timestamp"] - df["start_timestamp"]
    ).dt.total_seconds() / 60

    log = pm4py.format_dataframe(
        df,
        case_id="case_id",
        activity_key="activity",
        timestamp_key="timestamp",
        start_timestamp_key="start_timestamp",
    )

    pm_service = pm4py.get_service_time(
        log,
        aggregation_measure="mean",
        start_timestamp_key="start_timestamp",
    )

    metrics = []

    for activity, group in df.groupby("activity"):
        service = float(group["service_min"].mean())
        pm_value = float(pm_service[activity]) / 60

        assert math.isclose(
            service, pm_value, abs_tol=1e-6
        ), "Service time PM4Py/Pandas differente"

        metrics.append({
            "activity": activity,
            "observations": len(group),
            "mean_wait_min": float(group["wait_min"].mean()),
            "max_wait_min": float(group["wait_min"].max()),
            "waiting_pct": float(
                100 * (group["wait_min"] > 0).mean()
            ),
            "service_min": pm_value,
        })

    # Euristica indipendente dal nome dell'attività.
    # Rileva congestioni osservate, non cause dimostrate.
    candidates = [
        m for m in metrics
        if m["mean_wait_min"] > 1e-9
    ]

    candidates.sort(
        key=lambda m: -m["mean_wait_min"]
    )

    return metrics, [m["activity"] for m in candidates]


def main():
    print("=" * 60)
    print("P05 - EXP-07: Generalizzazione rilevatore")
    print("=" * 60)
    print("PM4Py:", pm4py.__version__)

    results = {}
    correct = 0

    for name, configuration in SCENARIOS.items():
        generated = generate(configuration)

        path = DATA / f"exp07_{name}.csv"
        generated.to_csv(path, index=False)

        # Il rilevatore legge il CSV: nessuna informazione
        # sulle capacità gli viene passata.
        log = pd.read_csv(path)

        metrics, detected = detect_queue_hotspots(log)
        expected = EXPECTED[name]

        passed = detected == expected
        correct += int(passed)

        print(f"\nSCENARIO {name}")

        for m in metrics:
            print(
                f"  {m['activity']}: "
                f"attesa={m['mean_wait_min']:.2f} min; "
                f"lavorazione={m['service_min']:.2f} min; "
                f"casi in attesa={m['waiting_pct']:.1f}%"
            )

        print("  Atteso:", expected or "nessuna criticità")
        print("  Rilevato:", detected or "nessuna criticità")
        print("  Esito:", "PASS" if passed else "FAIL")

        results[name] = {
            "expected": expected,
            "detected": detected,
            "passed": passed,
            "metrics": metrics,
        }

    # Test negativo: dati insufficienti.
    invalid = generate(SCENARIOS["A_cnc_critica"])
    invalid = invalid.drop(columns=["queue_entry"])

    try:
        detect_queue_hotspots(invalid)
        raise AssertionError("Mancata validazione dello schema")
    except ValueError:
        print("\nTest colonne mancanti: PASS")

    summary = {
        "experiment": "EXP-07",
        "pm4py_version": pm4py.__version__,
        "cases_per_scenario": N_CASES,
        "correct_scenarios": correct,
        "total_scenarios": len(SCENARIOS),
        "results": results,
    }

    output = RESULTS / "exp07_summary.json"
    output.write_text(
        json.dumps(summary, indent=2, ensure_ascii=False),
        encoding="utf-8"
    )

    print(
        f"\nScenari corretti: {correct}/{len(SCENARIOS)}"
    )
    print("Risultati:", output)

    assert correct == len(SCENARIOS), (
        "Uno o più scenari non hanno superato la verifica"
    )

    print("EXP-07: PASSED")


if __name__ == "__main__":
    main()
