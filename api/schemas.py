from __future__ import annotations

from datetime import datetime, timezone
from enum import Enum
from math import isclose
from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field, model_validator


class ContractModel(BaseModel):
    """Base model enforcing strict schema conformance and rejecting extra fields."""
    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)


# =====================================================================
# PR #16 ALIGNMENT: THREE EVIDENCE CATEGORIES & TARGETS
# =====================================================================

class EvidenceCategory(str, Enum):
    """Evidence hierarchy defined in PR #16 (docs/DETECTOR_BASELINE.md)."""
    L1_DELAY_HOTSPOT = "L1_delay_hotspot"              # Statistically long observed inter-event gap
    L2_QUEUE_CANDIDATE = "L2_queue_candidate"          # Direct evidence of physical queue waiting
    L3_CAPACITY_HYPOTHESIS = "L3_capacity_hypothesis"  # Hypothesis of persistent capacity saturation


class TargetType(str, Enum):
    """Target entity classification defined in PR #16."""
    ACTIVITY = "activity"
    TRANSITION = "transition"
    WORKSTATION = "workstation"


class BottleneckTarget(ContractModel):
    """Unambiguous analytical target for a detector finding."""

    target_type: TargetType = Field(
        ...,
        description="Target type: activity, transition, or workstation",
    )
    target_name: str = Field(
        min_length=1,
        description="Activity name, destination activity, or workstation name",
    )
    source_activity: str | None = Field(
        default=None,
        min_length=1,
        description="Source activity for a directed transition",
    )
    station_id: str | None = Field(
        default=None,
        min_length=1,
        description="Explicitly mapped workstation identifier",
    )

    @model_validator(mode="after")
    def validate_target(self) -> "BottleneckTarget":
        if self.target_type == TargetType.TRANSITION:
            if not self.source_activity:
                raise ValueError(
                    "source_activity is required for transition targets"
                )
            if self.station_id is not None:
                raise ValueError(
                    "station_id is not allowed for transition targets"
                )

        elif self.target_type == TargetType.WORKSTATION:
            if not self.station_id:
                raise ValueError(
                    "station_id is required for workstation targets"
                )
            if self.source_activity is not None:
                raise ValueError(
                    "source_activity is not allowed for workstation targets"
                )

        elif self.target_type == TargetType.ACTIVITY:
            if self.source_activity is not None:
                raise ValueError(
                    "source_activity is not allowed for activity targets"
                )
            if self.station_id is not None:
                raise ValueError(
                    "station_id is not allowed for activity targets"
                )

        return self


# =====================================================================
# PR #15 & PR #16: METRICS, CAPABILITIES & PROVENANCE
# =====================================================================

class MetricStatus(str, Enum):
    MEASURED = "measured"
    DERIVED = "derived"
    ESTIMATED = "estimated"
    UNAVAILABLE = "unavailable"


class TimeSemantics(str, Enum):
    COMPLETION_ONLY = "completion_only"
    START_AND_COMPLETE = "start_and_complete"
    NOT_APPLICABLE = "not_applicable"
    UNKNOWN = "unknown"


class EventLogFormat(str, Enum):
    CSV = "csv"
    XES = "xes"


class MetricProvenance(ContractModel):
    method: str = Field(min_length=1, description="Calculation method identifier (e.g., maximum_mean_gap)")
    evidence_category: EvidenceCategory = Field(default=EvidenceCategory.L1_DELAY_HOTSPOT)
    input_fields: list[str] = Field(default_factory=list, description="Log attributes consumed")
    algorithm_version: str | None = Field(default="0.1.0", description="Algorithm baseline version")
    evidence_refs: list[str] = Field(default_factory=list, description="Traceable evidence identifiers")


