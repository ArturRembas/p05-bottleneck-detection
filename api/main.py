from __future__ import annotations

import logging
from pathlib import Path
from typing import Any

from fastapi import FastAPI, File, Query, Request, UploadFile
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse, Response
from starlette.exceptions import HTTPException as StarletteHTTPException

from .schemas import (
    AnalysisResultPayload,
    AnalysisRequest,
    DatasetProfile,
    MappingProposal,
    MappingConfirmation,
    MappingRevision,
    ApprovalRequest,
    ApprovalResponse,
    CandidateBottleneck,
    ErrorDetail,
    ErrorResponse,
    ProcessKPI,
    PublishRequest,
    PublishResponse,
)

API_PREFIX = "/api/v1"
MAX_UPLOAD_BYTES = 50 * 1024 * 1024
ALLOWED_EXTENSIONS = {".csv", ".xes"}

logger = logging.getLogger("p05_api")

app = FastAPI(
    title="P05 — Bottleneck Detection in Processes API",
    description="API for P05 — Bottleneck Detection in Processes | AI Puzzle Framework",
    version="0.2.0",
)

app.openapi_version = "3.1.0"


class APIError(Exception):
    def __init__(self, status_code: int, code: str, message: str, details: list[ErrorDetail] | None = None):
        self.status_code = status_code
        self.payload = ErrorResponse(code=code, message=message, details=details or [])


@app.exception_handler(APIError)
async def api_error_handler(_: Request, exc: APIError) -> JSONResponse:
    return JSONResponse(status_code=exc.status_code, content=exc.payload.model_dump(mode="json"))


@app.exception_handler(RequestValidationError)
async def request_validation_handler(_: Request, exc: RequestValidationError) -> JSONResponse:
    details = []
    for error in exc.errors():
        location = ".".join(str(part) for part in error.get("loc", ()) if part not in {"body", "query", "path"})
        details.append(ErrorDetail(field=location or None, issue=str(error.get("msg", "Invalid value"))))
    payload = ErrorResponse(
        code="VALIDATION_ERROR",
        message="The request does not satisfy the API contract.",
        details=details,
    )
    return JSONResponse(status_code=422, content=payload.model_dump(mode="json"))


@app.exception_handler(Exception)
async def unexpected_error_handler(_: Request, exc: Exception) -> JSONResponse:
    logger.exception("Unhandled API exception", exc_info=exc)
    payload = ErrorResponse(code="INTERNAL_ERROR", message="An unexpected server error occurred.")
    return JSONResponse(status_code=500, content=payload.model_dump(mode="json"))


@app.exception_handler(StarletteHTTPException)
async def http_error_handler(_: Request, exc: StarletteHTTPException) -> JSONResponse:
    known = {
        404: ("NOT_FOUND", "The requested resource was not found."),
        405: ("METHOD_NOT_ALLOWED", "The HTTP method is not allowed for this resource."),
    }
    code, message = known.get(exc.status_code, ("HTTP_ERROR", str(exc.detail)))
    payload = ErrorResponse(code=code, message=message)
    return JSONResponse(status_code=exc.status_code, content=payload.model_dump(mode="json"))


ERROR_RESPONSES: dict[int, dict[str, Any]] = {
    404: {"model": ErrorResponse, "description": "Analysis or requested resource not found"},
    409: {"model": ErrorResponse, "description": "Operation conflicts with current resource state"},
    413: {"model": ErrorResponse, "description": "Uploaded file exceeds configured size limit"},
    415: {"model": ErrorResponse, "description": "Unsupported event-log format"},
    422: {"model": ErrorResponse, "description": "Request validation error"},
    500: {"model": ErrorResponse, "description": "Unexpected internal error"},
    501: {"model": ErrorResponse, "description": "Application service is not implemented yet"},
}


# --- DATASET OPERATIONS (AL-03, PR #15) ---

