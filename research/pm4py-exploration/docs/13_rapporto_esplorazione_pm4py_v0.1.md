# P05 — Bottleneck Detection in Processes
## Rapporto tecnico di esplorazione PM4Py

**Versione:** 0.1
**Data:** 28 ottobre 2026
**Corso:** Complex Systems Design — UNICAM
**Ambito:** Core Process Mining e analisi delle criticità
**Stato:** Ricognizione sperimentale completata; da revisionare con il gruppo

---

## 1. Obiettivo

L'attività esplorativa ha verificato quali funzionalità
di PM4Py siano utilizzabili per il progetto P05.

Gli obiettivi principali sono:

- Ricostruzione dei processi dagli event log.
- Individuazione di varianti e attività ripetute.
- Analisi delle prestazioni temporali.
- Studio dei comportamenti concorrenti.
- Identificazione di possibili criticità produttive.
- Verifica dei requisiti informativi dei dataset.

L'esplorazione non costituisce ancora una validazione
del sistema completo di bottleneck detection.

## 2. Ambiente sperimentale

Sistema operativo: Ubuntu 24.04
Python: 3.14.4
PM4Py: 2.7.23.11
Pandas: 2.3.3

Gli esperimenti utilizzano dataset sintetici
controllati e verifiche automatiche.

## 3. Registro degli esperimenti

| ID | Oggetto | Risultato | Stato |
|---|---|---|---|
| EXP-01 | DFG delle frequenze | Transizioni e frequenze corrette | PASS |
| EXP-02 | Performance DFG | Intervalli corretti rispetto a Pandas | PASS |
| EXP-03 | Varianti e ripetizioni | Due varianti, una attività ripetuta | PASS |
| EXP-04 | Parallelismo | Operatore AND individuato | PASS |
| EXP-05 | Capacità e attese | Effetto della capacità CNC verificato | PASS |
| EXP-06 | Prima detection | CNC critica individuata | PASS |
| EXP-07 | Scenari alternativi | Tre scenari corretti su tre | PASS |
| EXP-08 | Code transitorie e crescenti | Limite della prima euristica dimostrato | PASS |
| EXP-09 | Dinamica delle code | Tre classificazioni corrette | PASS |
| EXP-10 | Profilazione event log | Cinque scenari corretti su cinque | PASS |

PASS significa superamento delle verifiche predisposte
per il singolo esperimento, non validazione generale.

## 4. Funzionalità PM4Py esplorate

### 4.1 Process discovery

Metodi verificati:

- pm4py.discover_dfg()
- pm4py.discover_performance_dfg()
- pm4py.get_variants_as_tuples()
- pm4py.discover_process_tree_inductive()
- pm4py.discover_petri_net_inductive()

I primi esperimenti hanno confermato la possibilità
di ricostruire le transizioni e i percorsi osservati.

Inductive Miner ha riconosciuto un operatore AND
in un dataset sintetico con ordinamenti alternativi.

La concorrenza inferita non dimostra automaticamente
la sovrapposizione temporale effettiva.

### 4.2 Analisi delle prestazioni

Sono state verificate:

- Frequenze delle transizioni.
- Durate tra eventi consecutivi.
- Service time con timestamp di inizio e fine.
- Attese con timestamp espliciti di ingresso in coda.
- Attività ripetute nello stesso caso.

Il tempo fra due eventi consecutivi non può essere
interpretato automaticamente come tempo di attesa.

### 4.3 Attività ripetute

Metodo verificato:

pm4py.get_rework_cases_per_activity()

Il metodo ha identificato la ripetizione di Fresatura
nel caso P004.

Una ripetizione osservata non dimostra necessariamente
una rilavorazione dovuta a difetti produttivi.

## 5. Esperimenti sui vincoli di capacità

### EXP-05

Sono stati confrontati due scenari con otto pezzi:

| Indicatore | 1 CNC | 2 CNC |
|---|---:|---:|
| Attesa media (min) | 17.50 | 0.00 |
| Attesa massima (min) | 35.00 | 0.00 |
| Service time (min) | 12.00 | 12.00 |
| Makespan (min) | 96.00 | 61.00 |
| Throughput osservato (pezzi/h) | 5.00 | 7.87 |

L'incremento della capacità ha eliminato le attese
nel benchmark utilizzato.

Il throughput osservato è relativo a un campione finito
e non deve essere confuso con la capacità a regime.

### EXP-06

Processo:
Taglio -> Fresatura CNC -> Controllo.

Con una CNC:
- Attesa media Fresatura: 17.50 minuti.
- Pezzi in attesa: 87.5%.
- Criticità candidata: Fresatura CNC.

Con due CNC:
- Nessuna attesa osservata.
- Nessuna criticità candidata.

Il rilevatore individua una stazione con attesa
nel benchmark, non dimostra causalità generale.

### EXP-07

Tre scenari sintetici:

A: CNC con capacità insufficiente.
B: Taglio con capacità insufficiente.
C: CNC lenta ma con capacità sufficiente.

Risultati: 3 scenari su 3 riconosciuti.

Il caso C conferma che una lavorazione lunga
non deve essere automaticamente classificata
come collo di bottiglia.

## 6. Dinamica delle code

### EXP-08

Sono stati confrontati:

- Arrivi regolari senza attesa.
- Un picco temporaneo con coda riassorbita.
- Un sovraccarico con coda crescente.

