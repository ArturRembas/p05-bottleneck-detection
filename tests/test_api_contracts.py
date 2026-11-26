from __future__ import annotations

import sys
from pathlib import Path
import pytest
from pydantic import ValidationError

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from fastapi.testclient import TestClient
from api.main import app
from api.schemas import (
    BottleneckTarget,
    CandidateBottleneck,
    EvidenceCategory,
    MetricProvenance,
    MetricStatus,
    ProcessKPI,
    TargetType,
    TimeSemantics,
)

client = TestClient(app)


def test_health_check():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"


def test_openapi_specification_version_and_operation_ids():
    response = client.get("/openapi.json")
    assert response.status_code == 200
    schema = response.json()
    assert schema["openapi"] == "3.1.0"

    paths = schema["paths"]
    assert "/api/v1/analyses/{analysis_id}/bottlenecks" in paths
    assert "/api/v1/analyses/{analysis_id}/kpis" in paths
    assert "/api/v1/analyses/{analysis_id}/publish" in paths

    # Operation ID stabili per il Tool Registry di Luca
    assert paths["/api/v1/analyses/{analysis_id}/bottlenecks"]["get"]["operationId"] == "get_candidate_bottlenecks"


def test_upload_rejects_unsupported_format():
    files = {"file": ("test.txt", b"dummy content", "text/plain")}
    response = client.post("/api/v1/analyses", files=files)
    assert response.status_code == 415
    assert response.json()["code"] == "UNSUPPORTED_LOG_FORMAT"


def test_endpoints_return_501_not_mocked_data():
    response = client.get("/api/v1/analyses/run-demo-001/bottlenecks")
    assert response.status_code == 501
    assert response.json()["code"] == "ANALYSIS_REPOSITORY_NOT_IMPLEMENTED"


def test_pr16_detector_alignment_and_evidence_categories():
    # Validazione esatta di PR #16: target tipizzato (transizione), categoria L1, senza forzare severity
    target = BottleneckTarget(
        target_type=TargetType.TRANSITION,
        target_name="CNC_Milling",
        source_activity="Cutting"
    )
    candidate = CandidateBottleneck(
        candidate_id="cand-01",
        ranking_status="ranked",
        support_policy={
            "policy_version": "0.1.0",
            "min_observations": 3,
            "min_distinct_cases": 3,
        },
        target=target,
        evidence_category=EvidenceCategory.L1_DELAY_HOTSPOT,
        rank=1,
        observations_count=12,
        distinct_cases_count=4,  # Rispetta il min-support >= 3
        case_coverage_ratio=0.80,
        severity=None            # Non forzata se non supportata
    )
    assert candidate.evidence_category == EvidenceCategory.L1_DELAY_HOTSPOT
    assert candidate.distinct_cases_count >= 3
    assert candidate.severity is None


def test_data_capability_honesty_validation():
    provenance = MetricProvenance(
        method="maximum_mean_gap",
        evidence_category=EvidenceCategory.L1_DELAY_HOTSPOT
    )
    valid_kpi = ProcessKPI(
        metric="observed_transition_gap",
        value=None,
        unit="hours",
        status=MetricStatus.UNAVAILABLE,
        time_semantics=TimeSemantics.COMPLETION_ONLY,
        sample_size=100,
        provenance=provenance,
        unavailable_reason="Completion-only logs do not observe queue start"
    )
    assert valid_kpi.status == MetricStatus.UNAVAILABLE

    # Errore se value != None quando status = unavailable
    with pytest.raises(ValidationError):
        ProcessKPI(
            metric="observed_transition_gap",
            value=12.5,
            unit="hours",
            status=MetricStatus.UNAVAILABLE,
            time_semantics=TimeSemantics.COMPLETION_ONLY,
            sample_size=100,
            provenance=provenance
        )


