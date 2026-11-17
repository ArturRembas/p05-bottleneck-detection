# P05 — EXP-09: Analisi della dinamica delle code

Stato: DA VERIFICARE

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

Da compilare dopo l'esecuzione.

## Conclusioni

Da compilare dopo la verifica.
