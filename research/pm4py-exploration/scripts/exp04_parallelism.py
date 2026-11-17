#!/usr/bin/env python3
"""P05 EXP-04 - Process discovery e parallelismo."""

from pathlib import Path
from collections import Counter
import json
from datetime import datetime, timedelta, timezone

import pandas as pd
import pm4py
from pm4py.objects.process_tree.obj import Operator

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"
RESULTS = ROOT / "results"
DATA.mkdir(exist_ok=True)
RESULTS.mkdir(exist_ok=True)

A = "Controllo materiali"
B = "Setup macchina"

# Generazione di un log controllato con due ordini.
rows = []

for i in range(8):
    case_id = f"PAR{i+1:03d}"
    middle = [A, B] if i % 2 == 0 else [B, A]
    activities = ["Ordine", *middle, "Assemblaggio"]

    start = datetime(
        2026, 10, 1, 8, 0,
        tzinfo=timezone.utc
    ) + timedelta(hours=i)

    for j, activity in enumerate(activities):
        rows.append({
            "case_id": case_id,
            "activity": activity,
            "timestamp": (
                start + timedelta(minutes=10*j)
            ).isoformat()
        })

df = pd.DataFrame(rows)
dataset = DATA / "synthetic_parallel.csv"
df.to_csv(dataset, index=False)

log = pm4py.format_dataframe(
    df,
    case_id="case_id",
    activity_key="activity",
    timestamp_key="timestamp"
)

# DFG: verifica dei due ordini osservati.
dfg, starts, ends = pm4py.discover_dfg(log)

assert dfg.get((A, B)) == 4
assert dfg.get((B, A)) == 4

# Process tree mediante Inductive Miner.
tree = pm4py.discover_process_tree_inductive(log)

def contains_parallel(node):
    if node.operator == Operator.PARALLEL:
        return True
    return any(
        contains_parallel(child)
        for child in node.children
    )

parallel_detected = contains_parallel(tree)

# Controllo: osserviamo soltanto un ordine.
control_df = df[
    df["case_id"].isin(
        [f"PAR{i:03d}" for i in (1, 3, 5, 7)]
    )
].copy()

control_log = pm4py.format_dataframe(
    control_df,
    case_id="case_id",
    activity_key="activity",
    timestamp_key="timestamp"
)

control_tree = pm4py.discover_process_tree_inductive(
    control_log
)
control_parallel = contains_parallel(control_tree)

# Esportazione dei modelli.
pm4py.write_ptml(
    tree, str(RESULTS / "exp04_process_tree.ptml")
)

net, initial, final = pm4py.discover_petri_net_inductive(log)
pm4py.write_pnml(
    net, initial, final,
    str(RESULTS / "exp04_petri_net.pnml")
)

# Visualizzazione SVG (Graphviz richiesto).
try:
    pm4py.save_vis_process_tree(
        tree,
        str(RESULTS / "exp04_process_tree.svg")
    )
    svg_status = "created"
except Exception as exc:
    svg_status = f"unavailable: {exc}"

summary = {
    "experiment": "EXP-04",
    "dataset": dataset.name,
    "cases": 8,
    "events": len(df),
    "pm4py_version": pm4py.__version__,
    "dfg_A_to_B": dfg.get((A, B), 0),
    "dfg_B_to_A": dfg.get((B, A), 0),
    "process_tree": str(tree),
    "parallel_operator_detected": parallel_detected,
    "control_parallel_detected": control_parallel,
    "svg_status": svg_status
}

(RESULTS / "exp04_summary.json").write_text(
    json.dumps(summary, indent=2, ensure_ascii=False),
    encoding="utf-8"
)

print("=" * 60)
print("P05 - EXP-04: Parallelismo")
print("=" * 60)
print(f"Eventi: {len(df)} | Casi: 8")
print(f"{A} -> {B}: {dfg.get((A, B), 0)}")
print(f"{B} -> {A}: {dfg.get((B, A), 0)}")
print(f"\nProcess Tree:\n{tree}")
print(f"\nOperatore AND rilevato: {parallel_detected}")
print(f"AND nel controllo sequenziale: {control_parallel}")
print(f"Visualizzazione SVG: {svg_status}")

assert parallel_detected, (
    "Il modello non ha riconosciuto il parallelismo atteso"
)
assert not control_parallel, (
    "Parallelismo inatteso nel controllo sequenziale"
)

print("\nVerifiche EXP-04: PASSED")
print(f"Risultati salvati in: {RESULTS}")
