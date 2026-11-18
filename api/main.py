from datetime import datetime
from enum import Enum
import io
from typing import Any, Dict, List, Optional
from fastapi import FastAPI, File, HTTPException, Query, Response, UploadFile
from pydantic import BaseModel, Field

app = FastAPI(
    title="P05 — Bottleneck Detection in Processes API",
    description="Componente del framework AI Puzzle. Espone contratti OpenAPI 3.1 per l'analisi di colli di bottiglia, vincoli di capacità e KPI di processo.",
    version="0.2.0",
)

# ==========================================
# MODELLI DATI RIGOROSI (SRS v0.2 § 7.1)
# ==========================================


class MetricStatus(str, Enum):
    MEASURED = "measured"
    DERIVED = "derived"
    ESTIMATED = "estimated"
    UNAVAILABLE = "unavailable"


class BottleneckSeverity(str, Enum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"


class ValidationStatus(str, Enum):
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"


class TimeSemantics(str, Enum):
    COMPLETION_ONLY = "completion_only"
    START_AND_COMPLETE = "start_and_complete"


# Metrica di performance tipizzata (D13)
class ProcessKPI(BaseModel):
    metric: str = Field(
        ...,
        description="Identificativo metrica (es. observed_transition_gap, throughput_time)",
    )
    value: float = Field(..., description="Valore numerico calcolato")
    unit: str = Field(..., description="Unità di misura (min, hours, ratio)")
    status: MetricStatus = Field(
        ...,
        description="Stato di affidabilità del dato secondo i campi disponibili",
    )
    sample_size: int = Field(
        ..., description="Numero di casi/eventi su cui è calcolata"
    )


# Rilevamento candidato collo di bottiglia (D14)
class CandidateBottleneck(BaseModel):
    activity: str = Field(
        ..., description="Nome della stazione o fase di processo"
    )
    rank: int = Field(
        ..., description="Posizione nella graduatoria di congestione (1 = peggiore)"
    )
    method: str = Field(
        default="statistical_inter_event_gap",
        description="Metodo algoritmico applicato",
    )
    severity: BottleneckSeverity = Field(
        ..., description="Livello di criticità stimato"
    )
    waiting_time_hours: float = Field(
        ..., description="Tempo medio di intervallo/attesa in ore"
    )
    evidence_refs: List[str] = Field(
        default_factory=list,
        description="Riferimenti tracciabili agli ID KPI o run",
    )
    validation: ValidationStatus = Field(
        default=ValidationStatus.PENDING,
        description="Stato del gate di Human Oversight",
    )


# Interpretazione Cognitiva dell'AI (UC04 / UC09) - Rigorosamente separata!
class AIInterpretation(BaseModel):
    type: str = Field(
        default="hypothesis",
        description="Tipo di asserzione: hypothesis, explanatory, limitation",
    )
    text: str = Field(
        ..., description="Spiegazione contestuale o contromisura proposta"
    )
    evidence_refs: List[str] = Field(
        default_factory=list,
        description="Riferimenti a metriche deterministiche certe",
    )


# Payload Ufficiale di Risposta di Analisi (SRS § 7.1)
class AnalysisResultPayload(BaseModel):
    schema_version: str = "draft-0.2"
    analysis_id: str = Field(
        ..., description="Identificativo univoco della sessione di analisi"
    )
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    source: Dict[str, Any] = Field(
        ...,
        description="Metadati del log (versione, hash sorgente, semantica temporale)",
    )
    capabilities: Dict[str, bool] = Field(
        ...,
        description="Capability consentite dal log (process_discovery, service_duration, queue_length)",
    )
    kpis: List[ProcessKPI] = Field(
        default_factory=list, description="Lista dei KPI misurati o derivati"
    )
    candidate_bottlenecks: List[CandidateBottleneck] = Field(
        default_factory=list,
        description="Candidati colli di bottiglia identificati dal core deterministico",
    )
    ai_interpretations: List[AIInterpretation] = Field(
        default_factory=list,
        description="Ipotesi dell'AI e contromisure suggerite",
    )
    simulated_scenarios: List[Dict[str, Any]] = Field(
        default_factory=list,
        description="Esiti di eventuali simulazioni what-if SimPy",
    )
    limitations: List[str] = Field(
        default_factory=list,
        description="Disclaimer e vincoli sui dati non inferibili",
    )


# ==========================================
# ENDPOINT REST CONFORMI AD OPENAPI 3.1
# ==========================================


@app.get(
    "/api/v1/analyses/{analysis_id}/bottlenecks",
    response_model=List[CandidateBottleneck],
    tags=["Interoperability P06 / P20"],
)
def get_bottlenecks(analysis_id: str = "run-demo-001"):
    """Fornisce l'elenco ordinato delle stazioni critiche e dei colli di

    bottiglia candidati ai moduli a valle: P06 (Schedulazione) e P20 (Risorse).
    """
    return [
        CandidateBottleneck(
            activity="CNC_Milling",
            rank=1,
            method="inter_activity_gap_p75",
            severity=BottleneckSeverity.CRITICAL,
            waiting_time_hours=4.8,
            evidence_refs=["kpi-001", "trace-sample-50"],
            validation=ValidationStatus.APPROVED,
        ),
        CandidateBottleneck(
            activity="Welding",
            rank=2,
            method="inter_activity_gap_p75",
            severity=BottleneckSeverity.MEDIUM,
            waiting_time_hours=2.1,
            evidence_refs=["kpi-002"],
            validation=ValidationStatus.PENDING,
        ),
    ]


@app.get(
    "/api/v1/analyses/{analysis_id}/kpis",
    response_model=List[ProcessKPI],
    tags=["Interoperability P17"],
)
def get_process_kpis(analysis_id: str = "run-demo-001"):
    """Esporta i KPI globali di processo (tempo di throughput, intervalli di

    transizione) a beneficio del modulo P17 (Data Analytics).
    """
    return [
        ProcessKPI(
            metric="observed_transition_gap",
            value=12.4,
            unit="min",
            status=MetricStatus.DERIVED,
            sample_size=50,
        ),
        ProcessKPI(
            metric="mean_throughput_time",
            value=42.6,
            unit="hours",
            status=MetricStatus.DERIVED,
            sample_size=50,
        ),
        ProcessKPI(
            metric="service_duration",
            value=0.0,
            unit="hours",
            status=MetricStatus.UNAVAILABLE,
            sample_size=50,
        ),
    ]


@app.get(
    "/api/v1/analyses/{analysis_id}/full-report",
    response_model=AnalysisResultPayload,
    tags=["Full Analysis Result"],
)
def get_full_analysis(analysis_id: str = "run-demo-001"):
    """Restituisce il payload strutturato completo dell'analisi conforme alla

    Sezione 7.1 della SRS v0.2.
    """
    return AnalysisResultPayload(
        analysis_id=analysis_id,
        source={
            "log_version": "log-v1",
            "input_hash": "sha256:e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855",
            "time_semantics": TimeSemantics.COMPLETION_ONLY,
        },
        capabilities={
            "process_discovery": True,
            "service_duration": False,
            "queue_length": False,
        },
        kpis=[
            ProcessKPI(
                metric="observed_transition_gap",
                value=12.4,
                unit="min",
                status=MetricStatus.DERIVED,
                sample_size=50,
            )
        ],
        candidate_bottlenecks=[
            CandidateBottleneck(
                activity="CNC_Milling",
                rank=1,
                method="versioned_rule_gap",
                severity=BottleneckSeverity.CRITICAL,
                waiting_time_hours=4.8,
                evidence_refs=["kpi-001"],
                validation=ValidationStatus.APPROVED,
            )
        ],
        ai_interpretations=[
            AIInterpretation(
                type="hypothesis",
                text="Verificare la disponibilità di operatori fresatori nel turno serale.",
                evidence_refs=["kpi-001"],
            )
        ],
        simulated_scenarios=[],
        limitations=[
            "Log a timestamp singolo: gli intervalli tra eventi non costituiscono prova diretta di coda fisica stazionaria."
        ],
    )


@app.post(
    "/api/v1/countermeasures/approve",
    tags=["Human-in-the-Loop Governance (D24/UC11)"],
)
def approve_countermeasure(
    analysis_id: str = Query(..., description="ID dell'analisi"),
    workstation: str = Query(..., description="Stazione approvata"),
    action: str = Query(..., description="Azione convalidata"),
):
    """Registra la convalida esplicita dell'analista umano (HITL Gate).

    Nessuna raccomandazione operativa viene notificata a P06/P20 senza questa
    approvazione.
    """
    return {
        "status": "APPROVED",
        "analysis_id": analysis_id,
        "workstation": workstation,
        "action": action,
        "approval_timestamp": datetime.utcnow().isoformat(),
        "notified_partners": ["P06_Scheduling", "P20_Resource_Allocation"],
    }


@app.get(
    "/api/v1/analyses/{analysis_id}/export-bpmn",
    tags=["Export & Interoperability P21"],
)
def export_bpmn(analysis_id: str = "run-demo-001"):
    """Esporta il modello formale di processo scoperto in formato standard BPMN

    2.0 XML per P21 (What-If).
    """
    mock_bpmn_xml = '<?xml version="1.0" encoding="UTF-8"?><bpmn:definitions xmlns:bpmn="http://www.omg.org/spec/BPMN/20100524/MODEL" ...></bpmn:definitions>'
    return Response(content=mock_bpmn_xml, media_type="application/xml")
