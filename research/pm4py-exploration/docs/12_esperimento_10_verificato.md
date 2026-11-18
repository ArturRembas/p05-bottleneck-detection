# P05 — EXP-10: Profilazione degli event log

Stato: VERIFICATO

## Obiettivo

Identificare quali analisi sono strutturalmente
possibili in base ai campi e alla validità dei dati.

## Capacità valutate

- DFG
- Intervalli tra eventi
- Service time
- Waiting time

## Scenari

1. Event log completo.
2. Event log minimo.
3. Log senza ingresso in coda.
4. Log senza inizio lavorazione.
5. Log con timestamp non valido.

## Ipotesi

Ogni scenario deve produrre le capacità previste
dalla struttura e dai dati temporali disponibili.

## Limitazioni

La disponibilità dei campi non ne dimostra
la correttezza semantica.

Il timestamp potrebbe indicare un evento iniziale,
finale o un'altra osservazione.

Il profilo è preliminare e non sostituisce
la validazione completa dei dati.

## Risultati effettivi

Cinque scenari verificati:

1. Completo: tutte le capacità disponibili.
2. Minimo: DFG e intervalli fra eventi.
3. Senza ingresso in coda: waiting time non disponibile.
4. Senza inizio: service e waiting time non disponibili.
5. Timestamp finale invalido: DFG e service time
   non disponibili; waiting time strutturalmente possibile.

Risultati: 5/5 PASS.
Evidenza: results/exp10_summary.json.

Durante la prima esecuzione è comparso un warning
relativo all'inferenza del formato temporale.
È stata predisposta una correzione con ISO 8601.

## Conclusioni

Il modulo identifica correttamente le capacità
strutturali nei cinque scenari controllati.

Non certifica ancora la semantica dei timestamp,
la completezza delle tracce o la qualità complessiva
dell'event log.

La validazione temporale deve essere approfondita
prima dell'utilizzo su dataset manifatturieri reali.
