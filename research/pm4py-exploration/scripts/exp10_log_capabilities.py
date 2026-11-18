#!/usr/bin/env python3
"""P05 EXP-10 - Capacità analitiche dei log."""

from pathlib import Path
import sys
import json

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from core.log_capabilities import profile_event_log

DATA = ROOT / "data"
RESULTS = ROOT / "results"

complete = pd.read_csv(
    DATA / "exp08_C_sovraccarico.csv"
)

minimal = pd.read_csv(
    DATA / "synthetic_manufacturing.csv"
)

invalid = complete.copy()
invalid.loc[0, "timestamp"] = "data_non_valida"

scenarios = {
    "completo": (
        complete,
        {"dfg": True, "event_intervals": True,
         "service_time": True, "waiting_time": True}
    ),
    "minimo": (
        minimal,
        {"dfg": True, "event_intervals": True,
         "service_time": False, "waiting_time": False}
    ),
    "senza_ingresso_coda": (
        complete.drop(columns=["queue_entry"]),
        {"dfg": True, "event_intervals": True,
         "service_time": True, "waiting_time": False}
    ),
    "senza_inizio": (
        complete.drop(columns=["start_timestamp"]),
        {"dfg": True, "event_intervals": True,
         "service_time": False, "waiting_time": False}
    ),
    "timestamp_non_valido": (
        invalid,
        {"dfg": False, "event_intervals": False,
         "service_time": False, "waiting_time": True}
    ),
}

results = {}

print("=" * 60)
print("P05 - EXP-10: Profilazione event log")
print("=" * 60)

for name, (df, expected) in scenarios.items():
    result = profile_event_log(df)

    obtained = {
        key: value["structurally_possible"]
        for key, value in result["capabilities"].items()
    }

    assert obtained == expected, (
        f"{name}: atteso {expected}, ottenuto {obtained}"
    )

    print(f"\n{name}")
    for metric, possible in obtained.items():
        print(
            f"  {metric}: "
            f"{'POSSIBILE' if possible else 'NON DISPONIBILE'}"
        )

    print("  Test: PASS")
    results[name] = result

RESULTS.mkdir(exist_ok=True)

output = RESULTS / "exp10_summary.json"
output.write_text(
    json.dumps(results, indent=2, ensure_ascii=False),
    encoding="utf-8"
)

print("\nEXP-10: PASSED")
print("Output:", output)
