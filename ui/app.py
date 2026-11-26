import os

import pandas as pd
import requests
import streamlit as st


st.set_page_config(
    page_title="P05 | Bottleneck Detection System",
    layout="wide",
    initial_sidebar_state="expanded",
)

API_BASE_URL = os.getenv(
    "P05_API_URL", "http://localhost:8000"
).rstrip("/")

API_PREFIX = f"{API_BASE_URL}/api/v1"
MAX_UPLOAD_BYTES = 50 * 1024 * 1024
REQUEST_TIMEOUT = 10


def api_request(method, path, **kwargs):
    """Execute an HTTP request without fabricating backend results."""
    try:
        response = requests.request(
            method,
            f"{API_PREFIX}{path}",
            timeout=REQUEST_TIMEOUT,
            **kwargs,
        )
    except requests.exceptions.Timeout:
        st.warning("Backend request timed out.")
        return None
    except requests.exceptions.RequestException:
        st.warning("Backend service is unreachable.")
        return None

    try:
        payload = response.json()
    except ValueError:
        st.error(
            f"Invalid backend response (HTTP {response.status_code})."
        )
        return None

    if response.status_code == 501:
        message = (
            payload.get("message", "Service pending integration.")
            if isinstance(payload, dict)
            else "Service pending integration."
        )
        st.info(f"Backend scaffold — HTTP 501: {message}")
        return None

    if not response.ok:
        message = (
            payload.get("message", "Request rejected.")
            if isinstance(payload, dict)
            else "Request rejected."
        )
        st.error(f"HTTP {response.status_code}: {message}")
        return None

    return payload


def render_candidate(candidate):
    """Display a finding using the current API contract."""
    target = candidate.get("target", {})
    metric = candidate.get("primary_metric", {})
    coverage = candidate.get("observation_coverage", {})
    group = candidate.get("ranking_group") or {}

    name = target.get("target_name", "Unknown target")

    if target.get("target_type") == "transition":
        name = f"{target.get('source_activity', '?')} -> {name}"

    if target.get("target_type") == "workstation":
        name = f"{name} ({target.get('station_id', '?')})"

    st.markdown(f"**{name}**")

    st.caption(
        f"Evidence: {candidate.get('evidence_category', 'Unknown')}"
    )

    status = metric.get("status")
    value = metric.get("value")

    if status == "unavailable" or value is None:
        st.metric("Primary metric", "Unavailable")
        st.caption(
            metric.get("unavailable_reason")
            or "No eligible measurement available."
        )
    else:
        st.metric(
            metric.get("metric", "Primary metric"),
            f"{value:.2f} {metric.get('unit', '')}",
        )

    st.caption(
        f"Metric status: {status or 'Unknown'} | "
        f"Semantics: {metric.get('time_semantics', 'Unknown')}"
    )

    ranking_status = candidate.get("ranking_status")
    rank = candidate.get("rank")

    if ranking_status == "ranked" and rank is not None:
        st.write(
            f"Rank: {rank} — Group: "
            f"{group.get('group_id', 'Unknown')}"
        )
    else:
        st.write(f"Unranked — {ranking_status}")

    st.write(
        f"Eligible observations: "
        f"{candidate.get('observations_count', 'Unknown')}"
    )
    st.write(
        f"Distinct contributing cases: "
        f"{candidate.get('distinct_cases_count', 'Unknown')}"
    )

    ratio = coverage.get("ratio")
    st.write(
        "Observation coverage: "
        + (
            f"{ratio:.1%}"
            if ratio is not None
            else "Unknown"
        )
    )

    st.caption(
        f"Coverage class: "
        f"{coverage.get('coverage_class', 'Unknown')}"
    )

    fraction = candidate.get("positive_wait_fraction")
    if fraction is not None:
        st.write(f"Positive-wait fraction: {fraction:.1%}")

    severity = candidate.get("severity")
    st.caption(f"Severity: {severity or 'Not classified'}")

    for limitation in candidate.get("limitations", []):
        st.caption(f"Limitation: {limitation}")

    evidence_refs = candidate.get("evidence_refs", [])
    if evidence_refs:
        st.write("Evidence references:", evidence_refs)

    st.divider()


st.markdown(
    "### P05 — Bottleneck Detection in Manufacturing Processes"
)
st.caption(
    "AI Puzzle Framework | M1 Integration Scaffold"
)

st.sidebar.markdown("#### Dataset Upload & Mapping")

uploaded_file = st.sidebar.file_uploader(
    "Source Event Log",
    type=["csv", "xes"],
    help="Maximum accepted size: 50 MiB.",
)

