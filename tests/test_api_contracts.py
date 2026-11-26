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
    response = client.post("/api/v1/datasets/upload", files=files)
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
        **finding_fields(12),
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
        observation_coverage={
            "eligible_count": 12,
            "total_count": 12,
            "ratio": 1.0,
            "coverage_class": "full",
        },
        ranking_group={
            "group_id": "gap-full",
            "metric": "observed_transition_gap",
            "target_type": "transition",
            "analytical_view_ref": "completion-view",
            "observation_window_ref": "full-log",
            "coverage_class": "full",
        },
        case_coverage_ratio=0.80,
        affected_cases_count=4,
        total_cases_count=5,
        severity=None            # Non forzata se non supportata
    )
    assert candidate.evidence_category == EvidenceCategory.L1_DELAY_HOTSPOT
    assert candidate.distinct_cases_count >= 3
    assert candidate.severity is None


def test_data_capability_honesty_validation():
    provenance = MetricProvenance(
        method="correlated_queue_wait"
    )

    valid_kpi = ProcessKPI(
        metric="queue_waiting_time",
        value=None,
        unit="seconds",
        status=MetricStatus.UNAVAILABLE,
        time_semantics=TimeSemantics.QUEUE_WAITING_DURATION,
        sample_size=0,
        provenance=provenance,
        unavailable_reason=(
            "Completion-only logs do not observe queue entry "
            "and service start"
        ),
    )

    assert valid_kpi.status == MetricStatus.UNAVAILABLE
    assert valid_kpi.value is None

    with pytest.raises(ValidationError):
        ProcessKPI(
            metric="queue_waiting_time",
            value=12.5,
            unit="seconds",
            status=MetricStatus.UNAVAILABLE,
            time_semantics=TimeSemantics.QUEUE_WAITING_DURATION,
            sample_size=0,
            provenance=provenance,
            unavailable_reason="Required timestamps are missing",
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
        **finding_fields(n, status),
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
        "observation_coverage": {
            "eligible_count": n,
            "coverage_class": "unknown",
        },
        "ranking_group": {
            "group_id": "gap-unknown",
            "metric": "observed_transition_gap",
            "target_type": "transition",
            "analytical_view_ref": "completion-view",
            "observation_window_ref": "full-log",
            "coverage_class": "unknown",
        } if status == "ranked" else None,

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
        **finding_fields(3),
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
        "observation_coverage": {
            "eligible_count": 3,
            "coverage_class": "unknown",
        },
        "ranking_group": {
            "group_id": "gap-unknown",
            "metric": "observed_transition_gap",
            "target_type": "transition",
            "analytical_view_ref": "completion-view",
            "observation_window_ref": "full-log",
            "coverage_class": "unknown",
        },

        "support_policy": {
            "policy_version": "0.1.0-test",
            "min_observations": 5,
            "min_distinct_cases": 4,
        },
    }

    with pytest.raises(ValidationError):
        CandidateBottleneck(**payload)

    payload["observations_count"] = 5
    payload["primary_metric"]["sample_size"] = 5
    payload["observation_coverage"]["eligible_count"] = 5
    payload["distinct_cases_count"] = 4

    candidate = CandidateBottleneck(**payload)
    assert candidate.rank == 1


@pytest.mark.parametrize(
    "eligible,total,ratio,coverage_class,valid",
    [
        (10, 10, 1.0, "full", True),
        (5, 10, 0.5, "partial", True),
        (0, 10, 0.0, "partial", True),
        (5, None, None, "unknown", True),
        (0, 0, None, "unknown", True),
        (11, 10, 1.0, "full", False),
        (5, 10, 0.8, "partial", False),
        (5, 10, 0.5, "full", False),
        (10, 10, 1.0, "partial", False),
        (5, None, 0.5, "unknown", False),
        (5, None, None, "full", False),
        (5, 10, None, "partial", False),
        (1, 0, None, "unknown", False),
    ],
)
def test_observation_coverage(
    eligible, total, ratio, coverage_class, valid
):
    from api.schemas import ObservationCoverage

    payload = {
        "eligible_count": eligible,
        "total_count": total,
        "ratio": ratio,
        "coverage_class": coverage_class,
    }

    if valid:
        coverage = ObservationCoverage(**payload)
        assert coverage.eligible_count == eligible
    else:
        with pytest.raises(ValidationError):
            ObservationCoverage(**payload)


