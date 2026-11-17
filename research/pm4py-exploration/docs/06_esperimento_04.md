# P05 — EXP-04: Process Mining e parallelismo

Stato: DA VERIFICARE

## Obiettivo
Valutare se Inductive Miner riconosce un comportamento
compatibile con l'esecuzione parallela di due attività.

## Dataset
Log sintetico: 8 casi, 32 eventi.

Quattro casi osservano A prima di B.
Quattro casi osservano B prima di A.

A = Controllo materiali
B = Setup macchina

## Metodi PM4Py
- discover_dfg()
- discover_process_tree_inductive()
- discover_petri_net_inductive()

## Ipotesi
H1: il DFG mostra entrambi gli ordinamenti.
H2: il Process Tree contiene un operatore AND.
H3: il controllo con un solo ordine non contiene AND.

## Limite metodologico
L'inferenza di concorrenza nel modello non dimostra
una sovrapposizione temporale reale.

Il dataset contiene eventi ordinati nel tempo.
Il test verifica l'interpretazione del comportamento,
non l'esistenza di lavorazioni fisicamente simultanee.

## Risultati effettivi
Da compilare dopo l'esecuzione.

## Conclusioni
Da compilare dopo la validazione.
