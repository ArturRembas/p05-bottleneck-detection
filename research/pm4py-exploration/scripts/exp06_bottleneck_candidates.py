#!/usr/bin/env python3
"""P05 EXP-06: prima identificazione di criticita' da event log."""

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

STATIONS = [
    ("Taglio", 4),
    ("Fresatura CNC", 12),
    ("Controllo", 3),
]

N_CASES = 8
ARRIVAL_MIN = 7


def generate_log(cnc_capacity):
    """Genera un processo seriale con code FIFO per stazione."""
    pools = {}

    for name, duration in STATIONS:
        capacity = cnc_capacity if name == "Fresatura CNC" else 1
        pool = [
            (BASE, f"{name}-{i+1}")
            for i in range(capacity)
        ]
        heapify(pool)
        pools[name] = pool

    rows = []

    for i in range(N_CASES):
        case_id = f"P{i+1:03d}"
        arrival = BASE + timedelta(minutes=i * ARRIVAL_MIN)

        for name, duration in STATIONS:
            available, resource = heappop(pools[name])
            start = max(arrival, available)
            end = start + timedelta(minutes=duration)

            heappush(pools[name], (end, resource))

            rows.append({
                "case_id": case_id,
                "activity": name,
                "queue_entry": arrival.isoformat(),
                "start_timestamp": start.isoformat(),
                "timestamp": end.isoformat(),
                "resource": resource,
            })

            arrival = end

    return pd.DataFrame(rows)


def analyze_event_log(raw):
    """Analizza soltanto i dati del log, senza conoscere le capacità."""
    df = raw.copy()

    for col in ("queue_entry", "start_timestamp", "timestamp"):
        df[col] = pd.to_datetime(df[col], utc=True, errors="raise")

    df["wait_min"] = (
        df["start_timestamp"] - df["queue_entry"]
    ).dt.total_seconds() / 60

    df["service_min"] = (
        df["timestamp"] - df["start_timestamp"]
    ).dt.total_seconds() / 60

    assert (df["wait_min"] >= 0).all()
    assert (df["service_min"] >= 0).all()

    log = pm4py.format_dataframe(
        df,
        case_id="case_id",
        activity_key="activity",
        timestamp_key="timestamp",
        start_timestamp_key="start_timestamp",
    )

    service_pm4py = pm4py.get_service_time(
        log,
        aggregation_measure="mean",
        start_timestamp_key="start_timestamp",
    )

    dfg, _, _ = pm4py.discover_dfg(log)

    assert dfg[("Taglio", "Fresatura CNC")] == N_CASES
    assert dfg[("Fresatura CNC", "Controllo")] == N_CASES

    metrics = []

    for activity, group in df.groupby("activity"):
        mean_service = float(group["service_min"].mean())
        pm_service = float(service_pm4py[activity]) / 60

        assert math.isclose(
            mean_service, pm_service, abs_tol=1e-6
        )

        metrics.append({
            "activity": activity,
            "observations": int(len(group)),
            "mean_wait_min": float(group["wait_min"].mean()),
            "max_wait_min": float(group["wait_min"].max()),
            "cases_waiting_pct": float(
                100 * (group["wait_min"] > 0).mean()
            ),
            "mean_service_min": pm_service,
        })

    # Prima euristica: individua le attività con attesa osservata.
    # Non equivale a una diagnosi causale definitiva.
    candidates = sorted(
        [m for m in metrics if m["mean_wait_min"] > 0],
        key=lambda m: -m["mean_wait_min"],
    )

    return metrics, candidates


def run_scenario(capacity):
    raw = generate_log(capacity)
    label = f"{capacity}cnc"

    raw.to_csv(
        DATA / f"exp06_events_{label}.csv",
        index=False
    )

    metrics, candidates = analyze_event_log(raw)

    print(f"\nSCENARIO: {capacity} CNC")

    for m in sorted(metrics, key=lambda x: x["activity"]):
        print(
            f"  {m['activity']}: "
            f"attesa={m['mean_wait_min']:.2f} min, "
            f"casi in attesa={m['cases_waiting_pct']:.1f}%, "
            f"lavorazione={m['mean_service_min']:.2f} min"
        )

    names = [m["activity"] for m in candidates]
    print("  Criticità candidate:", names or "nessuna")

    return {
        "capacity_configuration": capacity,
        "metrics": metrics,
        "candidates": names,
    }


def main():
    print("=" * 60)
    print("P05 - EXP-06: Bottleneck candidate detection")
    print("=" * 60)
    print("PM4Py:", pm4py.__version__)

    baseline = run_scenario(1)
    intervention = run_scenario(2)

    # Validazione contro lo scenario sintetico noto.
    assert baseline["candidates"] == ["Fresatura CNC"]
    assert intervention["candidates"] == []

    base_metrics = {
        m["activity"]: m for m in baseline["metrics"]
    }
    new_metrics = {
        m["activity"]: m for m in intervention["metrics"]
    }

    assert math.isclose(
        base_metrics["Fresatura CNC"]["mean_wait_min"], 17.5
    )
    assert math.isclose(
        base_metrics["Fresatura CNC"]["cases_waiting_pct"], 87.5
    )
    assert math.isclose(
        new_metrics["Fresatura CNC"]["mean_wait_min"], 0
    )

    summary = {
        "experiment": "EXP-06",
        "pm4py_version": pm4py.__version__,
        "baseline": baseline,
        "intervention": intervention,
        "regression_test": "passed",
    }

    output = RESULTS / "exp06_summary.json"
    output.write_text(
        json.dumps(summary, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )

    print("\nValidazione scenario noto: PASSED")
    print("Output:", output)


if __name__ == "__main__":
    main()
