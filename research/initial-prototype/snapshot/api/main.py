import io
import pandas as pd
from fastapi import FastAPI, UploadFile, File
from fastapi.responses import Response
from pydantic import BaseModel
from typing import List

app = FastAPI(
    title="P05 — Bottleneck Detection API",
    description="Microservizio per il rilevamento colli di bottiglia e vincoli di capacità per P06 e P20.",
    version="1.0.0",
)


class BottleneckMetric(BaseModel):
    workstation: str
    average_waiting_time_hours: float
    rework_percentage: float
    severity: str
    queue_length_estimated: int
    suggested_countermeasure: str


class ProcessKPIs(BaseModel):
    total_cases_analyzed: int
    mean_throughput_time_hours: float
    non_value_added_time_ratio: float


@app.get("/api/v1/bottlenecks", response_model=List[BottleneckMetric])
def get_bottlenecks():
    return [
        {
            "workstation": "CNC_Milling",
            "average_waiting_time_hours": 4.8,
            "rework_percentage": 14.5,
            "severity": "CRITICAL",
            "queue_length_estimated": 35,
            "suggested_countermeasure": "Riallocare 1 risorsa o ridurre lotto in ingresso.",
        },
        {
            "workstation": "Welding",
            "average_waiting_time_hours": 2.1,
            "rework_percentage": 5.2,
            "severity": "MEDIUM",
            "queue_length_estimated": 12,
            "suggested_countermeasure": "Nessuna azione urgente richiesta.",
        },
    ]


@app.get("/api/v1/metrics", response_model=ProcessKPIs)
def get_kpis():
    return {
        "total_cases_analyzed": 225,
        "mean_throughput_time_hours": 42.6,
        "non_value_added_time_ratio": 0.38,
    }


# ORA LEGGE DAVVERO IL FILE CARICATO!
@app.post("/api/v1/process/upload")
async def upload_log(file: UploadFile = File(...)):
    contents = await file.read()
    df = pd.read_csv(io.BytesIO(contents))
    return {
        "filename": file.filename,
        "total_rows": len(df),
        "columns": list(df.columns),
        "status": "Log caricato e profilato con successo dall'API!",
    }


@app.get("/api/v1/process/export-bpmn")
def export_bpmn():
    mock_bpmn_xml = (
        '<?xml version="1.0" encoding="UTF-8"?><definitions ...></definitions>'
    )
    return Response(content=mock_bpmn_xml, media_type="application/xml")


@app.post("/api/v1/countermeasures/approve")
def approve_countermeasure(workstation: str, action: str):
    return {
        "status": "APPROVED",
        "workstation": workstation,
        "action": action,
        "notified_services": ["P06_Scheduling", "P20_Resource_Allocation"],
    }