@app.post(
    f"{API_PREFIX}/datasets/upload",
    response_model=DatasetProfile,
    operation_id="upload_dataset",
    summary="Upload dataset and generate structural profile",
    responses={413: ERROR_RESPONSES[413], 415: ERROR_RESPONSES[415], 422: ERROR_RESPONSES[422], 501: ERROR_RESPONSES[501]},
    tags=["Dataset Ingestion"],
)
async def upload_dataset(
    file: UploadFile = File(..., description="Event log in CSV or XES format")
) -> Any:
    suffix = Path(file.filename or "").suffix.lower()
    if suffix not in ALLOWED_EXTENSIONS:
        raise APIError(415, "UNSUPPORTED_LOG_FORMAT", "Only .csv and .xes event logs are accepted.")
    content = await file.read(MAX_UPLOAD_BYTES + 1)
    if len(content) > MAX_UPLOAD_BYTES:
        raise APIError(413, "FILE_TOO_LARGE", f"The upload exceeds the {MAX_UPLOAD_BYTES}-byte limit.")
    if not content:
        raise APIError(422, "EMPTY_FILE", "The uploaded event log is empty.")

    raise APIError(501, "DATASET_SERVICE_NOT_IMPLEMENTED", "Staged dataset profiling service pending integration.")


# Mapping documents remain owned by TASK-03. These are reference-based
# boundaries; server-side storage, validation and authorization are deferred.
@app.post(
    f"{API_PREFIX}/datasets/{{dataset_id}}/mapping/propose",
    response_model=MappingProposal,
    operation_id="propose_semantic_mapping",
    description="Manual or AI-assisted proposal service; AI may use only authorized minimized profiles. No automatic confirmation.",
    responses={422: ERROR_RESPONSES[422], 501: ERROR_RESPONSES[501]},
)
async def propose_mapping(dataset_id: str, mapping_document_ref: str = Query(..., min_length=1)) -> MappingProposal:
    raise APIError(501, "MAPPING_SERVICE_NOT_IMPLEMENTED", "Mapping proposal service pending integration.")


@app.post(
    f"{API_PREFIX}/datasets/{{dataset_id}}/mapping/confirm",
    response_model=MappingConfirmation,
    operation_id="confirm_semantic_mapping",
    description="Requires authenticated human confirmation of exact input hash and mapping revision. Never authorizes ingestion implicitly.",
    responses={409: ERROR_RESPONSES[409], 422: ERROR_RESPONSES[422], 501: ERROR_RESPONSES[501]},
)
async def confirm_mapping(dataset_id: str, request: MappingRevision) -> MappingConfirmation:
    if dataset_id != request.dataset_id:
        raise APIError(409, "DATASET_ID_MISMATCH", "Path and body dataset identifiers differ.")
    raise APIError(501, "MAPPING_CONFIRMATION_NOT_IMPLEMENTED", "Trusted confirmation service pending integration.")


@app.post(
    f"{API_PREFIX}/analyses",
    response_model=AnalysisResultPayload,
    operation_id="create_analysis",
    summary="Create analysis from confirmed mapping",
    description="Server must verify exact dataset hash, mapping revision, trusted human confirmation and separate ingestion authorization before execution.",
    responses={409: ERROR_RESPONSES[409], 422: ERROR_RESPONSES[422], 500: ERROR_RESPONSES[500], 501: ERROR_RESPONSES[501]},
    tags=["Analysis ingestion and processing"],
)
async def create_analysis(request: AnalysisRequest) -> AnalysisResultPayload:
    raise APIError(501, "ANALYSIS_ENGINE_NOT_IMPLEMENTED", "Confirmed ingestion and deterministic analysis pending integration.")


# --- INTEROPERABILITY & RESULTS (AL-05, AL-06, AL-07, PR #16) ---

@app.get(
    f"{API_PREFIX}/analyses/{{analysis_id}}/bottlenecks",
    response_model=list[CandidateBottleneck],
    operation_id="get_candidate_bottlenecks",
    summary="Get candidate bottlenecks",
    responses={404: ERROR_RESPONSES[404], 422: ERROR_RESPONSES[422], 500: ERROR_RESPONSES[500], 501: ERROR_RESPONSES[501]},
    description="Internal authorized retrieval only; external consumers require a separate published revision interface.",
    tags=["Interoperability P06 / P20"],
)
async def get_bottlenecks(analysis_id: str) -> list[CandidateBottleneck]:
    _ = analysis_id
    raise APIError(501, "ANALYSIS_REPOSITORY_NOT_IMPLEMENTED", "Analysis result retrieval is not implemented yet.")


