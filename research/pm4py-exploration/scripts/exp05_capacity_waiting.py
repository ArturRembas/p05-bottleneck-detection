#!/usr/bin/env python3
"""P05 EXP-05 - Capacità, attesa e service time."""

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

BASE = datetime(2026, 10, 1, 8, 0, tzinfo=timezone.utc)
N_PIECES = 8
ARRIVAL_MIN = 7
SERVICE_MIN = 12


def generate(capacity):
    """Scheduler FIFO deterministico con macchine identiche."""
    machines = [
        (BASE, f"CNC-{i+1}")
        for i in range(capacity)
    ]
    heapify(machines)

    cases = []
    events = []

    for i in range(N_PIECES):
        case_id = f"P{i+1:03d}"
        arrival = BASE + timedelta(minutes=ARRIVAL_MIN * i)

        available, machine = heappop(machines)
        start = max(arrival, available)
        end = start + timedelta(minutes=SERVICE_MIN)
        heappush(machines, (end, machine))

        wait = (start - arrival).total_seconds() / 60

        cases.append({
            "case_id": case_id,
            "machine": machine,
            "arrival": arrival.isoformat(),
            "start": start.isoformat(),
            "complete": end.isoformat(),
            "wait_min": wait,
            "service_min": SERVICE_MIN
        })

        # Evento di ingresso in coda
        events.append({
            "case_id": case_id,
            "activity": "Ingresso coda CNC",
            "start_timestamp": arrival.isoformat(),
            "timestamp": arrival.isoformat()
        })

        # Intervallo reale di lavorazione
        events.append({
            "case_id": case_id,
            "activity": "Lavorazione CNC",
            "start_timestamp": start.isoformat(),
            "timestamp": end.isoformat()
        })

    return pd.DataFrame(cases), pd.DataFrame(events)


def analyze(capacity):
    cases, events = generate(capacity)

    label = f"{capacity}cnc"
    cases.to_csv(DATA / f"exp05_cases_{label}.csv", index=False)
    events.to_csv(DATA / f"exp05_events_{label}.csv", index=False)

    # Converte esplicitamente i timestamp.
    for col in ("start_timestamp", "timestamp"):
        events[col] = pd.to_datetime(events[col], utc=True)

    # Event log compatibile con PM4Py.
    log = pm4py.format_dataframe(
        events,
        case_id="case_id",
        activity_key="activity",
        timestamp_key="timestamp",
        start_timestamp_key="start_timestamp"
    )

    service = pm4py.get_service_time(
        log,
        aggregation_measure="mean",
        start_timestamp_key="start_timestamp"
    )

    # PM4Py restituisce il valore in secondi.
    pm_service_min = float(service["Lavorazione CNC"]) / 60

    # Validazione indipendente della durata.
    work_events = events[
        events["activity"] == "Lavorazione CNC"
    ]

    independent_service = (
        work_events["timestamp"] -
        work_events["start_timestamp"]
    ).dt.total_seconds().mean() / 60

    assert math.isclose(
        pm_service_min, independent_service,
        abs_tol=1e-6
    )
    assert math.isclose(pm_service_min, SERVICE_MIN)

    mean_wait = float(cases["wait_min"].mean())
    max_wait = float(cases["wait_min"].max())

    start_time = pd.to_datetime(cases["arrival"]).min()
    end_time = pd.to_datetime(cases["complete"]).max()
    makespan = (end_time - start_time).total_seconds() / 60

    throughput = N_PIECES / (makespan / 60)

    # Valori attesi calcolati indipendentemente.
    expected = {
        1: {"wait": 17.5, "max_wait": 35.0, "makespan": 96.0},
        2: {"wait": 0.0, "max_wait": 0.0, "makespan": 61.0}
    }[capacity]

    assert math.isclose(mean_wait, expected["wait"])
    assert math.isclose(max_wait, expected["max_wait"])
    assert math.isclose(makespan, expected["makespan"])

    print(f"\nSCENARIO {capacity} CNC")
    print(f"  Attesa media: {mean_wait:.2f} min")
    print(f"  Attesa massima: {max_wait:.2f} min")
    print(f"  Service time PM4Py: {pm_service_min:.2f} min")
    print(f"  Durata osservazione: {makespan:.2f} min")
    print(f"  Throughput osservato: {throughput:.2f} pezzi/ora")
    print("  Validazione PM4Py/Pandas: OK")
    print("  Test di regressione: PASSED")

    return {
        "capacity": capacity,
        "cases": N_PIECES,
        "mean_wait_min": mean_wait,
        "max_wait_min": max_wait,
        "mean_service_min": pm_service_min,
        "makespan_min": makespan,
        "observed_throughput_per_hour": throughput,
        "tests": "passed"
    }


def main():
    print("=" * 60)
    print("P05 - EXP-05: Capacità e tempi di attesa")
    print("=" * 60)
    print("PM4Py:", pm4py.__version__)

    results = [analyze(1), analyze(2)]

    assert results[1]["mean_wait_min"] < results[0]["mean_wait_min"]
    assert (
        results[1]["observed_throughput_per_hour"] >
        results[0]["observed_throughput_per_hour"]
    )

    output = {
        "experiment": "EXP-05",
        "pm4py_version": pm4py.__version__,
        "arrival_interval_min": ARRIVAL_MIN,
        "service_duration_min": SERVICE_MIN,
        "scenarios": results
    }

    path = RESULTS / "exp05_summary.json"
    path.write_text(
        json.dumps(output, indent=2, ensure_ascii=False),
        encoding="utf-8"
    )

    print("\nConfronto scenari: PASSED")
    print("Output:", path)


if __name__ == "__main__":
    main()
