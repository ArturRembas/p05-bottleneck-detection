# P05 — EXP-09: Analisi della dinamica delle code

Stato: VERIFICATO

## Obiettivo

Verificare un modulo analitico riutilizzabile
capace di descrivere l'evoluzione delle attese.

## Input

Event log contenente:
- case_id
- activity
- queue_entry
- start_timestamp
- timestamp

## Classificazioni sperimentali

- no_observed_queue
- recovered_queue
- growing_queue
- inconclusive

## Parametri

Minimo osservazioni: 6
Finestra finale: 3 osservazioni
Soglia incremento: 70%

Questi parametri sono euristici e non validati.

## Ipotesi

H1: scenario A classificato senza coda.
H2: scenario B classificato come coda riassorbita.
H3: scenario C classificato come coda crescente.
H4: campioni troppo piccoli producono inconclusive.
H5: dati privi di campi necessari sono rifiutati.

## Limiti

La classificazione riguarda solo la finestra osservata.

Una coda crescente non dimostra da sola
la presenza di un bottleneck persistente.

L'assenza di attesa osservata non dimostra
l'assenza di un vincolo produttivo.

Le soglie devono essere valutate sperimentalmente.

La disponibilità di timestamp di ingresso in coda
e inizio lavorazione rimane un prerequisito.

## Risultati effettivi

Esperimento verificato con tre scenari sintetici.

- A: no_observed_queue — PASS
- B: recovered_queue — PASS
- C: growing_queue — PASS
- Campione insufficiente: inconclusive — PASS
- Colonne mancanti: errore gestito — PASS

Scenario B:
- Attesa media: 3.375 minuti
- Frazione di incrementi: 0.286

Scenario C:
- Attesa media: 17.500 minuti
- Frazione di incrementi: 1.000

Evidenza: results/exp09_summary.json

## Conclusioni

Il modulo queue_diagnostics.py distingue correttamente
i tre comportamenti nei benchmark utilizzati.

La logica è indipendente dagli script di generazione.

Le classificazioni sono descrittive e limitate
alla finestra osservata.

Le soglie euristiche richiedono ulteriori
esperimenti e validazione su dati indipendenti.

Non è ancora dimostrata la capacità di diagnosticare
automaticamente vincoli produttivi persistenti.
