from __future__ import annotations

from datetime import datetime, timezone
from enum import Enum
from math import isclose
from typing import Any, Literal

from pydantic import AwareDatetime, BaseModel, ConfigDict, Field, model_validator


class ContractModel(BaseModel):
    """Base model enforcing strict schema conformance and rejecting extra fields."""
    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)


# =====================================================================
# PR #16 ALIGNMENT: THREE EVIDENCE CATEGORIES & TARGETS
# =====================================================================

class EvidenceCategory(str, Enum):
    """Evidence hierarchy defined in PR #16 (docs/DETECTOR_BASELINE.md)."""
    L1_DELAY_HOTSPOT = "L1_delay_hotspot"              # Observed inter-event delay signal
    L2_QUEUE_CANDIDATE = "L2_queue_candidate"          # Evidence of correlated queue waiting
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


class SourceTimestampSemantics(str, Enum):
    """Meaning of timestamps in the source event log."""

    COMPLETION = "completion"
    START = "start"
    LIFECYCLE = "lifecycle"
    OTHER_OBSERVED = "other_observed"
    UNKNOWN = "unknown"


class TimeSemantics(str, Enum):
    """Meaning of an analytical temporal metric."""

    OBSERVED_INTER_EVENT_GAP = "observed_inter_event_gap"
    PROCESSING_DURATION = "processing_duration"
    QUEUE_WAITING_DURATION = "queue_waiting_duration"
    THROUGHPUT_DURATION = "throughput_duration"
    NOT_APPLICABLE = "not_applicable"
    UNKNOWN = "unknown"


TEMPORAL_METRIC_SEMANTICS = {
    "observed_transition_gap":
        TimeSemantics.OBSERVED_INTER_EVENT_GAP,
    "processing_time":
        TimeSemantics.PROCESSING_DURATION,
    "queue_waiting_time":
        TimeSemantics.QUEUE_WAITING_DURATION,
    "throughput_time":
        TimeSemantics.THROUGHPUT_DURATION,
}


class EventLogFormat(str, Enum):
    CSV = "csv"
    XES = "xes"


class MetricProvenance(ContractModel):
    method: str = Field(min_length=1, description="Calculation method identifier (e.g., maximum_mean_gap)")
    evidence_category: EvidenceCategory | None = Field(
        default=None,
        description="Evidence category, when applicable and established",
    )
    input_fields: list[str] = Field(default_factory=list, description="Log attributes consumed")
    algorithm_version: str | None = Field(
        default=None,
        min_length=1,
        description="Version of the algorithm actually used",
    )
    evidence_refs: list[str] = Field(default_factory=list, description="Traceable evidence identifiers")


class ProcessKPI(ContractModel):
    metric: str = Field(min_length=1, description="Stable metric identifier")
    value: float | None = Field(default=None, allow_inf_nan=False, description="Numeric value; null when unavailable")
    unit: str = Field(min_length=1, description="Metric unit; temporal durations use seconds")
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
            raise ValueError(
                "value must be provided unless status is unavailable"
            )
        elif self.unavailable_reason is not None:
            raise ValueError(
                "Available metrics must not carry an unavailable reason"
            )

        expected_semantics = TEMPORAL_METRIC_SEMANTICS.get(
            self.metric
        )

        if (
            expected_semantics is not None
            and self.time_semantics != expected_semantics
        ):
            raise ValueError(
                "Metric identifier and temporal semantics are inconsistent"
            )

        temporal_semantics = {
            TimeSemantics.OBSERVED_INTER_EVENT_GAP,
            TimeSemantics.PROCESSING_DURATION,
            TimeSemantics.QUEUE_WAITING_DURATION,
            TimeSemantics.THROUGHPUT_DURATION,
        }

        if self.time_semantics in temporal_semantics:
            if self.unit != "seconds":
                raise ValueError(
                    "Temporal duration metrics must use seconds"
                )

            if self.value is not None and self.value < 0:
                raise ValueError(
                    "Temporal durations cannot be negative"
                )

            if (
                self.status in {
                    MetricStatus.MEASURED,
                    MetricStatus.DERIVED,
                }
                and self.sample_size == 0
            ):
                raise ValueError(
                    "Observed or derived durations require observations"
                )

        return self


