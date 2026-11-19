from __future__ import annotations

from datetime import datetime
from enum import Enum
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, model_validator


class ContractModel(BaseModel):
    """Base class: reject undocumented fields to keep the API contract strict."""

    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)


class MetricStatus(str, Enum):
    MEASURED = "measured"
    DERIVED = "derived"
    ESTIMATED = "estimated"
    UNAVAILABLE = "unavailable"


class TimeSemantics(str, Enum):
    """Meaning of timestamps used by a temporal metric.

    completion_only means timestamps represent event/activity completion only;
    it does not establish activity start time, processing duration, or queue time.
    """

    COMPLETION_ONLY = "completion_only"
    START_AND_COMPLETE = "start_and_complete"
    NOT_APPLICABLE = "not_applicable"
    UNKNOWN = "unknown"


class EventLogFormat(str, Enum):
    CSV = "csv"
    XES = "xes"


class MetricProvenance(ContractModel):
    method: str = Field(min_length=1, description="Calculation method or algorithm identifier")
    input_fields: list[str] = Field(
        default_factory=list,
        description="Input event-log attributes used by the calculation",
    )
    algorithm_version: str | None = Field(
        default=None, description="Algorithm/version identifier when available"
    )
    evidence_refs: list[str] = Field(
        default_factory=list,
        description="References to evidence records or intermediate calculations",
    )


class ProcessKPI(ContractModel):
    metric: str = Field(min_length=1, description="Stable metric identifier")
    value: float | None = Field(
        default=None,
        allow_inf_nan=False,
        description="Numeric value; null when status is unavailable",
    )
    unit: str = Field(min_length=1, description="Unit, for example seconds, hours, ratio, or count")
    status: MetricStatus
    time_semantics: TimeSemantics = Field(
        description="Temporal interpretation of the input data used for this KPI"
    )
    sample_size: int = Field(ge=0, description="Number of observations used")
    provenance: MetricProvenance
    unavailable_reason: str | None = Field(
        default=None,
        description="Required when status=unavailable; explains why the value cannot be computed",
    )

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
    reason: str | None = Field(default=None, description="Explanation of partial/unavailable capability")

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


class SourceMetadata(ContractModel):
    format: EventLogFormat
    input_sha256: str = Field(pattern=r"^[a-fA-F0-9]{64}$")
    time_semantics: TimeSemantics
    case_id_column: str | None = None
    activity_column: str | None = None
    timestamp_column: str | None = None
    source_log_version: str | None = None


class AnalysisStatus(str, Enum):
    COMPLETED = "completed"
    COMPLETED_WITH_LIMITATIONS = "completed_with_limitations"


class BottleneckSeverity(str, Enum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"


class CandidateReviewStatus(str, Enum):
    PENDING = "pending"
    CONFIRMED = "confirmed"
    REJECTED = "rejected"


class CandidateBottleneck(ContractModel):
    candidate_id: str = Field(min_length=1)
    activity: str = Field(min_length=1, description="Activity or process step associated with the candidate")
    rank: int = Field(ge=1, description="Relative ranking; 1 indicates the highest priority")
    method: str = Field(min_length=1, description="Deterministic detection method identifier")
    severity: BottleneckSeverity
    waiting_time: ProcessKPI | None = Field(
        default=None,
        description=(
            "Waiting-time KPI, if assessed. If assessed but not computable, provide a ProcessKPI "
            "with status=unavailable rather than inventing a numeric value."
        ),
    )
    evidence_refs: list[str] = Field(default_factory=list)
    review_status: CandidateReviewStatus = CandidateReviewStatus.PENDING


class AIInterpretationType(str, Enum):
    HYPOTHESIS = "hypothesis"
    EXPLANATORY = "explanatory"
    LIMITATION = "limitation"


class AIInterpretation(ContractModel):
    interpretation_id: str = Field(min_length=1)
    type: AIInterpretationType
    text: str = Field(min_length=1)
    evidence_refs: list[str] = Field(default_factory=list)
    model_name: str | None = None
    model_version: str | None = None
    prompt_version: str | None = None
    generated_at: datetime | None = None


class DatasetLimitation(ContractModel):
    code: str = Field(min_length=1, description="Stable limitation identifier")
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


class AnalysisResultPayload(ContractModel):
    schema_version: Literal["0.2.0"] = "0.2.0"
    analysis_id: str = Field(min_length=1)
    timestamp: datetime
    status: AnalysisStatus
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
    approver_id: str = Field(
        description="Must be populated from the authenticated user context, never trusted from client input"
    )
    approval_timestamp: datetime
    supervisor_notes: str | None = None


class ErrorDetail(ContractModel):
    field: str | None = None
    issue: str


class ErrorResponse(ContractModel):
    code: str
    message: str
    details: list[ErrorDetail] = Field(default_factory=list)