@pytest.mark.parametrize(
    "payload",
    [
        {
            "target_type": "transition",
            "target_name": "Welding",
        },
        {
            "target_type": "workstation",
            "target_name": "CNC",
        },
        {
            "target_type": "activity",
            "target_name": "Cutting",
            "source_activity": "Welding",
        },
        {
            "target_type": "activity",
            "target_name": "Cutting",
            "station_id": "CNC-01",
        },
        {
            "target_type": "transition",
            "target_name": "Welding",
            "source_activity": "Cutting",
            "station_id": "CNC-01",
        },
        {
            "target_type": "workstation",
            "target_name": "CNC",
            "station_id": "CNC-01",
            "source_activity": "Cutting",
        },
        {
            "target_type": "activity",
            "target_name": "   ",
        },
    ],
)
def test_invalid_bottleneck_targets(payload):
    with pytest.raises(ValidationError):
        BottleneckTarget(**payload)


@pytest.mark.parametrize(
    "payload",
    [
        {
            "target_type": "activity",
            "target_name": "Cutting",
        },
        {
            "target_type": "transition",
            "target_name": "Welding",
            "source_activity": "Cutting",
        },
        {
            "target_type": "workstation",
            "target_name": "CNC",
            "station_id": "CNC-01",
        },
        {
            "target_type": "transition",
            "target_name": "Milling",
            "source_activity": "Milling",
        },
    ],
)
def test_valid_bottleneck_targets(payload):
    target = BottleneckTarget(**payload)
    assert target.target_name == payload["target_name"]


@pytest.mark.parametrize(
    "n,c,rank,status,valid",
    [
        (12, 4, 1, "ranked", True),
        (3, 3, 1, "ranked", True),
        (2, 2, 1, "ranked", False),
        (10, 1, 1, "ranked", False),
        (0, 0, 1, "ranked", False),
        (3, 5, 1, "ranked", False),
        (5, 0, 1, "ranked", False),
        (5, 5, None, "ranked", False),
        (2, 2, None, "insufficient_support", True),
        (10, 1, None, "insufficient_support", True),
        (3, 3, None, "insufficient_support", False),
        (0, 0, None, "insufficient_support", False),
        (0, 0, None, "unavailable", True),
        (2, 2, None, "unavailable", False),
        (3, 3, None, "no_positive_signal", True),
        (2, 2, None, "no_positive_signal", False),
        (3, 3, 1, "no_positive_signal", False),
    ],
)
def test_ranking_support_validation(n, c, rank, status, valid):
    payload = {
        "candidate_id": "candidate-test",
        "target": {
            "target_type": "transition",
            "target_name": "Welding",
            "source_activity": "Cutting",
        },
        "evidence_category": "L1_delay_hotspot",
        "rank": rank,
        "ranking_status": status,
        "observations_count": n,
        "distinct_cases_count": c,
        "case_coverage_ratio": 0.0 if n == 0 else 0.5,
        "support_policy": {
            "policy_version": "0.1.0",
            "min_observations": 3,
            "min_distinct_cases": 3,
        },
    }

    if valid:
        candidate = CandidateBottleneck(**payload)
        assert candidate.rank == rank
    else:
        with pytest.raises(ValidationError):
            CandidateBottleneck(**payload)


def test_configurable_support_threshold():
    payload = {
        "candidate_id": "candidate-config",
        "target": {
            "target_type": "transition",
            "target_name": "Welding",
            "source_activity": "Cutting",
        },
        "evidence_category": "L1_delay_hotspot",
        "rank": 1,
        "ranking_status": "ranked",
        "observations_count": 3,
        "distinct_cases_count": 3,
        "case_coverage_ratio": 0.75,
        "support_policy": {
            "policy_version": "0.1.0-test",
            "min_observations": 5,
            "min_distinct_cases": 4,
        },
    }

    with pytest.raises(ValidationError):
        CandidateBottleneck(**payload)

    payload["observations_count"] = 5
    payload["distinct_cases_count"] = 4

    candidate = CandidateBottleneck(**payload)
    assert candidate.rank == 1