@pytest.mark.parametrize(
    "issue",
    [
        "missing_group",
        "wrong_target_type",
        "wrong_coverage_class",
        "inconsistent_eligible_count",
    ],
)
def test_invalid_ranking_group(issue):
    payload = {
        **finding_fields(4),
        "candidate_id": "group-test",
        "target": {
            "target_type": "transition",
            "target_name": "Welding",
            "source_activity": "Cutting",
        },
        "evidence_category": "L1_delay_hotspot",
        "ranking_status": "ranked",
        "rank": 1,
        "observations_count": 4,
        "distinct_cases_count": 4,
        "support_policy": {
            "policy_version": "0.1.0",
        },
        "observation_coverage": {
            "eligible_count": 4,
            "total_count": 8,
            "ratio": 0.5,
            "coverage_class": "partial",
        },
        "ranking_group": {
            "group_id": "gap-partial",
            "metric": "observed_transition_gap",
            "target_type": "transition",
            "analytical_view_ref": "completion-view",
            "observation_window_ref": "full-log",
            "coverage_class": "partial",
        },
    }

    # Verify that the original payload is valid.
    CandidateBottleneck(**payload)

    if issue == "missing_group":
        payload["ranking_group"] = None
    elif issue == "wrong_target_type":
        payload["ranking_group"]["target_type"] = "activity"
    elif issue == "wrong_coverage_class":
        payload["ranking_group"]["coverage_class"] = "full"
    elif issue == "inconsistent_eligible_count":
        payload["observations_count"] = 5

    with pytest.raises(ValidationError):
        CandidateBottleneck(**payload)


@pytest.mark.parametrize(
    "metric,semantics",
    [
        ("observed_transition_gap", "observed_inter_event_gap"),
        ("processing_time", "processing_duration"),
        ("queue_waiting_time", "queue_waiting_duration"),
        ("throughput_time", "throughput_duration"),
    ],
)
@pytest.mark.parametrize("value", [0.0, 120.0])
def test_valid_temporal_metrics(metric, semantics, value):
    kpi = ProcessKPI(
        metric=metric,
        value=value,
        unit="seconds",
        status="derived",
        time_semantics=semantics,
        sample_size=3,
        provenance={"method": "test_calculation"},
    )

    assert kpi.value == value


@pytest.mark.parametrize(
    "changes",
    [
        {"value": -1.0},
        {"value": float("nan")},
        {"value": float("inf")},
        {"value": float("-inf")},
        {"unit": "hours"},
        {"unit": "minutes"},
        {"time_semantics": "queue_waiting_duration"},
        {"time_semantics": "processing_duration"},
        {"time_semantics": "unknown"},
        {"sample_size": 0},
        {"value": None},
        {"unavailable_reason": "Unexpected reason"},
    ],
)
def test_invalid_temporal_metrics(changes):
    payload = {
        "metric": "observed_transition_gap",
        "value": 120.0,
        "unit": "seconds",
        "status": "derived",
        "time_semantics": "observed_inter_event_gap",
        "sample_size": 3,
        "provenance": {
            "method": "maximum_mean_gap",
        },
    }

    # Confirm that the unchanged payload is valid.
    ProcessKPI(**payload)

    payload.update(changes)

    with pytest.raises(ValidationError):
        ProcessKPI(**payload)


def test_provenance_has_no_unsupported_defaults():
    provenance = MetricProvenance(
        method="activity_count"
    )

    assert provenance.evidence_category is None
    assert provenance.algorithm_version is None


def test_non_temporal_metric():
    kpi = ProcessKPI(
        metric="activity_count",
        value=12,
        unit="count",
        status="derived",
        time_semantics="not_applicable",
        sample_size=12,
        provenance={"method": "count_events"},
    )

    assert kpi.value == 12
    assert kpi.provenance.evidence_category is None


def test_observed_zero_is_not_unavailable():
    kpi = ProcessKPI(
        metric="queue_waiting_time",
        value=0,
        unit="seconds",
        status="derived",
        time_semantics="queue_waiting_duration",
        sample_size=8,
        provenance={"method": "correlated_queue_wait"},
    )

    assert kpi.value == 0
    assert kpi.status == MetricStatus.DERIVED
    assert kpi.unavailable_reason is None


def test_unavailable_metric_requires_reason():
    with pytest.raises(ValidationError):
        ProcessKPI(
            metric="queue_waiting_time",
            value=None,
            unit="seconds",
            status="unavailable",
            time_semantics="queue_waiting_duration",
            sample_size=0,
            provenance={"method": "correlated_queue_wait"},
        )


def finding_fields(n, status="ranked"):
    return {
        "primary_metric": {
            "metric": "observed_transition_gap", "unit": "seconds",
            "value": None if status == "unavailable" else (0 if status == "no_positive_signal" else 120),
            "status": "unavailable" if status == "unavailable" else "derived",
            "time_semantics": "observed_inter_event_gap", "sample_size": n,
            "unavailable_reason": "No eligible pairs" if status == "unavailable" else None,
            "provenance": {"method": "mean_gap", "evidence_category": "L1_delay_hotspot"},
        },
        "analytical_view_ref": "completion-view", "observation_window_ref": "full-log",
        "detector_rule_ref": "rule-test", "detector_config_ref": "config-test",
    }


