# P05 — EXP-02: Risultati verificati

Stato: VERIFICATO
Ambiente: Ubuntu 24.04
Python: 3.14.4
PM4Py: 2.7.23.11
Pandas: 2.3.3

Dataset: synthetic_manufacturing.csv
Eventi: 17
Casi: 4

## Risultati

| Transizione | Media in minuti |
|---|---:|
| Taglio -> Fresatura | 17.75 |
| Fresatura -> Fresatura | 42.00 |
| Fresatura -> Saldatura | 35.50 |
| Saldatura -> Controllo | 21.25 |

## Validazione

Confronto PM4Py / Pandas: OK
Regression test: PASSED

## Conclusione

PM4Py calcola correttamente gli intervalli medi
tra eventi consecutivi nel dataset sperimentale.

Questi intervalli non devono essere interpretati
automaticamente come tempi di attesa o lavorazione.

## Evidenza

Esecuzione locale del 27/10/2026.

File prodotti:
- results/exp02_performance_dfg.csv
- results/exp02_summary.json
