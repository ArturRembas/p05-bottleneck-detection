#!/usr/bin/env python3
"""P05 EXP-08 - Code transitorie e persistenti."""

from datetime import datetime, timedelta, timezone
from pathlib import Path
import json
import math

import pandas as pd

# Riutilizziamo il rilevatore reale di EXP-07.
from exp07_generalization import detect_queue_hotspots

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"
RESULTS = ROOT / "results"

DATA.mkdir(exist_ok=True)
RESULTS.mkdir(exist_ok=True)

BASE = datetime(2026, 10, 1, 8, tzinfo=timezone.utc)

SCENARIOS = {
    "A_regolare": {
        "arrivals": [0, 15, 30, 45, 60, 75, 90, 105],
        "service": 10,
        "expected_waits": [0] * 8,
    },
    "B_picco_temporaneo": {
        "arrivals": [0, 1, 2, 30, 45, 60, 75, 90],
        "service": 10,
        "expected_waits": [0, 9, 18, 0, 0, 0, 0, 0],
    },
    "C_sovraccarico": {
        "arrivals": [0, 7, 14, 21, 28, 35, 42, 49],
        "service": 12,
        "expected_waits": [0, 5, 10, 15, 20, 25, 30, 35],
    },
}


def generate(config):
    rows = []
    next_free = BASE

    for i, minute in enumerate(config["arrivals"]):
        arrival = BASE + timedelta(minutes=minute)
        start = max(arrival, next_free)
        end = start + timedelta(minutes=config["service"])
        next_free = end

        rows.append({
            "case_id": f"P{i+1:03d}",
            "activity": "Fresatura CNC",
            "queue_entry": arrival.isoformat(),
            "start_timestamp": start.isoformat(),
            "timestamp": end.isoformat(),
            "resource": "CNC-1",
        })

    return pd.DataFrame(rows)


def main():
    summary = {}

    print("=" * 60)
    print("P05 - EXP-08: Code transitorie e persistenti")
    print("=" * 60)

    for name, config in SCENARIOS.items():
        df = generate(config)
        path = DATA / f"exp08_{name}.csv"
        df.to_csv(path, index=False)

        # Il rilevatore riceve il log, non lo scenario.
        metrics, detected = detect_queue_hotspots(
            pd.read_csv(path)
        )

        arrivals = pd.to_datetime(df["queue_entry"], utc=True)
        starts = pd.to_datetime(
            df["start_timestamp"], utc=True
        )

        waits = (
            (starts - arrivals).dt.total_seconds() / 60
        ).tolist()

        expected = config["expected_waits"]

        assert waits == expected, (
            f"Tempi attesa inattesi per {name}"
        )

        expected_detection = (
            [] if not any(expected) else ["Fresatura CNC"]
        )

        assert detected == expected_detection

        mean_wait = sum(waits) / len(waits)
        first_half = sum(waits[:4]) / 4
        second_half = sum(waits[4:]) / 4

        assert math.isclose(
            mean_wait,
            sum(expected) / len(expected),
            abs_tol=1e-9
        )

        print(f"\n{name}")
        print("  Attese per pezzo:", waits)
        print(f"  Attesa media: {mean_wait:.3f} min")
        print(f"  Prima metà: {first_half:.3f} min")
        print(f"  Seconda metà: {second_half:.3f} min")
        print("  Hotspot rilevato:", bool(detected))
        print("  Test: PASS")

        summary[name] = {
            "waits_min": waits,
            "mean_wait_min": mean_wait,
            "first_half_mean_min": first_half,
            "second_half_mean_min": second_half,
            "hotspot_detected": bool(detected),
            "metrics": metrics,
        }

    # Controlli sul comportamento dei due scenari.
    burst = summary["B_picco_temporaneo"]
    overload = summary["C_sovraccarico"]

    assert burst["hotspot_detected"]
    assert burst["second_half_mean_min"] == 0
    assert overload["hotspot_detected"]
    assert (
        overload["second_half_mean_min"] >
        overload["first_half_mean_min"]
    )

    output = RESULTS / "exp08_summary.json"
    output.write_text(
        json.dumps(summary, indent=2, ensure_ascii=False),
        encoding="utf-8"
    )

    print("\nValidazione EXP-08: PASSED")
    print("Output:", output)


if __name__ == "__main__":
    main()
