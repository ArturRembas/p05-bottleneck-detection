# P05 — EXP-08: Congestione temporanea e persistente

Stato: VERIFICATO

## Domanda di ricerca

La presenza di tempi di attesa è sufficiente
per identificare un bottleneck produttivo?

## Ipotesi

H1: arrivi regolari con capacità sufficiente
non generano attesa.

H2: un picco temporaneo di arrivi genera
una coda destinata a riassorbirsi.

H3: un flusso di arrivi superiore alla capacità
genera una coda crescente nel campione.

H4: l'euristica mean_wait > 0 segnala
sia le code temporanee sia quelle persistenti.

## Metodologia

Tre log sintetici, otto casi ciascuno.

Singola stazione CNC, gestione FIFO.

Analisi mediante il rilevatore EXP-07.

Confronto dei tempi di attesa nella prima
e nella seconda metà dei casi.

## Limiti

I dati sono sintetici e deterministici.

Il confronto tra le due metà è una verifica
descrittiva, non un criterio generale
per diagnosticare bottleneck.

Per dimostrare persistenza e vincoli causali
serviranno osservazioni temporali più estese
e informazioni sulle risorse.

## Risultati effettivi

Da compilare dopo l'esecuzione.

## Conclusioni

Da compilare dopo la verifica.


## Verifica sperimentale — 27/10/2026

### Scenario A — Arrivi regolari
Attese: [0, 0, 0, 0, 0, 0, 0, 0]
Attesa media: 0 minuti.
Hotspot rilevato: no.
Esito: PASS.

### Scenario B — Picco temporaneo
Attese: [0, 9, 18, 0, 0, 0, 0, 0]
Attesa media: 3.375 minuti.
Prima metà: 6.750 minuti.
Seconda metà: 0 minuti.
Hotspot rilevato: sì.
Esito: PASS.

### Scenario C — Sovraccarico
Attese: [0, 5, 10, 15, 20, 25, 30, 35]
Attesa media: 17.500 minuti.
Prima metà: 7.500 minuti.
Seconda metà: 27.500 minuti.
Hotspot rilevato: sì.
Esito: PASS.

### Conclusioni

L'euristica di EXP-07 identifica correttamente
la presenza di attesa, ma segnala sia una
congestione transitoria sia una crescente.

Per distinguere i fenomeni sono necessari
indicatori relativi all'evoluzione temporale.

I risultati non dimostrano la presenza
di vincoli persistenti nel lungo periodo.

Validazione EXP-08: PASSED.

Evidenza: results/exp08_summary.json
