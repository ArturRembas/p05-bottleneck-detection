import os
import requests
import pandas as pd
import streamlit as st

# Configurazione pagina pulita e minimale
st.set_page_config(
    page_title="P05 | Bottleneck Detection System",
    layout="wide",
    initial_sidebar_state="expanded"
)

API_BASE_URL = os.getenv("P05_API_URL", "http://localhost:8000")
API_PREFIX = f"{API_BASE_URL}/api/v1"

# Header istituzionale e sobrio
st.markdown("### P05 — Bottleneck Detection in Manufacturing Processes")
st.caption("AI Puzzle Framework | Level 2 Analytical Service | Integration Baseline v0.2")
st.markdown("---")

# =====================================================================
# SIDEBAR: DATA INGESTION & RUN CONTROL
# =====================================================================
st.sidebar.markdown("#### Ingestion & Schema Mapping")
uploaded_file = st.sidebar.file_uploader(
    "Source Event Log (CSV format)",
    type=["csv"],
    help="Upload an execution log. Maximum accepted size: 50 MB."
)

if uploaded_file:
    try:
        df_preview = pd.read_csv(uploaded_file, nrows=5)
        st.sidebar.markdown("**Schema Inspection (First 5 records)**")
        st.sidebar.dataframe(df_preview, use_container_width=True, hide_index=True)

        st.sidebar.markdown("**Canonical Column Mapping**")
        c_case = st.sidebar.selectbox("Case Identifier", df_preview.columns, index=0)
        c_act = st.sidebar.selectbox("Activity Label", df_preview.columns, index=1 if len(df_preview.columns) > 1 else 0)
        c_time = st.sidebar.selectbox("Completion Timestamp", df_preview.columns, index=2 if len(df_preview.columns) > 2 else 0)

        if st.sidebar.button("Submit Ingestion Request", use_container_width=True):
            with st.spinner("Transmitting dataset to analysis backend..."):
                uploaded_file.seek(0)
                files = {"file": (uploaded_file.name, uploaded_file.getvalue(), "text/csv")}
                params = {
                    "case_id_col": c_case,
                    "activity_col": c_act,
                    "timestamp_col": c_time
                }

                try:
                    res = requests.post(f"{API_PREFIX}/analyses", files=files, params=params, timeout=10)
                    if res.status_code == 200:
                        st.session_state["analysis_payload"] = res.json()
                        st.sidebar.success("Analysis executed successfully.")
                    elif res.status_code == 501:
                        err = res.json()
                        st.sidebar.info(f"Backend Scaffold Status [HTTP 501]:\n{err.get('message', 'Analytical engine pending integration.')}")
                        st.session_state["backend_status"] = "scaffold_501"
                    else:
                        st.sidebar.error(f"HTTP {res.status_code}: {res.text}")
                except requests.exceptions.ConnectionError:
                    st.sidebar.warning(f"Connection failure: API service unreachable at {API_BASE_URL}.")
    except Exception as e:
        st.sidebar.error(f"Ingestion parsing failure: {e}")

# =====================================================================
# MAIN WORKSPACE: TABS ARCHITECTURE (Enterprise Layout)
# =====================================================================
tab_topology, tab_governance, tab_assistant = st.tabs([
    "Process Discovery & Topology",
    "Bottleneck Analysis & Governance",
    "Knowledge Assistant & Audit"
])

with tab_topology:
    col_graph, col_ctrl = st.columns([3, 1])

    with col_graph:
        st.markdown("##### Directly-Follows Graph (DFG) Overview")
        st.caption("Rendering observed workstation transitions and inter-activity latency.")

        # Area riservata al rendering Graphviz del motore
        st.container(border=True).info(
            "DFG visualization stream active. Awaiting verified analytical results from backend engine."
        )

    with col_ctrl:
        st.markdown("##### Discovery Controls")
        variant_slider = st.slider(
            "Variant Coverage Threshold (%)",
            min_value=10,
            max_value=100,
            value=80,
            help="Filters out low-frequency operational paths to isolate primary flow patterns."
        )
        st.caption("Configured method: Heuristic inter-activity gap aggregation (Mean).")

