# P05 — EXP-08: Congestione temporanea e persistente

Stato: DA VERIFICARE

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
