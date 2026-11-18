"""P05 - Analisi sperimentale della dinamica delle code.

Questo modulo non conosce gli scenari di test e non
contiene nomi di attività o capacità preconfigurate.

Le classificazioni descrivono soltanto il periodo
osservato. Non sono diagnosi causali di bottleneck.
"""

import pandas as pd

MIN_OBSERVATIONS = 6
TAIL_WINDOW = 3
GROWTH_THRESHOLD = 0.70
EPS = 1e-9

REQUIRED = {
    "case_id",
    "activity",
    "queue_entry",
    "start_timestamp",
    "timestamp",
}


def analyze_queue_dynamics(raw):
    """Restituisce metriche e andamento delle code per attività."""

    missing = REQUIRED - set(raw.columns)
    if missing:
        raise ValueError(f"Colonne mancanti: {sorted(missing)}")

    if raw.empty:
        raise ValueError("Event log vuoto")

    df = raw.copy()

    for col in ("queue_entry", "start_timestamp", "timestamp"):
        df[col] = pd.to_datetime(
            df[col], utc=True, errors="raise"
        )

    if df[list(("queue_entry", "start_timestamp", "timestamp"))].isna().any().any():
        raise ValueError("Timestamp mancanti")

    valid_order = (
        (df["queue_entry"] <= df["start_timestamp"]) &
        (df["start_timestamp"] <= df["timestamp"])
    )

    if not valid_order.all():
        raise ValueError("Sequenza temporale non valida")

    df["wait_min"] = (
        df["start_timestamp"] - df["queue_entry"]
    ).dt.total_seconds() / 60

    results = []

    for activity, group in df.groupby("activity", sort=True):
        group = group.sort_values(
            ["queue_entry", "case_id"],
            kind="stable"
        )

        waits = group["wait_min"].tolist()
        n = len(waits)

        positive_steps = sum(
            waits[i] > waits[i - 1] + EPS
            for i in range(1, n)
        )

        growth_fraction = (
            positive_steps / (n - 1) if n > 1 else 0.0
        )

        tail = waits[-TAIL_WINDOW:]

        if n < MIN_OBSERVATIONS:
            classification = "inconclusive"

        elif all(w <= EPS for w in waits):
            classification = "no_observed_queue"

        elif all(w <= EPS for w in tail):
            classification = "recovered_queue"

        elif (
            growth_fraction >= GROWTH_THRESHOLD
            and waits[-1] > waits[0] + EPS
        ):
            classification = "growing_queue"

        else:
            classification = "inconclusive"

        results.append({
            "activity": str(activity),
            "observations": n,
            "mean_wait_min": float(sum(waits) / n),
            "max_wait_min": float(max(waits)),
            "waiting_pct": float(
                100 * sum(w > EPS for w in waits) / n
            ),
            "growth_fraction": float(growth_fraction),
            "classification": classification,
        })

    return results
