# P05 — EXP-05
## Analisi dei tempi di attesa e dei vincoli di capacità

Stato: VERIFICATO

## 1. Domanda di ricerca

È possibile osservare l'effetto di un vincolo
di capacità sul tempo di attesa dei pezzi?

## 2. Ipotesi

H1: una singola CNC genera una coda crescente.
H2: due CNC eliminano l'attesa nello scenario scelto.
H3: PM4Py calcola correttamente il service time.
H4: il throughput osservato migliora con due CNC.

## 3. Dati sperimentali

- Otto pezzi.
- Arrivi deterministici ogni 7 minuti.
- Tempo di lavorazione: 12 minuti.
- Disciplina FIFO.
- Macchine identiche.
- Nessun guasto, fermo o setup aggiuntivo.

## 4. Scenari

A: una macchina CNC.
B: due macchine CNC.

## 5. Metodologia

Uno scheduler deterministico genera gli orari di:
- ingresso nella coda;
- inizio lavorazione;
- fine lavorazione.

Il tempo di attesa viene calcolato come:
inizio lavorazione - ingresso in coda.

Il service time viene verificato mediante PM4Py,
con timestamp di inizio e fine lavorazione.

## 6. Risultati attesi

Scenario A:
- Attesa media: 17.5 minuti.
- Attesa massima: 35 minuti.
- Service time: 12 minuti.
- Durata osservazione: 96 minuti.

Scenario B:
- Attesa media: 0 minuti.
- Attesa massima: 0 minuti.
- Service time: 12 minuti.
- Durata osservazione: 61 minuti.

## 7. Risultati effettivi

Da compilare dopo l'esecuzione.

## 8. Limiti

I dati sono sintetici e deterministici.

Il risultato non costituisce una validazione su dati
manifatturieri reali.

Il throughput osservato dipende dall'orizzonte
finito di otto pezzi e non coincide necessariamente
con la capacità teorica a regime.

Il vincolo è noto perché definito nel modello
generativo. L'identificazione automatica del
bottleneck sarà oggetto di esperimenti successivi.

## 9. Conclusioni

Da compilare dopo la verifica.


## 10. Verifica sperimentale del 27/10/2026

Ambiente: PM4Py 2.7.23.11.

### Scenario A - 1 CNC

- Attesa media: 17.50 minuti
- Attesa massima: 35.00 minuti
- Service time PM4Py: 12.00 minuti
- Makespan: 96.00 minuti
- Throughput osservato: 5.00 pezzi/ora

### Scenario B - 2 CNC

- Attesa media: 0.00 minuti
- Attesa massima: 0.00 minuti
- Service time PM4Py: 12.00 minuti
- Makespan: 61.00 minuti
- Throughput osservato: 7.87 pezzi/ora

### Validazione

- Confronto PM4Py/Pandas: OK in entrambi gli scenari
- Test di regressione: PASSED
- Confronto scenari: PASSED

### Conclusione

L'esperimento conferma l'effetto del vincolo
di capacità sui tempi di attesa, nel modello
sintetico deterministico utilizzato.

Non rappresenta ancora una rilevazione automatica
del bottleneck: la configurazione critica era nota
prima dell'esperimento.

I risultati devono essere distinti da una
validazione su dati manifatturieri reali.

Evidenza: results/exp05_summary.json