if uploaded_file is not None:
    valid_upload = True

    if uploaded_file.size == 0:
        st.sidebar.error("The selected file is empty.")
        valid_upload = False

    elif uploaded_file.size > MAX_UPLOAD_BYTES:
        st.sidebar.error("The file exceeds the 50 MiB limit.")
        valid_upload = False

    if valid_upload:
        if uploaded_file.name.lower().endswith(".csv"):
            try:
                uploaded_file.seek(0)

                preview = pd.read_csv(
                    uploaded_file,
                    nrows=5,
                    dtype=str,
                    keep_default_na=False,
                )

                st.sidebar.caption(
                    "Local structural preview — not a backend profile."
                )
                st.sidebar.write(
                    f"Columns: {len(preview.columns)}"
                )
                st.sidebar.write(list(preview.columns))

            except Exception:
                st.sidebar.warning(
                    "Local CSV preview unavailable. "
                    "Backend validation remains authoritative."
                )

        else:
            st.sidebar.caption(
                "XES profiling requires the backend service."
            )

        if st.sidebar.button(
            "Upload for Dataset Profiling",
            use_container_width=True,
        ):
            st.session_state.pop("dataset_profile", None)
            st.session_state.pop("analysis_payload", None)

            mime_type = (
                "text/csv"
                if uploaded_file.name.lower().endswith(".csv")
                else "application/xml"
            )

            with st.spinner("Requesting dataset profiling..."):
                profile = api_request(
                    "POST",
                    "/datasets/upload",
                    files={
                        "file": (
                            uploaded_file.name,
                            uploaded_file.getvalue(),
                            mime_type,
                        )
                    },
                )

                if (
                    isinstance(profile, dict)
                    and profile.get("dataset_id")
                    and profile.get("input_sha256")
                    and profile.get("profile_ref")
                ):
                    st.session_state["dataset_profile"] = profile
                    st.sidebar.success("Dataset profile received.")

profile = st.session_state.get("dataset_profile")

if profile:
    st.sidebar.write("Dataset ID:", profile["dataset_id"])
    st.sidebar.write("Profile:", profile["profile_ref"])


st.sidebar.markdown("#### Human Oversight — Mapping")

st.sidebar.info(
    "Mapping proposal, correction and trusted human confirmation "
    "require backend services that are not yet integrated."
)

st.sidebar.button(
    "Confirm Semantic Mapping",
    disabled=True,
    use_container_width=True,
)

st.sidebar.button(
    "Execute Analysis",
    disabled=True,
    use_container_width=True,
    help="Requires a confirmed mapping and ingestion authorization.",
)


tab_topology, tab_governance, tab_assistant = st.tabs([
    "Process Discovery & Topology",
    "Bottleneck Analysis & Governance",
    "Knowledge Assistant & Audit",
])


with tab_topology:
    st.markdown("##### Directly-Follows Graph (DFG)")

    st.info(
        "Process discovery visualization is not yet integrated. "
        "No process graph has been generated."
    )

    st.slider(
        "Variant Coverage Threshold (%)",
        min_value=10,
        max_value=100,
        value=80,
        disabled=True,
        help="Reserved for future process discovery integration.",
    )


with tab_governance:
    col_results, col_action = st.columns([2, 1])

    with col_results:
        st.markdown("##### Detector Findings")

        analysis = st.session_state.get("analysis_payload")
        analysis_id = (
            analysis.get("analysis_id")
            if isinstance(analysis, dict)
            else None
        )

        if analysis_id:
            candidates = api_request(
                "GET",
                f"/analyses/{analysis_id}/bottlenecks",
            )

            if isinstance(candidates, list):
                if candidates:
                    st.caption(
                        "Ranks are comparable only within "
                        "the same ranking group."
                    )

                    for candidate in candidates:
                        render_candidate(candidate)
                else:
                    st.info("No findings returned.")

        else:
            st.info(
                "No completed analysis is available. "
                "Detector findings require confirmed ingestion "
                "and backend execution."
            )

    with col_action:
        st.markdown("##### Human Oversight Gate")

        st.info(
            "No verified operational countermeasure is available."
        )

        st.text_area(
            "Supervisor Review Notes",
            disabled=True,
        )

        st.button(
            "Approve Countermeasure",
            disabled=True,
            use_container_width=True,
        )

        st.button(
            "Authorize External Publication",
            disabled=True,
            use_container_width=True,
        )

        st.caption(
            "Countermeasure approval and external publication "
            "are independent governed operations."
        )


with tab_assistant:
    st.markdown("##### Supervisor Copilot & Operational Knowledge")

    st.info(
        "RAG and AI-assisted explanations are not integrated "
        "in this M1 frontend scaffold."
    )

    st.text_input(
        "Knowledge Base Query",
        disabled=True,
    )

    st.caption(
        "No document retrieval or AI inference has been performed."
    )
