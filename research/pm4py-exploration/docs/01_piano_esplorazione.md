# P05 — Piano di esplorazione tecnica PM4Py

**Data di apertura:** 27/10/2026  
**Autore del filone esplorativo:** Artur  
**Stato:** proposta tecnica individuale da confrontare con Luca e Diego.

## Obiettivo
Determinare quali funzionalità di Process Mining siano disponibili in PM4Py e quali risultati siano affidabili per costruire il motore analitico di P05. Non confondere i tempi osservati fra eventi con attese o vincoli di capacità.

## Domande di ricerca
1. Quali formati possiamo importare (CSV, XES, eventualmente OCEL)?
2. Quali modelli e varianti possiamo ricostruire (DFG, BPMN/Petri net)?
3. Quali indicatori si ricavano direttamente dagli event log?
4. Quali campi sono necessari per distinguere tempi di lavorazione e tempi di attesa?
5. Quali metriche servono per *segnalare* e poi *validare* un collo di bottiglia?
6. Quale contratto minimo può esporre `core/pm_engine.py` alle API/agenti?

## Sequenza sperimentale proposta
| ID | Esperimento | Evidenza | Stato |
|---|---|---|---|
| EXP-01 | Importazione CSV e DFG frequenze | CSV + JSON + verbale | Da eseguire |
| EXP-02 | Performance DFG e semantica timestamp | CSV KPI + note sui limiti | Da eseguire |
| EXP-03 | Varianti, loop e rework | Tabella varianti e controlli | Da eseguire |
| EXP-04 | Process discovery: BPMN/Petri | Confronto modelli | Da eseguire |
| EXP-05 | Dataset con bottleneck noto | Baseline e verifica detection | Da progettare |
| EXP-06 | Contratto funzioni core / API | Proposta di interfaccia | Da discutere |

## Regole per gli esperimenti
- Conservare dataset e versione degli strumenti.
- Registrare assunzioni e limitazioni, anche nei risultati negativi.
- Non attribuire a PM4Py una conclusione causale non dimostrata.
- Separare prove individuali dalle decisioni approvate dal gruppo.
- Evitare dati reali sensibili: usare dati sintetici o dataset pubblici consentiti.

## Riferimenti
- PM4Py: https://processintelligence.solutions/pm4py/
- API: https://processintelligence.solutions/pm4py/api/
- PyPI (versione fissata per la riproducibilità): https://pypi.org/project/pm4py/
