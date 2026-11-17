#!/usr/bin/env python3
"""P05 EXP-09 - Validazione modulo dinamica delle code."""

from pathlib import Path
import sys
import json

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from core.queue_diagnostics import analyze_queue_dynamics

DATA = ROOT / "data"
RESULTS = ROOT / "results"

EXPECTED = {
    "A_regolare": "no_observed_queue",
    "B_picco_temporaneo": "recovered_queue",
    "C_sovraccarico": "growing_queue",
}


def main():
    print("=" * 60)
    print("P05 - EXP-09: Dinamica delle code")
    print("=" * 60)

    results = {}

    for scenario, expected in EXPECTED.items():
        path = DATA / f"exp08_{scenario}.csv"

        df = pd.read_csv(path)
        analysis = analyze_queue_dynamics(df)

        assert len(analysis) == 1

        result = analysis[0]
        detected = result["classification"]

        print(f"\nSCENARIO {scenario}")
        print("  Attesa media:", round(result["mean_wait_min"], 3))
        print("  Percentuale in attesa:", round(result["waiting_pct"], 1))
        print("  Frazione di incrementi:", round(result["growth_fraction"], 3))
        print("  Atteso:", expected)
        print("  Rilevato:", detected)

        assert detected == expected, (
            f"Classificazione errata: {scenario}"
        )

        print("  Test: PASS")
        results[scenario] = result

    # Campione troncato: non abbiamo ancora osservazioni
    # sufficienti per interpretare il comportamento.
    incomplete = pd.read_csv(
        DATA / "exp08_C_sovraccarico.csv"
    ).head(3)

    incomplete_result = analyze_queue_dynamics(incomplete)[0]

    assert (
        incomplete_result["classification"] == "inconclusive"
    )

    print("\nControllo campione insufficiente: PASS")

    # Schema non valido.
    invalid = incomplete.drop(columns=["queue_entry"])

    try:
        analyze_queue_dynamics(invalid)
    except ValueError:
        print("Controllo colonne mancanti: PASS")
    else:
        raise AssertionError("Schema invalido accettato")

    output = {
        "experiment": "EXP-09",
        "results": results,
        "incomplete_sample": incomplete_result,
        "status": "passed",
    }

    RESULTS.mkdir(exist_ok=True)

    path = RESULTS / "exp09_summary.json"
    path.write_text(
        json.dumps(output, indent=2, ensure_ascii=False),
        encoding="utf-8"
    )

    print("\nEXP-09: PASSED")
    print("Output:", path)


if __name__ == "__main__":
    main()
