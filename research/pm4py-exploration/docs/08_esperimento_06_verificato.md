# P05 — EXP-06: Identificazione di criticità candidate

Stato: VERIFICATO

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

Esecuzione locale: 27/10/2026.
PM4Py: 2.7.23.11.

Scenario con 1 CNC:
- Taglio: attesa media 0 minuti.
- Fresatura CNC: attesa media 17.50 minuti.
- Controllo: attesa media 0 minuti.
- Fresatura CNC: 87.5% dei casi in attesa.
- Criticità candidata: Fresatura CNC.

Scenario con 2 CNC:
- Nessuna attesa rilevata.
- Nessuna criticità candidata.

Validazione scenario noto: PASSED.

Evidenza: results/exp06_summary.json

## Conclusioni

L'euristica individua correttamente la stazione
con attesa positiva nel benchmark sintetico.

La rimozione delle attese aumentando la capacità
è coerente con il vincolo introdotto nel generatore.

Il risultato non dimostra ancora la generalizzabilità
del rilevatore su altri processi o dataset.

## 10. Limiti implementativi

- L'analisi richiede queue_entry, start_timestamp
  e timestamp.
- Le verifiche strutturali dello script EXP-06
  contengono nomi di attività fissati nel codice.
- La regola mean_wait > 0 è una prima euristica,
  non una diagnosi causale.
- Il benchmark usa un solo processo sintetico noto.
- È necessaria una verifica su configurazioni
  differenti e su un controllo negativo.
