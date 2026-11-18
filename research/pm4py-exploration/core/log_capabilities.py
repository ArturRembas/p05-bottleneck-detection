"""P05 - Profilazione preliminare degli event log.

Controlla la possibilità strutturale di calcolare
metriche. Non certifica la semantica dei timestamp.
"""

import pandas as pd

REQUIREMENTS = {
    "dfg": ["case_id", "activity", "timestamp"],
    "event_intervals": [
        "case_id", "activity", "timestamp"
    ],
    "service_time": [
        "case_id", "activity",
        "start_timestamp", "timestamp"
    ],
    "waiting_time": [
        "case_id", "activity",
        "queue_entry", "start_timestamp"
    ],
}

TEMPORAL_FIELDS = {
    "queue_entry", "start_timestamp", "timestamp"
}


def profile_event_log(df):
    if df.empty:
        raise ValueError("Event log vuoto")

    parsed = {}
    invalid = set()

    for col in df.columns:
        if col in TEMPORAL_FIELDS:
            parsed[col] = pd.to_datetime(
                df[col],
                format="ISO8601",
                utc=True,
                errors="coerce"
            )
            if parsed[col].isna().any():
                invalid.add(col)

        elif col in {"case_id", "activity"}:
            values = df[col].astype("string").str.strip()
            if not values.notna().all() or not values.ne("").all():
                invalid.add(col)

    capabilities = {}

    for metric, required in REQUIREMENTS.items():
        missing = [c for c in required if c not in df.columns]
        invalid_required = [c for c in required if c in invalid]

        reasons = []

        if missing:
            reasons.append(f"Colonne assenti: {missing}")

        if invalid_required:
            reasons.append(
                f"Valori mancanti o non validi: {invalid_required}"
            )

        if not reasons and metric == "service_time":
            if (
                parsed["start_timestamp"] >
                parsed["timestamp"]
            ).any():
                reasons.append("Fine precedente all'inizio")

        if not reasons and metric == "waiting_time":
            if (
                parsed["queue_entry"] >
                parsed["start_timestamp"]
            ).any():
                reasons.append(
                    "Inizio precedente all'ingresso in coda"
                )

        capabilities[metric] = {
            "structurally_possible": not bool(reasons),
            "reasons": reasons,
        }

    return {
        "events": len(df),
        "columns": list(df.columns),
        "capabilities": capabilities,
        "semantic_validation": "not_performed",
    }