@app.get(
    f"{API_PREFIX}/analyses/{{analysis_id}}/kpis",
    response_model=list[ProcessKPI],
    operation_id="get_process_kpis",
    summary="Get process KPIs",
    responses={404: ERROR_RESPONSES[404], 422: ERROR_RESPONSES[422], 500: ERROR_RESPONSES[500], 501: ERROR_RESPONSES[501]},
    description="Internal authorized retrieval only; external consumers require a separate published revision interface.",
    tags=["Interoperability P17"],
)
async def get_process_kpis(analysis_id: str) -> list[ProcessKPI]:
    _ = analysis_id
    raise APIError(501, "ANALYSIS_REPOSITORY_NOT_IMPLEMENTED", "Analysis result retrieval is not implemented yet.")


@app.get(
    f"{API_PREFIX}/analyses/{{analysis_id}}/full-report",
    response_model=AnalysisResultPayload,
    operation_id="get_full_analysis_report",
    summary="Get the full analysis report",
    responses={404: ERROR_RESPONSES[404], 422: ERROR_RESPONSES[422], 500: ERROR_RESPONSES[500], 501: ERROR_RESPONSES[501]},
    tags=["Full analysis result"],
)
async def get_full_analysis(analysis_id: str) -> AnalysisResultPayload:
    _ = analysis_id
    raise APIError(501, "ANALYSIS_REPOSITORY_NOT_IMPLEMENTED", "Analysis result retrieval is not implemented yet.")


# --- GOVERNANCE & EXTERNAL PUBLICATION (AL-12) ---

@app.post(
    f"{API_PREFIX}/analyses/{{analysis_id}}/countermeasures/approve",
    response_model=ApprovalResponse,
    operation_id="approve_countermeasure",
    summary="Approve a countermeasure (Human Gate)",
    responses={404: ERROR_RESPONSES[404], 409: ERROR_RESPONSES[409], 422: ERROR_RESPONSES[422], 500: ERROR_RESPONSES[500], 501: ERROR_RESPONSES[501]},
    tags=["Human oversight"],
)
async def approve_countermeasure(analysis_id: str, request: ApprovalRequest) -> ApprovalResponse:
    _ = (analysis_id, request)
    raise APIError(
        501,
        "APPROVAL_SERVICE_NOT_IMPLEMENTED",
        "Approval is disabled until authentication, authorization and durable audit logging are implemented.",
    )


@app.post(
    f"{API_PREFIX}/analyses/{{analysis_id}}/publish",
    response_model=PublishResponse,
    operation_id="publish_analysis_results",
    summary="Publish an explicitly approved result revision",
    description="Server must verify trusted human approval for the path analysis ID, exact result revision and explicit consumer set. No client reference grants authorization by itself.",
    responses={404: ERROR_RESPONSES[404], 409: ERROR_RESPONSES[409], 422: ERROR_RESPONSES[422], 500: ERROR_RESPONSES[500], 501: ERROR_RESPONSES[501]},
    tags=["External Publication"],
)
async def publish_results(analysis_id: str, request: PublishRequest) -> PublishResponse:
    _ = (analysis_id, request)
    raise APIError(
        501,
        "PUBLICATION_SERVICE_NOT_IMPLEMENTED",
        "External publication requires human confirmation gate and partner agreement.",
    )


@app.get(
    f"{API_PREFIX}/analyses/{{analysis_id}}/export-bpmn",
    response_class=Response,
    operation_id="export_bpmn_xml",
    summary="Export the discovered process as BPMN XML",
    responses={
        200: {
            "description": "BPMN 2.0 XML document",
            "content": {"application/xml": {"schema": {"type": "string", "format": "binary"}}},
        },
        404: ERROR_RESPONSES[404],
        422: ERROR_RESPONSES[422],
        500: ERROR_RESPONSES[500],
        501: ERROR_RESPONSES[501],
    },
    tags=["Export and interoperability P21"],
)
async def export_bpmn(analysis_id: str) -> Response:
    _ = analysis_id
    raise APIError(501, "BPMN_EXPORT_NOT_IMPLEMENTED", "BPMN discovery/export is not implemented yet.")


@app.get("/health", operation_id="get_health_status", tags=["Technical"])
async def health() -> dict[str, str]:
    return {"status": "ok", "component": "p05-contract-scaffold"}
