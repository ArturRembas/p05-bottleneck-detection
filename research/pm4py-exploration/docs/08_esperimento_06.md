# P05 — EXP-06: Identificazione di criticità candidate

Stato: DA VERIFICARE

## Domanda di ricerca

È possibile individuare una stazione con segnali di
congestione mediante l'analisi di un event log?

## Ipotesi

H1: la Fresatura CNC presenta attese positive con
una sola macchina.

H2: Taglio e Controllo non presentano attese.

H3: con due CNC le attese si annullano.

H4: l'euristica identifica la Fresatura CNC senza
ricevere l'identità del vincolo dal generatore.

## Dataset

Processo seriale:
Taglio -> Fresatura CNC -> Controllo

Otto pezzi, arrivo ogni 7 minuti.

Service time deterministici:
- Taglio: 4 minuti
- Fresatura CNC: 12 minuti
- Controllo: 3 minuti

## Metodologia

Il generatore conosce le capacità delle risorse.
Il rilevatore riceve soltanto l'event log.

Metriche:
- attesa media per attività;
- attesa massima;
- percentuale di pezzi in attesa;
- service time verificato tramite PM4Py.

L'euristica segnala attività con attesa media positiva
e le ordina in modo decrescente.

## Limiti

È un benchmark sintetico con scenario noto.

Il rilevatore individua segnali di congestione,
non dimostra automaticamente la causalità.

La rilevazione richiede il momento di ingresso
nella coda, inizio e fine lavorazione.

L'euristica è preliminare e potrebbe produrre
falsi positivi su processi reali.

## Risultati effettivi

Da compilare dopo l'esecuzione.

## Conclusioni

Da compilare dopo la validazione.
