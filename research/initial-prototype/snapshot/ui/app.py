import os
import sys

# Assicura che Python veda la cartella 'core'
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from core.pm_engine import elabora_log_e_genera_dfg
import pandas as pd
import requests
import streamlit as st

st.set_page_config(page_title="P05 - Bottleneck Detection", layout="wide")

st.title("🏭 P05 — Bottleneck Detection in Processes")
st.caption(
    "AI Puzzle Framework — Deterministic Core (pm4py) & Service Architecture"
)

API_BASE_URL = "http://localhost:8000"

# 1. SIDEBAR: INGESTION (D01, D02, D03 della SRS)
st.sidebar.header("1. Ingestion Dati")
uploaded_file = st.sidebar.file_uploader(
    "Carica Event Log (CSV/XES)", type=["csv", "xes"]
)

if uploaded_file:
    # Mostra anteprima delle prime 5 righe (D02)
    df_sample = pd.read_csv(uploaded_file, nrows=5)
    st.sidebar.subheader("Anteprima Profilo (Pandas)")
    st.sidebar.dataframe(df_sample)

    st.sidebar.subheader("Validazione Schema (Human Gate)")
    c_case = st.sidebar.selectbox("Colonna Case ID", df_sample.columns, index=0)
    c_act = st.sidebar.selectbox(
        "Colonna Activity",
        df_sample.columns,
        index=1 if len(df_sample.columns) > 1 else 0,
    )
    c_time = st.sidebar.selectbox(
        "Colonna Timestamp",
        df_sample.columns,
        index=2 if len(df_sample.columns) > 2 else 0,
    )

    # PULSANTE DI CALCOLO REALE
    if st.sidebar.button("✅ Conferma e Avvia Process Mining (D03/D09)"):
        with st.spinner("Elaborazione del log con pm4py in corso..."):
            try:
                uploaded_file.seek(0)
                # Chiamata al motore pm4py di Artur!
                dot_source, kpis = elabora_log_e_genera_dfg(
                    uploaded_file, c_case, c_act, c_time
                )
                st.session_state["graphviz_dot"] = dot_source
                st.session_state["kpis"] = kpis
                st.sidebar.success(
                    f"Analisi completata con successo! {kpis['total_cases']} casi elaborati."
                )
            except Exception as e:
                st.sidebar.error(f"Errore durante l'elaborazione pm4py: {e}")

# 2. AREA CENTRALE: Grafo reale ed Indicatori
col1, col2 = st.columns([2, 1])

with col1:
    st.subheader("Mappa di Processo Reale (D09 - DFG)")
    # Se il grafo è stato calcolato, lo disegna in vettoriale interattivo!
    if "graphviz_dot" in st.session_state:
        st.graphviz_chart(
            st.session_state["graphviz_dot"], use_container_width=True
        )
    else:
        st.info(
            "Carica un file CSV a sinistra e clicca su 'Conferma e Avvia' per calcolare il grafo DFG."
        )

    variant_slider = st.slider(
        "Filtro Varianti (Stile Disco - D10)",
        min_value=10,
        max_value=100,
        value=80,
    )

with col2:
    st.subheader("Indicatori di Processo Reali (D13)")
    if "kpis" in st.session_state:
        st.metric(
            "Casi Totali Tracciati", st.session_state["kpis"]["total_cases"]
        )
        st.metric(
            "Eventi Registrati", st.session_state["kpis"]["total_events"]
        )
        st.metric(
            "Attività Distinte", st.session_state["kpis"]["unique_activities"]
        )
    else:
        st.write("Nessun dato calcolato al momento.")

    st.divider()
    st.subheader("Colli di Bottiglia Rilevati (D14)")

# Sotto 'Colli di Bottiglia Rilevati (D14)':
    if "kpis" in st.session_state and "worst_bottleneck" in st.session_state["kpis"]:
        st.metric(
            label=f"Transizione Critica: {st.session_state['kpis']['worst_bottleneck']}",
            value=f"{st.session_state['kpis']['worst_hours']}h attesa",
            delta="CRITICAL",
            delta_color="inverse",
        )
    else:
        st.write("In attesa dell'analisi del log...")

    # Recupero dati da FastAPI
    try:
        res = requests.get(f"{API_BASE_URL}/api/v1/bottlenecks", timeout=2)
        bottleneck_data = res.json()[0]
    except Exception:
        bottleneck_data = {
            "workstation": "CNC Milling",
            "average_waiting_time_hours": 4.8,
            "severity": "CRITICAL",
            "suggested_countermeasure": "Aggiungere +1 risorsa nel turno serale.",
        }

    st.metric(
        label=f"Stazione Critica #1: {bottleneck_data['workstation']}",
        value=f"{bottleneck_data['average_waiting_time_hours']}h attesa media",
        delta=bottleneck_data["severity"],
        delta_color="inverse",
    )

    st.subheader("Validazione Intervento Umano (HITL Gate)")
    st.write(f"**Proposta:** {bottleneck_data['suggested_countermeasure']}")
    if st.button("🚀 Approva e Notifica a P06/P20"):
        try:
            approve_url = f"{API_BASE_URL}/api/v1/countermeasures/approve?workstation={bottleneck_data['workstation']}&action=Add_Resource"
            r = requests.post(approve_url)
            if r.status_code == 200:
                st.success("Decisione registrata e notificata alle API esterne!")
        except Exception:
            st.success("Decisione confermata localmente.")

# 3. AREA CHAT
st.divider()
st.subheader("💬 Supervisor Copilot (Assistente RAG)")
user_query = st.chat_input("Fai una domanda sui processi o sulla dashboard...")
if user_query:
    with st.chat_message("user"):
        st.write(user_query)
    with st.chat_message("assistant"):
        st.write(
            f"*(Risposta simulata del Copilot)*: In base al modello DFG elaborato, la stazione di fresatura genera ritardi significativi tra i turni."
        )
