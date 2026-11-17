# Catalogo preliminare dei metodi PM4Py — P05

**Stato:** inventario iniziale basato sulla documentazione, non ancora verificato sperimentalmente.

| Metodo | Scopo | Prova prevista | Limite/attenzione |
|---|---|---|---|
| `pm4py.format_dataframe` | Normalizzare i nomi logici dei campi | EXP-01 | Richiede corretto mapping |
| `pm4py.discover_dfg` | Transizioni frequenti | EXP-01 | Non rappresenta da solo la concorrenza |
| `pm4py.discover_performance_dfg` | Prestazioni sulle transizioni | EXP-02 | Semantica dei timestamp fondamentale |
| `pm4py.get_variants` | Varianti delle tracce | EXP-03 | Conflitti d'ordine con timestamp uguali |
| `pm4py.get_rework_cases_per_activity` | Attività ripetute per caso | EXP-03 | Rework da validare nel dominio |
| `pm4py.discover_bpmn_inductive` | Modello BPMN | EXP-04 | Il modello è un'inferenza dal log |
| `pm4py.discover_petri_net_inductive` | Modello Petri net | EXP-04 | Verificare concorrenza/completezza log |

## Esito e decisione
Aggiornare dopo ciascuna prova: **disponibilità verificata, formato di output, esempio, limiti, ipotesi di utilizzo nel core P05**.
