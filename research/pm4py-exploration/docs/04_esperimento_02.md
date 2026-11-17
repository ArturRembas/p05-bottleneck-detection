# EXP-02 — Performance DFG e semantica degli intervalli

**Stato:** predisposto, esecuzione da verificare sul PC di sviluppo  
**Data di esecuzione:** [da compilare]  
**Esecutore:** Artur

## Domanda di ricerca
PM4Py ricava correttamente, da un log con un solo timestamp per evento, l'intervallo medio tra attività direttamente successive?

## Dataset
`data/synthetic_manufacturing.csv`: 4 casi, 17 eventi, timestamp timezone-aware e un ciclo `Fresatura → Fresatura`. I dati sono **sintetici**, con un solo timestamp per attività.

## Metodo e controlli
- Preparazione con `pd.read_csv`, `pd.to_datetime(..., utc=True)`, ordinamento stabile e `pm4py.format_dataframe`.
- Calcolo con `pm4py.discover_performance_dfg(log, perf_aggregation_key="mean")`.
- Controllo indipendente: differenza fra timestamp consecutivi per ciascun caso, poi media degli intervalli per ciascuna coppia di attività.
- Assertion per confrontare i risultati di PM4Py e quelli calcolati in modo indipendente.
- Regression test per il dataset originale, identificato con hash SHA-256.

## Risultati attesi
| Transizione | Occorrenze | Intervalli osservati (min) | Media attesa (min) |
|---|---:|---|---:|
| Taglio → Fresatura | 4 | 15, 20, 18, 18 | 17,75 |
| Fresatura → Fresatura | 1 | 42 | 42,00 |
| Fresatura → Saldatura | 4 | 35, 30, 37, 40 | 35,50 |
| Saldatura → Controllo | 4 | 20, 20, 25, 20 | 21,25 |

## Esecuzione
Dalla radice del progetto e con `.venv` attivo:

```bash
python scripts/exp02_performance_dfg.py
```

Output:
- `results/exp02_performance_dfg.csv`
- `results/exp02_summary.json`

## Esito effettivo
- Esecuzione: [OK/KO]
- Ambiente: [versioni]
- Verifica indipendente: [OK/KO]
- Regression test: [passed/not_applicable/KO]
- Differenze dai risultati attesi: [descrivere]
- Eventuali errori: [descrivere]

## Interpretazione e limiti
Con un timestamp per attività misuriamo **differenze temporali tra eventi successivi dello stesso caso**. Non possiamo dedurre da questi valori, senza ulteriori informazioni, né la durata di lavorazione della fase di destinazione, né il tempo passato in coda, né il grado di saturazione di una macchina. Il dato non identifica da solo un bottleneck.

Il dataset è volutamente piccolo e controllato: non costituisce validazione su processi reali. Ulteriori esperimenti dovranno includere eventi `start`/`complete`, risorse/capacità e scenari con coda nota.

## Conclusione
[Da compilare dopo l'esecuzione: cosa è stato verificato; cosa rimane non dimostrato.]
