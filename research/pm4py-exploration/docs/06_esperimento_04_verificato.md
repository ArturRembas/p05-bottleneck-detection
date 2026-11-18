# P05 — EXP-04: Process Mining e parallelismo

Stato: VERIFICATO

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
Esecuzione: 27/10/2026.

- Eventi: 32
- Casi: 8
- Controllo materiali -> Setup macchina: 4
- Setup macchina -> Controllo materiali: 4
- Operatore AND nel Process Tree: presente
- Operatore AND nel controllo sequenziale: assente
- SVG: creato
- Verifiche automatiche: PASSED

Process Tree ottenuto:

    ->( 'Ordine',
        +( 'Setup macchina', 'Controllo materiali' ),
        'Assemblaggio' )

Evidenze:
- results/exp04_summary.json
- results/exp04_process_tree.ptml
- results/exp04_petri_net.pnml
- results/exp04_process_tree.svg

## Conclusioni
Inductive Miner ha ricostruito correttamente
un modello contenente parallelismo sul dataset sintetico.

Il controllo sequenziale ha restituito un modello
privo di operatore AND.

L'esperimento dimostra la capacità dell'algoritmo
di inferire comportamenti concorrenti, non
la contemporaneità fisica delle lavorazioni.

Occorre validare questa capacità anche su log
più rappresentativi di processi reali.