class CapabilityStatus(str, Enum):
    AVAILABLE = "available"
    PARTIAL = "partial"
    UNAVAILABLE = "unavailable"


class CapabilityAssessment(ContractModel):
    status: CapabilityStatus
    reason: str | None = Field(default=None, description="Explanation when partial or unavailable")
    runtime_implemented: bool = Field(description="Whether the capability is implemented, independently of data eligibility")

    @model_validator(mode="after")
    def explain_unavailable(self) -> "CapabilityAssessment":
        if self.status != CapabilityStatus.AVAILABLE and not self.reason:
            raise ValueError("reason is required for partial or unavailable capabilities")
        return self


class CapabilityReport(ContractModel):
    process_discovery: CapabilityAssessment
    kpi_calculation: CapabilityAssessment
    bottleneck_detection: CapabilityAssessment
    observed_inter_event_gaps: CapabilityAssessment
    processing_durations: CapabilityAssessment
    queue_waiting_durations: CapabilityAssessment
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
    statistic: Literal["mean"] = "mean"
    unit: Literal["seconds"] = "seconds"


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

    # Configurable minimum support (proposed DB-04).
    observations_count: int = Field(ge=0, description="Total eligible observations")
    distinct_cases_count: int = Field(ge=0, description="Distinct cases contributing eligible observations")
    observation_coverage: ObservationCoverage
    affected_cases_count: int | None = Field(default=None, ge=0)
    total_cases_count: int | None = Field(default=None, ge=1)
    case_coverage_ratio: float | None = Field(
        default=None,
        ge=0.0,
        le=1.0,
        description="Affected-case ratio when independently established",
    )

    # Optional severity; never inferred solely from evidence category.
    severity: BottleneckSeverity | None = Field(default=None, description="Optional severity classification")

    primary_metric: ProcessKPI = Field(description="Mean duration used for ranking; null value if unavailable")
    median_seconds: float | None = Field(default=None, ge=0, allow_inf_nan=False)
    maximum_seconds: float | None = Field(default=None, ge=0, allow_inf_nan=False)
    positive_wait_fraction: float | None = Field(default=None, ge=0, le=1, allow_inf_nan=False)
    analytical_view_ref: str = Field(min_length=1)
    observation_window_ref: str = Field(min_length=1)
    detector_rule_ref: str = Field(min_length=1)
    detector_config_ref: str = Field(min_length=1)
    limitations: list[str] = Field(default_factory=list)
    evidence_refs: list[str] = Field(default_factory=list)
    review_status: CandidateReviewStatus = CandidateReviewStatus.PENDING

    @model_validator(mode="after")
    def validate_ranking_support(self) -> "CandidateBottleneck":
        n = self.observations_count
        c = self.distinct_cases_count
        if self.case_coverage_ratio is not None:
            if self.affected_cases_count is None or self.total_cases_count is None:
                raise ValueError("Affected-case ratio requires explicit counts")
            if self.affected_cases_count > self.total_cases_count or not isclose(self.case_coverage_ratio, self.affected_cases_count / self.total_cases_count):
                raise ValueError("Inconsistent affected-case ratio")
        if self.affected_cases_count is not None and self.affected_cases_count > c:
            raise ValueError("Affected cases cannot exceed contributing cases")
        if self.total_cases_count is not None and c > self.total_cases_count:
            raise ValueError("Contributing cases cannot exceed total cases")
        metric = self.primary_metric
        if self.evidence_category == EvidenceCategory.L3_CAPACITY_HYPOTHESIS:
            raise ValueError("L3 is reserved; no reviewed capacity inference rule is implemented in this baseline")
        expected = (
            "observed_transition_gap" if self.evidence_category == EvidenceCategory.L1_DELAY_HOTSPOT
            else "queue_waiting_time"
        )
        if metric.metric != expected:
            raise ValueError("Primary metric must match evidence category")
        if metric.provenance.evidence_category != self.evidence_category:
            raise ValueError("Metric provenance must match finding evidence category")
        if self.evidence_category == EvidenceCategory.L1_DELAY_HOTSPOT and self.target.target_type != TargetType.TRANSITION:
            raise ValueError("L1 requires a directed transition")
        if self.evidence_category == EvidenceCategory.L2_QUEUE_CANDIDATE and self.target.target_type == TargetType.TRANSITION:
            raise ValueError("L2 requires an activity or mapped workstation")
        if metric.sample_size != n:
            raise ValueError("Metric sample size must match eligible observations")
        if metric.status == MetricStatus.ESTIMATED:
            raise ValueError("Estimated values cannot support deterministic findings")
        if self.ranking_status == RankingStatus.UNAVAILABLE:
            if metric.status != MetricStatus.UNAVAILABLE:
                raise ValueError("Unavailable finding requires unavailable metric")
        elif metric.status not in {MetricStatus.MEASURED, MetricStatus.DERIVED}:
            raise ValueError("Finding requires observed or derived metric")
        if self.ranking_status == RankingStatus.RANKED and (metric.value is None or metric.value <= 0):
            raise ValueError("Ranked finding requires positive mean duration")
        if self.ranking_status == RankingStatus.NO_POSITIVE_SIGNAL and metric.value != 0:
            raise ValueError("No-positive-signal finding requires observed zero mean")
        if n == 0 and any(v is not None for v in (self.median_seconds, self.maximum_seconds, self.positive_wait_fraction)):
            raise ValueError("Unavailable findings cannot carry observed statistics")
        if self.maximum_seconds is not None and (metric.value > self.maximum_seconds or (self.median_seconds is not None and self.median_seconds > self.maximum_seconds)):
            raise ValueError("Maximum cannot be below mean or median")
        if expected == "queue_waiting_time" and n > 0:
            if self.positive_wait_fraction is None:
                raise ValueError("Queue evidence requires positive-wait fraction")
            if (metric.value == 0) != (self.positive_wait_fraction == 0):
                raise ValueError("Positive-wait fraction contradicts mean")
        elif self.positive_wait_fraction is not None:
            raise ValueError("Positive-wait fraction applies only to observed queue waits")
        if self.ranking_group is not None:
            if (self.ranking_group.metric != metric.metric or
                self.ranking_group.analytical_view_ref != self.analytical_view_ref or
                self.ranking_group.observation_window_ref != self.observation_window_ref):
                raise ValueError("Ranking group must match metric, view and window")

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