@pytest.mark.parametrize('changes', [
    {'value': 0}, {'status': 'estimated'}, {'sample_size': 2},
    {'metric': 'queue_waiting_time', 'time_semantics': 'queue_waiting_duration'},
    {'provenance': {'method': 'mean_gap', 'evidence_category': 'L2_queue_candidate'}},
])
def test_invalid_ranked_metric(changes):
    payload = ranked_payload()
    payload['primary_metric'].update(changes)
    with pytest.raises(ValidationError):
        CandidateBottleneck(**payload)


def ranked_payload():
    return {
        **finding_fields(4), 'candidate_id': 'test',
        'target': {'target_type': 'transition', 'target_name': 'B', 'source_activity': 'A'},
        'evidence_category': 'L1_delay_hotspot', 'ranking_status': 'ranked', 'rank': 1,
        'support_policy': {'policy_version': 'test'}, 'observations_count': 4,
        'distinct_cases_count': 4,
        'observation_coverage': {'eligible_count': 4, 'coverage_class': 'unknown'},
        'ranking_group': {'group_id': 'g', 'metric': 'observed_transition_gap',
                          'target_type': 'transition', 'analytical_view_ref': 'completion-view',
                          'observation_window_ref': 'full-log', 'coverage_class': 'unknown'},
    }


def test_l3_reserved():
    payload = ranked_payload()
    payload['evidence_category'] = 'L3_capacity_hypothesis'
    with pytest.raises(ValidationError):
        CandidateBottleneck(**payload)


def test_l2_requires_queue_evidence():
    payload = ranked_payload()
    payload.update(target={'target_type': 'activity', 'target_name': 'B'},
                   evidence_category='L2_queue_candidate', positive_wait_fraction=0.75)
    payload['primary_metric'].update(metric='queue_waiting_time', time_semantics='queue_waiting_duration',
                                     provenance={'method': 'correlated_queue_wait', 'evidence_category': 'L2_queue_candidate'})
    payload['ranking_group'].update(metric='queue_waiting_time', target_type='activity')
    CandidateBottleneck(**payload)
    payload['positive_wait_fraction'] = 0
    with pytest.raises(ValidationError):
        CandidateBottleneck(**payload)


@pytest.mark.parametrize('status', ['partial', 'unavailable'])
def test_capability_reason_required(status):
    from api.schemas import CapabilityAssessment
    with pytest.raises(ValidationError):
        CapabilityAssessment(status=status, runtime_implemented=False)
    CapabilityAssessment(status=status, reason='Missing timestamps', runtime_implemented=False)


def mapping_request():
    return {'dataset_id': 'd', 'input_sha256': 'a'*64, 'mapping_id': 'm',
            'mapping_version': 1, 'mapping_contract_version': '0.1.0'}


def test_staged_ingestion_contract():
    assert client.post('/api/v1/datasets/upload', files={'file': ('log.csv', b'a,b\n1,2', 'text/csv')}).status_code == 501
    assert client.post('/api/v1/datasets/d/mapping/propose', params={'mapping_document_ref': 'proposal'}).status_code == 501
    assert client.post('/api/v1/datasets/d/mapping/confirm', json=mapping_request()).status_code == 501
    assert client.post('/api/v1/datasets/other/mapping/confirm', json=mapping_request()).status_code == 409
    assert client.post('/api/v1/analyses', json=mapping_request()).status_code == 422
    request = {**mapping_request(), 'approval_ref': 'approval', 'ingestion_authorization_ref': 'authorization'}
    assert client.post('/api/v1/analyses', json=request).status_code == 501


def test_governance_stubs():
    request = {'result_revision': 'r1', 'authorized_consumers': ['P06'], 'publication_approval_ref': 'decision'}
    url = '/api/v1/analyses/a/publish'
    assert client.post(url, json=request).status_code == 501
    for changes in [{'authorized_consumers': []}, {'authorized_consumers': ['P06', 'P06']}, {'analysis_id': 'other'}]:
        assert client.post(url, json={**request, **changes}).status_code == 422
    assert client.post(url, json={'result_revision': 'r1', 'publication_approval_ref': 'decision'}).status_code == 422
    assert client.post('/api/v1/analyses/a/countermeasures/approve', json={
        'result_revision': 'r1', 'candidate_id': 'c', 'countermeasure_id': 'cm',
        'workstation': 'w', 'action': 'review'}).status_code == 501
    assert client.get('/api/v1/analyses/a/export-bpmn').status_code == 501


def test_generated_openapi_consistency():
    import json
    path = Path(__file__).resolve().parents[1] / 'schemas/openapi_v0.2.json'
    assert json.loads(path.read_text(encoding='utf-8')) == app.openapi()
    ids = [operation['operationId'] for methods in app.openapi()['paths'].values()
           for operation in methods.values() if isinstance(operation, dict) and 'operationId' in operation]
    assert len(ids) == len(set(ids))