L'euristica mean_wait > 0 identifica la presenza
di attese, ma non ne distingue la dinamica.

### EXP-09

È stato realizzato il modulo:

core/queue_diagnostics.py

Classificazioni sperimentali:

- no_observed_queue
- recovered_queue
- growing_queue
- inconclusive

Tre scenari principali e due controlli aggiuntivi
hanno superato le verifiche.

I parametri attualmente utilizzati sono euristici:
- Minimo di 6 osservazioni.
- Finestra finale di 3 osservazioni.
- Soglia di crescita del 70%.

Questi parametri non sono ancora validati su
dataset indipendenti e non devono essere trattati
come soglie scientifiche definitive.

## 7. Requisiti informativi degli event log

### EXP-10

È stato realizzato:

core/log_capabilities.py

Il modulo verifica la possibilità strutturale
di calcolare determinate grandezze.

| Analisi | Campi principali richiesti |
|---|---|
| DFG | case_id, activity, timestamp |
| Intervalli fra eventi | case_id, activity, timestamp |
| Service time | start_timestamp, timestamp |
| Waiting time | queue_entry, start_timestamp |

I requisiti temporali si aggiungono all'identificazione
del caso e dell'attività quando tali metriche vengono
associate a eventi del processo.

Risultati: 5 scenari su 5 superati.

La presenza di colonne sufficienti non garantisce
che il loro significato sia corretto.

Il semantic mapping richiederà conferma della
semantica e validazione dei dati.

## 8. Matrice di fattibilità preliminare

| Funzionalità | Supporto disponibile | Ulteriore lavoro P05 |
|---|---|---|
| Importazione e normalizzazione | PM4Py/Pandas | Mapping e validazione |
| DFG delle frequenze | PM4Py | Visualizzazione e API |
| Performance DFG | PM4Py | Interpretazione delle durate |
| Varianti del processo | PM4Py | Ranking e filtri |
| Rilevazione ripetizioni | PM4Py | Interpretazione del rework |
| Process Tree e Petri net | PM4Py | Valutazione dei modelli |
| Service time | PM4Py | Semantica lifecycle |
| Waiting time | Pandas e dati temporali | Gestione dei timestamp |
| Dinamica delle code | Modulo sperimentale P05 | Validazione delle euristiche |
| Bottleneck detection | Prototipo euristico | Algoritmo e validazione causale |
| Profilazione del log | Modulo sperimentale P05 | Qualità e semantica dei dati |

## 9. Proposta di organizzazione del core

Componenti candidati:

- log_capabilities: verifica preliminare dei dati.
- pm_engine: interfaccia con PM4Py.
- metrics: metriche quantitative del processo.
- queue_diagnostics: analisi delle code.
- bottleneck_detector: ranking delle criticità.

Questa organizzazione è una proposta tecnica,
non una decisione architetturale ratificata.

Il core dovrebbe rimanere indipendente da FastAPI,
dall'interfaccia grafica e dagli agenti AI.

## 10. Interfacce candidate

Funzionalità da discutere con Luca e Diego:

profile_log(input) -> capability_report

discover_process(log) -> process_model

calculate_metrics(log) -> process_metrics

detect_criticalities(metrics) -> candidate_findings

Gli output dovrebbero includere:

- Identificativo dell'analisi.
- Identificativo di attività o transizione.
- Metrica e unità di misura.
- Numero di osservazioni.
- Evidenze a supporto.
- Limiti e dati mancanti.
- Classificazione o stato di validazione.

I contratti effettivi devono ancora essere definiti
con il gruppo.

## 11. Limiti complessivi

Tutti gli esperimenti completati utilizzano dati
sintetici controllati.

Molti controlli sono stati costruiti sulle
caratteristiche note degli stessi benchmark.

Non è stata ancora dimostrata:

- L'accuratezza su dataset manifatturieri esterni.
- La robustezza a dati rumorosi o incompleti.
- La generalizzabilità delle soglie euristiche.
- La diagnosi causale dei vincoli produttivi.
- La correttezza su processi complessi multi-risorsa.
- L'efficacia con log privi di start/end.
- L'interoperabilità reale con gli altri moduli.

Le ipotesi di processo e i dati disponibili
devono essere esplicitati in ogni analisi.

## 12. Questioni da discutere con il gruppo

1. Definizione operativa di bottleneck.
2. Schema canonico minimo degli event log.
3. Responsabilità del semantic mapping AI.
4. Formato dei risultati per API e agenti.
5. Metodologia di ranking delle criticità.
6. Dataset esterni per la validazione.
7. Priorità di XES e OCEL.
8. Ruolo di SimPy e delle simulazioni.
9. Confini fra core deterministico e AI.
10. Criteri di accettazione degli incrementi.

## 13. Conclusione

La ricognizione dimostra la fattibilità tecnica
di un nucleo di Process Mining basato su PM4Py
per le funzionalità sperimentate.

Le analisi deterministiche e le prime euristiche
di individuazione delle criticità funzionano
nei benchmark controllati.

Per completare P05 sarà necessario sviluppare
e validare una metodologia affidabile di
identificazione dei bottleneck, separando
osservazioni quantitative, ipotesi e diagnosi.

Questo documento costituisce materiale tecnico
da condividere e discutere con il gruppo P05.

Non rappresenta l'approvazione definitiva
dell'architettura o degli algoritmi.