class ProcessKPI(ContractModel):
    metric: str = Field(min_length=1, description="Stable metric identifier")
    value: float | None = Field(default=None, allow_inf_nan=False, description="Numeric value; null when unavailable")
    unit: str = Field(min_length=1, description="Unit: seconds, hours, ratio, count")
    status: MetricStatus
    time_semantics: TimeSemantics
    sample_size: int = Field(ge=0, description="Observations count")
    provenance: MetricProvenance
    unavailable_reason: str | None = Field(default=None, description="Mandatory when status=unavailable")

    @model_validator(mode="after")
    def validate_availability(self) -> "ProcessKPI":
        if self.status == MetricStatus.UNAVAILABLE:
            if self.value is not None:
                raise ValueError("value must be null when status is 'unavailable'")
            if not self.unavailable_reason:
                raise ValueError("unavailable_reason is required when status is 'unavailable'")
        elif self.value is None:
            raise ValueError("value must be provided unless status is 'unavailable'")
        return self


class CapabilityStatus(str, Enum):
    AVAILABLE = "available"
    PARTIAL = "partial"
    UNAVAILABLE = "unavailable"


class CapabilityAssessment(ContractModel):
    status: CapabilityStatus
    reason: str | None = Field(default=None, description="Explanation when partial or unavailable")

    @model_validator(mode="after")
    def explain_unavailable(self) -> "CapabilityAssessment":
        if self.status == CapabilityStatus.UNAVAILABLE and not self.reason:
            raise ValueError("reason is required when capability status is 'unavailable'")
        return self


class CapabilityReport(ContractModel):
    process_discovery: CapabilityAssessment
    kpi_calculation: CapabilityAssessment
    bottleneck_detection: CapabilityAssessment
    resource_analysis: CapabilityAssessment
    bpmn_export: CapabilityAssessment
    simulation: CapabilityAssessment


# =====================================================================
# CANDIDATE BOTTLENECK (PR #16 COMPLIANT)
# =====================================================================