with tab_governance:
    col_kpi, col_action = st.columns([1, 1])

    with col_kpi:
        st.markdown("##### Detected Candidate Bottlenecks")

        # Retrieve bottlenecks only for a real analysis
        analysis_payload = st.session_state.get("analysis_payload")
        analysis_id = (
            analysis_payload.get("analysis_id")
            if analysis_payload
            else None
        )

        bottleneck_target = "Not available"

        if analysis_id:
            try:
                res = requests.get(
                    f"{API_PREFIX}/analyses/{analysis_id}/bottlenecks",
                    timeout=5
                )

                if res.status_code == 200:
                    b_list = res.json()

                    if b_list:
                        top_b = b_list[0]
                        bottleneck_target = top_b["target"]["target_name"]

                        waiting_time = top_b.get("waiting_time_hours")
                        metric_value = (
                            f"{waiting_time:.2f} hrs"
                            if waiting_time is not None
                            else "Unavailable"
                        )

                        st.metric(
                            label=f"Rank #{top_b['rank']} Hotspot: {bottleneck_target}",
                            value=metric_value,
                            delta=f"Severity: {top_b.get('severity') or 'Not classified'}",
                            delta_color="inverse"
                        )
                    else:
                        st.info("No bottleneck candidates found.")

                elif res.status_code == 501:
                    st.caption(
                        "Backend scaffold active: bottleneck retrieval not implemented yet."
                    )
                else:
                    st.warning(f"Unable to retrieve bottlenecks: HTTP {res.status_code}")

            except requests.exceptions.RequestException as e:
                st.warning(f"Backend connection error: {e}")

        else:
            st.info("Upload an event log and execute an analysis to view bottlenecks.")

        st.markdown("""
        **Operational Context (Illustrative):**
        - Observed Metric: Mean transition gap (not yet computed)
        - Epistemic Reliability: not yet available
        - Evidence Reference: Demonstration placeholder — no verified evidence linked.
        """)

    with col_action:
        st.markdown("##### Human Oversight Gate (HITL)")
        st.markdown(f"**Target Station:** `{bottleneck_target}`")
        st.info(
            "Demonstration mode: no operational countermeasure "
            "is currently available."
        )

        st.markdown(
            "**Illustrative Proposed Countermeasure:** "
            "Reallocate +1 operator during evening shift changeovers."
        )

        st.caption(
            "Illustrative estimate only — simulation not executed. "
            "The displayed -22% queue reduction is not a verified result."
        )

        supervisor_notes = st.text_area(
            "Review Notes & Decision Log",
            placeholder="Document rationale, shift constraints, or operational justification...",
            height=100
        )

        st.button(
            "Approve Countermeasure",
            disabled=True,
            use_container_width=True,
            help="Approval is disabled until a real candidate and countermeasure are available."
        )

        st.caption(
            "Countermeasure approval and external publication are separate operations. "
            "Neither operation is currently enabled in this frontend."
        )
with tab_assistant:
    st.markdown("##### Supervisor Copilot & Operational Knowledge")
    st.caption("Domain-specific assistance grounded on process documentation and validated run evidence.")

    user_query = st.text_input("Submit query to knowledge base", placeholder="e.g., Explain observed variance between Cutting and Milling...")

    if user_query:
        st.info(
            "Demonstration mode: this is an illustrative placeholder, "
            "not an AI-generated analysis."
        )

        st.markdown("**Illustrative System Response:**")

        st.container(border=True).markdown(
            f"*Query received:* `{user_query}`\n\n"
            "This is a demonstration response. No actual event-log analysis, "
            "document retrieval, or AI inference has been performed."
        )
