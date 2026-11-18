# P05 — Esperimento EXP-03
## Analisi delle varianti e delle attività ripetute

Stato: DA VERIFICARE
Dataset: synthetic_manufacturing.csv

## 1. Obiettivo

Verificare le funzionalità di PM4Py per:

- Identificazione delle varianti del processo.
- Conteggio dei casi per variante.
- Rilevazione di attività ripetute.
- Confronto indipendente dei risultati con Pandas.

## 2. Metodi esplorati

### pm4py.get_variants_as_tuples()

Identifica le sequenze di attività osservate nei casi
e ne determina la frequenza.

### pm4py.get_rework_cases_per_activity()

Individua le attività eseguite più volte nello stesso caso.

Il termine "rework" utilizzato dalla libreria
non implica necessariamente una rilavorazione causata
da difetti produttivi.

## 3. Dataset

Eventi: 17
Casi: 4
Dominio simulato: produzione discreta

Attività:
- Taglio
- Fresatura
- Saldatura
- Controllo

## 4. Risultati attesi

Variante standard:
Taglio -> Fresatura -> Saldatura -> Controllo
Frequenza attesa: 3 casi (75%)

Variante con ripetizione:
Taglio -> Fresatura -> Fresatura -> Saldatura -> Controllo
Frequenza attesa: 1 caso (25%)

Attività ripetuta: Fresatura
Caso interessato: P004

## 5. Validazione

I risultati PM4Py vengono confrontati con conteggi
indipendenti effettuati mediante Pandas.

Sono previsti controlli automatici sulle frequenze,
sulle ripetizioni e sul dataset originale.

## 6. Risultati effettivi

Da compilare dopo l'esecuzione.

## 7. Limiti metodologici

Una ripetizione di attività non dimostra automaticamente
l'esistenza di una rilavorazione dovuta a un difetto.

Occorrono informazioni aggiuntive sul processo,
sul contesto produttivo e sulle cause delle ripetizioni.

Inoltre, una ripetizione non dimostra di per sé
l'esistenza di un collo di bottiglia.

## 8. Conclusioni

Da compilare dopo la verifica sperimentale.