class DatasetIdentity(ContractModel):
    dataset_id: str = Field(min_length=1)
    input_sha256: str = Field(pattern=r"^[a-fA-F0-9]{64}$")


class DatasetProfile(DatasetIdentity):
    format: EventLogFormat
    profile_ref: str = Field(min_length=1)
    attributes: list[str] = Field(description="Minimized structural attributes; no raw event values")


class MappingRevision(DatasetIdentity):
    mapping_id: str = Field(min_length=1)
    mapping_version: int = Field(ge=1)
    mapping_contract_version: str = Field(min_length=1)


class MappingProposal(MappingRevision):
    status: Literal["proposed"]
    mapping_document_ref: str = Field(min_length=1, description="Stored TASK-03 mapping document without trusted approval")


class MappingConfirmation(MappingRevision):
    status: Literal["confirmed"]
    approval_ref: str = Field(min_length=1)
    actor_ref: str = Field(min_length=1)
    confirmed_at: AwareDatetime


class AnalysisRequest(MappingRevision):
    approval_ref: str = Field(min_length=1, description="Server must verify exact mapping revision and input hash against trusted human approval")
    ingestion_authorization_ref: str = Field(min_length=1, description="Separate trusted ingestion authorization")


class SourceMetadata(ContractModel):
    format: EventLogFormat
    canonical_schema_version: str = Field(min_length=1)
    confirmed_mapping: MappingConfirmation
    source_timestamp_semantics: SourceTimestampSemantics
    case_notion: str = Field(min_length=1)
    normalized_timezone: Literal["UTC"]
    quality_report_ref: str = Field(min_length=1)
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


