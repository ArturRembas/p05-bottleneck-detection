# EXP-01 — Importazione CSV e DFG delle frequenze

**Stato:** preparato, NON ancora eseguito sulla macchina di sviluppo  
**Data di esecuzione:** [compilare]  
**Esecutore:** Artur

## Domanda
Con un piccolo event log manifatturiero siamo in grado di ricostruire le transizioni osservate e le relative frequenze in modo riproducibile?

## Input
- `data/synthetic_manufacturing.csv` — **sintetico**, creato esclusivamente per il test.
- 4 casi e 17 eventi: un caso (`P004`) contiene una ripetizione di `Fresatura`.
- Ogni riga rappresenta un evento puntuale; **non** sono presenti start/end lifecycle.

## Metodi
- `pandas.read_csv()`
- `pandas.to_datetime(..., utc=True)`
- `pm4py.format_dataframe()`
- `pm4py.discover_dfg()`

## Risultati attesi (derivati manualmente dal dataset)
| Source | Target | Frequenza attesa |
|---|---|---:|
| Taglio | Fresatura | 4 |
| Fresatura | Fresatura | 1 |
| Fresatura | Saldatura | 4 |
| Saldatura | Controllo | 4 |

Attività iniziale `Taglio`: 4 casi; finale `Controllo`: 4 casi.

## Esecuzione
Da terminale nella cartella del progetto:

```bash
python scripts/exp01_dfg.py
```

Il programma produce:
- `results/exp01_dfg_frequency.csv`
- `results/exp01_summary.json` (versioni ambiente, hash dataset, statistiche principali)

## Esito effettivo
- Esecuzione: [OK / KO]
- Versione Python: [compilare]
- Versione PM4Py: [compilare]
- Differenze rispetto ai valori attesi: [compilare]
- Errori riscontrati: [compilare]

## Interpretazione e limiti
Il DFG misura quante volte due attività si susseguono direttamente nello stesso caso. **Non dimostra** che `Fresatura` sia una stazione congestionata, né calcola automaticamente i tempi di attesa. La ripetizione osservata su P004 è un loop, ma occorre contesto per stabilire se sia rework.

## Prossimo esperimento
EXP-02: performance DFG e significato degli intervalli temporali, da definire dopo la verifica dell'EXP-01.
