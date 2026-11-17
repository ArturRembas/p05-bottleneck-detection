# P05 — Esplorazione PM4Py (ambiente individuale)

Questo progetto contiene le prime prove **esplorative** relative al core di Process Mining di P05. Non è il repository ufficiale né sostituisce le decisioni del gruppo.

## 1. Prerequisiti
- Linux/Ubuntu, Python >= 3.11 (Ubuntu 24.04 distribuisce tipicamente Python 3.12).
- Accesso a Internet per installare le dipendenze.
- `python3-venv` installato (su Ubuntu: `sudo apt install python3-venv`, se necessario).

## 2. Ambiente isolato
Aprire un terminale nella directory del progetto:

```bash
python3 --version
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
python -c "import pm4py, pandas; print('PM4Py:', pm4py.__version__, 'Pandas:', pandas.__version__)"
```

In caso di errore `ensurepip is not available`, installare `python3-venv` con apt e ripetere.

## 3. Primo esperimento

```bash
python scripts/exp01_dfg.py
```

Attesi: **4 casi, 17 eventi, 4 archi DFG**, frequenze `4/1/4/4` come riportate in `docs/02_esperimento_01.md`.

I file prodotti si trovano in `results/` e non sono precompilati, così da distinguere dati attesi da dati osservati.

## 4. Documentazione
- `docs/01_piano_esplorazione.md`: obiettivi, metodologia, roadmap esplorativa.
- `docs/02_esperimento_01.md`: protocollo dell'esperimento e spazio per l'esito.
- `docs/03_catalogo_metodi.md`: inventario dei metodi e verifiche da completare.

## 5. Materiale da condividere dopo la prova
La cartella `results/` contiene i risultati archiviati della baseline sperimentale v0.1. Gli esperimenti possono essere rieseguiti per verificare la riproducibilità, ma l'esito delle esecuzioni precedenti non costituisce una validazione generale degli algoritmi.

## 6. Nota importante
I dati sono sintetici e non contengono informazioni sull'inizio e la fine delle lavorazioni. Il DFG risultante **non costituisce** una diagnosi di bottleneck.
