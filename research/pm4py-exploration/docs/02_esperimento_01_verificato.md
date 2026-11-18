# EXP-01 — Importazione CSV e DFG delle frequenze

**Stato:** ESEGUITO — risultato conforme ai valori attesi  
**Data di esecuzione:** 27 ottobre 2026  
**Esecutore:** Artur

## Domanda
Con un piccolo event log manifatturiero siamo in grado di ricostruire le transizioni osservate e le relative frequenze in modo riproducibile?

## Dataset e metodo
- `data/synthetic_manufacturing.csv` — **sintetico**, 4 casi e 17 eventi.
- Il caso P004 presenta la transizione `Fresatura → Fresatura`.
- Ogni riga è un evento puntuale, senza lifecycle `start` e `complete`.
- Operazioni: `pandas.read_csv`, normalizzazione timestamp a UTC, `pm4py.format_dataframe`, `pm4py.discover_dfg`.
- Esecuzione: `python scripts/exp01_dfg.py` dalla radice del progetto.

## Ambiente verificato
- Python: `3.14.4`
- PM4Py: `2.7.23.11`
- Pandas: `2.3.3`
- Sistema di esecuzione: Ubuntu (PC di sviluppo)

## Risultati
| Source | Target | Atteso | Ottenuto | Esito |
|---|---|---:|---:|---|
| Taglio | Fresatura | 4 | 4 | Conforme |
| Fresatura | Fresatura | 1 | 1 | Conforme |
| Fresatura | Saldatura | 4 | 4 | Conforme |
| Saldatura | Controllo | 4 | 4 | Conforme |

Attività iniziali: `{'Taglio': 4}`.  
Attività finali: `{'Controllo': 4}`.

**Errori nell'esecuzione comunicata:** nessuno.  
**Differenze dai valori attesi:** nessuna.

## File prodotti sul PC di sviluppo
- `results/exp01_dfg_frequency.csv`
- `results/exp01_summary.json`

I nomi e i percorsi sono confermati dall'output del programma; il contenuto completo dei file non è stato riesaminato separatamente.

## Interpretazione
Il DFG delle frequenze ricostruisce correttamente le transizioni direttamente successive. La transizione `Fresatura → Fresatura` è un loop osservato, non ancora qualificabile come rework senza il contesto di dominio. Non sono stati calcolati tempi di attesa o misure di saturazione.

## Limiti e prossima attività
Il dataset è piccolo e sintetico. Questo test verifica un comportamento di base su un input controllato, non l'affidabilità generale di PM4Py né la capacità di identificare colli di bottiglia. Prossima attività: EXP-02, Performance DFG e significato degli intervalli temporali.
