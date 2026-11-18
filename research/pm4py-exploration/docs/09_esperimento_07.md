# P05 — EXP-07: Generalizzazione del rilevatore

Stato: DA VERIFICARE

## Domanda di ricerca
Il rilevatore individua segnali di congestione
anche quando cambia la stazione critica?

## Scenari
A: CNC critica per capacità insufficiente.
B: Taglio critico per capacità insufficiente.
C: CNC lenta, ma con capacità sufficiente.

## Metodologia
12 casi per scenario.
Intervallo di arrivo: 7 minuti.

Il generatore conosce durate e capacità.
Il rilevatore riceve soltanto i dati degli eventi.

Indicatori:
- Attesa media e massima.
- Percentuale di casi in attesa.
- Service time verificato con PM4Py.

## Ipotesi
H1: rilevazione Fresatura CNC nello scenario A.
H2: rilevazione Taglio nello scenario B.
H3: nessuna criticità nello scenario C.
H4: rifiuto di log senza campi temporali necessari.

## Limiti
Si tratta di tre benchmark sintetici deterministici.
Il rilevatore identifica code osservate, non
dimostra automaticamente vincoli causali.

Non è ancora verificato su dataset esterni.

Un'assenza di attesa nel campione non dimostra
che un processo non abbia vincoli di capacità.

## Risultati effettivi
Da compilare dopo l'esecuzione.

## Conclusioni
Da compilare dopo la verifica.
