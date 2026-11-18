# P05 — Esperimento EXP-03
## Analisi delle varianti e delle attività ripetute

Stato: VERIFICATO
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

Esecuzione locale: 27/10/2026.

Ambiente:
- Python 3.14.4
- PM4Py 2.7.23.11
- Pandas 2.3.3

Risultati:
- 17 eventi e 4 casi.
- Variante standard: 3 casi (75%).
- Variante con Fresatura ripetuta: 1 caso (25%).
- Attività ripetuta: Fresatura.
- Caso interessato: P004, con 2 esecuzioni.

Controlli:
- Confronto indipendente PM4Py/Pandas: OK.
- Test di regressione: PASSED.

Evidenze:
- results/exp03_variants.csv
- results/exp03_case_repetitions.csv
- results/exp03_summary.json

## 7. Limiti metodologici

Una ripetizione di attività non dimostra automaticamente
l'esistenza di una rilavorazione dovuta a un difetto.

Occorrono informazioni aggiuntive sul processo,
sul contesto produttivo e sulle cause delle ripetizioni.

Inoltre, una ripetizione non dimostra di per sé
l'esistenza di un collo di bottiglia.

## 8. Conclusioni

PM4Py ha individuato correttamente le varianti e le
attività ripetute nel dataset controllato.

La verifica indipendente conferma i risultati.

L'esperimento valida il funzionamento dei metodi
sul dataset utilizzato, non la loro accuratezza
su processi manifatturieri reali.

La ripetizione di un'attività costituisce un segnale
da approfondire, non una prova automatica di rework
o di bottleneck.