class BottleneckSeverity(str, Enum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"


class CandidateReviewStatus(str, Enum):
    PENDING = "pending"
    CONFIRMED = "confirmed"
    REJECTED = "rejected"


class RankingStatus(str, Enum):
    RANKED = "ranked"
    INSUFFICIENT_SUPPORT = "insufficient_support"
    NO_POSITIVE_SIGNAL = "no_positive_signal"
    UNAVAILABLE = "unavailable"


class SupportPolicy(ContractModel):
    """Explicit and versioned detector support configuration."""

    policy_version: str = Field(min_length=1)
    min_observations: int = Field(ge=1, default=3)
    min_distinct_cases: int = Field(ge=1, default=3)


class CoverageClass(str, Enum):
    FULL = "full"
    PARTIAL = "partial"
    UNKNOWN = "unknown"


class ObservationCoverage(ContractModel):
    eligible_count: int = Field(ge=0)
    total_count: int | None = Field(default=None, ge=0)
    ratio: float | None = Field(default=None, ge=0, le=1)
    coverage_class: CoverageClass

    @model_validator(mode="after")
    def validate_coverage(self) -> "ObservationCoverage":
        if self.total_count is None or self.total_count == 0:
            if self.total_count == 0 and self.eligible_count != 0:
                raise ValueError(
                    "Eligible count cannot exceed total count"
                )
            if self.ratio is not None:
                raise ValueError(
                    "Coverage ratio requires a positive denominator"
                )
            if self.coverage_class != CoverageClass.UNKNOWN:
                raise ValueError(
                    "Undefined coverage must be classified as unknown"
                )
            return self

        if self.eligible_count > self.total_count:
            raise ValueError(
                "Eligible count cannot exceed total count"
            )

        expected = self.eligible_count / self.total_count

        if self.ratio is None or not isclose(
            self.ratio, expected, rel_tol=1e-9, abs_tol=1e-12
        ):
            raise ValueError(
                "Coverage ratio must equal eligible_count / total_count"
            )

        expected_class = (
            CoverageClass.FULL
            if self.eligible_count == self.total_count
            else CoverageClass.PARTIAL
        )

        if self.coverage_class != expected_class:
            raise ValueError(
                "Coverage class is inconsistent with observation counts"
            )

        return self


class RankingGroup(ContractModel):
    group_id: str = Field(min_length=1)
    metric: str = Field(min_length=1)
    target_type: TargetType
    analytical_view_ref: str = Field(min_length=1)
    observation_window_ref: str = Field(min_length=1)
    coverage_class: CoverageClass


class CandidateBottleneck(ContractModel):
    candidate_id: str = Field(min_length=1)
    target: BottleneckTarget = Field(..., description="Target activity, transition or workstation (AL-06)")
    evidence_category: EvidenceCategory = Field(..., description="L1, L2 or L3 category per PR #16 (AL-05)")
    ranking_status: RankingStatus
    rank: int | None = Field(
        default=None,
        ge=1,
        description="Rank within a comparable group, when supported",
    )
    support_policy: SupportPolicy
    ranking_group: RankingGroup | None = None

    # Parametri di supporto minimo di PR #16 (almeno 3 osservazioni su 3 casi)
    observations_count: int = Field(ge=0, description="Total valid observations (min support: 3)")
    distinct_cases_count: int = Field(ge=0, description="Distinct cases affected (min support: 3)")
    observation_coverage: ObservationCoverage
    case_coverage_ratio: float | None = Field(
        default=None,
        ge=0.0,
        le=1.0,
        description="Affected-case ratio when independently established",
    )

    # Severità opzionale: non forzata se i dati non la supportano (PR #16)
    severity: BottleneckSeverity | None = Field(default=None, description="Optional severity classification")

    observed_gap_hours: float | None = Field(default=None, description="Mean observed inter-event gap in hours")
    waiting_time_hours: float | None = Field(default=None, description="Measured queue wait in hours (only for L2/L3)")
    evidence_refs: list[str] = Field(default_factory=list)
    review_status: CandidateReviewStatus = CandidateReviewStatus.PENDING

    @model_validator(mode="after")
    def validate_ranking_support(self) -> "CandidateBottleneck":
        n = self.observations_count
        c = self.distinct_cases_count

        if self.observation_coverage.eligible_count != n:
            raise ValueError(
                "Coverage eligible_count must match observations_count"
            )

        if self.ranking_status == RankingStatus.RANKED:
            if self.ranking_group is None:
                raise ValueError(
                    "Ranked findings require a ranking group"
                )

        if self.ranking_group is not None:
            if self.ranking_group.target_type != self.target.target_type:
                raise ValueError(
                    "Ranking group target type must match finding target"
                )
            if (
                self.ranking_group.coverage_class
                != self.observation_coverage.coverage_class
            ):
                raise ValueError(
                    "Ranking group coverage class must match finding coverage"
                )

        if c > n:
            raise ValueError(
                "distinct_cases_count cannot exceed observations_count"
            )

        if n > 0 and c == 0:
            raise ValueError(
                "Positive observations require at least one distinct case"
            )

        supported = (
            n >= self.support_policy.min_observations
            and c >= self.support_policy.min_distinct_cases
        )

        if self.ranking_status == RankingStatus.RANKED:
            if self.rank is None:
                raise ValueError(
                    "Rank is required for ranked findings"
                )
            if not supported:
                raise ValueError(
                    "Ranked findings require sufficient support"
                )
        elif self.rank is not None:
            raise ValueError(
                "Unranked findings must not carry a rank"
            )

        if self.ranking_status == RankingStatus.UNAVAILABLE:
            if n != 0 or c != 0:
                raise ValueError(
                    "Unavailable findings cannot have eligible observations"
                )

        elif self.ranking_status == RankingStatus.INSUFFICIENT_SUPPORT:
            if n == 0 or supported:
                raise ValueError(
                    "Insufficient support requires observations "
                    "below the configured threshold"
                )

        elif self.ranking_status == RankingStatus.NO_POSITIVE_SIGNAL:
            if not supported:
                raise ValueError(
                    "No-positive-signal findings require sufficient support"
                )

        return self


# =====================================================================
# PR #15 CANONICAL LOG METADATA & REVISION TRACKING
# =====================================================================

class SourceMetadata(ContractModel):
    format: EventLogFormat
    canonical_schema_version: str = Field(default="0.1.0", description="Canonical schema from PR #15")
    mapping_contract_version: str = Field(default="0.1.0", description="Mapping specification version")
    mapping_revision_id: str | None = Field(default=None, description="Traceable confirmed mapping reference")
    input_sha256: str = Field(pattern=r"^[a-fA-F0-9]{64}$", description="SHA-256 integrity hash")
    time_semantics: TimeSemantics
    source_log_version: str | None = None


class AIInterpretationType(str, Enum):
    HYPOTHESIS = "hypothesis"
    EXPLANATORY = "explanatory"
    LIMITATION = "limitation"


class AIInterpretation(ContractModel):
    interpretation_id: str = Field(min_length=1)
    target_ref: str | None = Field(default=None, description="Target candidate or metric ID interpreted")
    type: AIInterpretationType
    text: str = Field(min_length=1)
    evidence_refs: list[str] = Field(default_factory=list)
    model_name: str | None = None
    model_version: str | None = None
    prompt_version: str | None = None
    generated_at: datetime | None = None


class DatasetLimitation(ContractModel):
    code: str = Field(min_length=1, description="Limitation identifier (e.g., LIM-NO-START-TIMESTAMP)")
    description: str = Field(min_length=1)
    affected_capabilities: list[str] = Field(default_factory=list)


class SimulationStatus(str, Enum):
    NOT_RUN = "not_run"
    COMPLETED = "completed"
    FAILED = "failed"


class SimulationScenarioResult(ContractModel):
    scenario_id: str = Field(min_length=1)
    status: SimulationStatus
    assumptions: list[str] = Field(default_factory=list)
    outputs: list[ProcessKPI] = Field(default_factory=list)
    limitations: list[str] = Field(default_factory=list)


class PublicationState(str, Enum):
    INTERNAL_DRAFT = "internal_draft"
    APPROVED_FOR_PUBLICATION = "approved_for_publication"
    PUBLISHED = "published"


class AnalysisResultPayload(ContractModel):
    schema_version: Literal["0.2.0"] = "0.2.0"
    analysis_id: str = Field(min_length=1)
    timestamp: datetime
    publication_state: PublicationState = Field(default=PublicationState.INTERNAL_DRAFT)
    source: SourceMetadata
    capabilities: CapabilityReport
    kpis: list[ProcessKPI] = Field(default_factory=list)
    candidate_bottlenecks: list[CandidateBottleneck] = Field(default_factory=list)
    ai_interpretations: list[AIInterpretation] = Field(default_factory=list)
    simulated_scenarios: list[SimulationScenarioResult] = Field(default_factory=list)
    limitations: list[DatasetLimitation] = Field(default_factory=list)


class ApprovalRequest(ContractModel):
    candidate_id: str = Field(min_length=1)
    countermeasure_id: str = Field(min_length=1)
    workstation: str = Field(min_length=1)
    action: str = Field(min_length=1)
    supervisor_notes: str | None = None


class ApprovalResponse(ContractModel):
    approval_id: str
    analysis_id: str
    candidate_id: str
    countermeasure_id: str
    status: Literal["approved"]
    approver_id: str = Field(description="Derived from authenticated user context")
    approval_timestamp: datetime
    supervisor_notes: str | None = None


class PublishRequest(ContractModel):
    analysis_id: str = Field(min_length=1)
    authorized_consumers: list[str] = Field(default_factory=lambda: ["P06", "P20", "P17"])
    authorization_token: str = Field(min_length=1)


class PublishResponse(ContractModel):
    publication_id: str
    analysis_id: str
    status: Literal["published"]
    published_at: datetime
    consumers: list[str]


class ErrorDetail(ContractModel):
    field: str | None = None
    issue: str


class ErrorResponse(ContractModel):
    code: str
    message: str
    details: list[ErrorDetail] = Field(default_factory=list)