class AnalysisExecutionStatus(str, Enum):
    COMPLETED = "completed"
    FAILED = "failed"


class EvidenceRecord(ContractModel):
    evidence_id: str = Field(min_length=1)
    description: str = Field(min_length=1)
    artifact_ref: str = Field(min_length=1, description="Authorized deterministic artifact reference; not raw event data")


class AnalysisResultPayload(ContractModel):
    schema_version: Literal["0.2.0"] = "0.2.0"
    analysis_id: str = Field(min_length=1)
    timestamp: AwareDatetime
    result_revision: str = Field(min_length=1)
    execution_status: AnalysisExecutionStatus
    evidence: list[EvidenceRecord] = Field(default_factory=list)
    publication_state: PublicationState = Field(default=PublicationState.INTERNAL_DRAFT)
    source: SourceMetadata
    capabilities: CapabilityReport
    kpis: list[ProcessKPI] = Field(default_factory=list)
    candidate_bottlenecks: list[CandidateBottleneck] = Field(default_factory=list)
    ai_interpretations: list[AIInterpretation] = Field(default_factory=list)
    simulated_scenarios: list[SimulationScenarioResult] = Field(default_factory=list)
    limitations: list[DatasetLimitation] = Field(default_factory=list)

    @model_validator(mode="after")
    def validate_result(self) -> "AnalysisResultPayload":
        if self.execution_status != AnalysisExecutionStatus.COMPLETED:
            if self.publication_state != PublicationState.INTERNAL_DRAFT or self.candidate_bottlenecks or self.kpis:
                raise ValueError("Failed analysis cannot expose completed results or be published")
        ids = {item.evidence_id for item in self.evidence}
        if len(ids) != len(self.evidence):
            raise ValueError("Duplicate evidence identifiers")
        refs = set()
        for item in self.kpis:
            refs.update(item.provenance.evidence_refs)
        for item in self.candidate_bottlenecks:
            refs.update(item.evidence_refs)
            refs.update(item.primary_metric.provenance.evidence_refs)
        for item in self.ai_interpretations:
            refs.update(item.evidence_refs)
        if not refs <= ids:
            raise ValueError("Evidence references must resolve within the result revision")
        return self


class ApprovalRequest(ContractModel):
    result_revision: str = Field(min_length=1)
    candidate_id: str = Field(min_length=1)
    countermeasure_id: str = Field(min_length=1)
    workstation: str = Field(min_length=1)
    action: str = Field(min_length=1)
    supervisor_notes: str | None = None


class ApprovalResponse(ContractModel):
    approval_id: str
    analysis_id: str
    result_revision: str
    candidate_id: str
    countermeasure_id: str
    status: Literal["approved"]
    approver_id: str = Field(description="Derived from authenticated user context")
    approval_timestamp: datetime
    supervisor_notes: str | None = None


class PublishRequest(ContractModel):
    result_revision: str = Field(min_length=1)
    authorized_consumers: list[Literal["P06", "P20", "P17", "P21"]] = Field(min_length=1)
    publication_approval_ref: str = Field(min_length=1, description="Trusted human decision bound to path analysis ID, exact revision and selected consumers")

    @model_validator(mode="after")
    def unique_consumers(self) -> "PublishRequest":
        if len(set(self.authorized_consumers)) != len(self.authorized_consumers):
            raise ValueError("Consumers must be unique")
        return self


class PublishResponse(ContractModel):
    publication_id: str
    analysis_id: str
    result_revision: str
    publication_approval_ref: str
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
