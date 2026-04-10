from __future__ import annotations

import json
from pathlib import Path
from typing import Any, List

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, EmailStr, Field

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"
OUTPUT_DIR = BASE_DIR / "output"
PROMPT_FILE = BASE_DIR / "prompts" / "incident_reasoning_prompt.md"

app = FastAPI(title="Incident Reasoning Agent", version="0.1.0")


class Reporter(BaseModel):
    name: str
    email: EmailStr


class IncidentRequest(BaseModel):
    incident_id: str = Field(..., examples=["INC-1001"])
    title: str
    description: str
    service: str
    environment: str
    severity: str
    reporter: Reporter
    attachments: List[str] = []
    observed_at: str


class RootCauseHypothesis(BaseModel):
    cause: str
    confidence: float


class IncidentResponse(BaseModel):
    summary: str
    observable_signals: List[str]
    possible_root_causes: List[RootCauseHypothesis]
    recommended_actions: List[str]
    ticket_summary: str


def load_json(path: Path) -> dict[str, Any]:
    if not path.exists():
        raise FileNotFoundError(f"Missing file: {path.name}")
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def load_prompt() -> str:
    return PROMPT_FILE.read_text(encoding="utf-8")


def mock_reasoning_engine(incident: IncidentRequest, log_data: dict[str, Any]) -> IncidentResponse:
    messages = [signal.get("message", "") for signal in log_data.get("signals", [])]
    observable_signals = [message for message in messages if message]

    lowered_text = " ".join(observable_signals).lower()

    if "timeout" in lowered_text:
        causes = [
            RootCauseHypothesis(cause="Misconfigured timeout or retry policy in payment path", confidence=0.78),
            RootCauseHypothesis(cause="Network latency spike between checkout and payment service", confidence=0.58),
            RootCauseHypothesis(cause="Downstream dependency degradation in payment service", confidence=0.43),
        ]
        actions = [
            "Review timeout and retry configuration for payment authorization",
            "Check latency metrics between checkout-service and payment-service",
            "Validate whether payment-service showed degraded response times in the same window",
        ]
        summary = "Checkout flow shows timeout behavior when waiting for payment authorization."
    elif "missing" in lowered_text or "validation" in lowered_text:
        causes = [
            RootCauseHypothesis(cause="Required field missing in downstream fulfillment payload", confidence=0.84),
            RootCauseHypothesis(cause="Schema drift between orchestrator contract and fulfillment gateway", confidence=0.66),
            RootCauseHypothesis(cause="Payload mapping regression introduced in recent code change", confidence=0.49),
        ]
        actions = [
            "Compare payload schema sent by order-orchestrator against downstream contract",
            "Validate field mapping for customerSegment and related optional attributes",
            "Review recent code changes in request transformation layer",
        ]
        summary = "Order orchestration flow is failing due to a likely downstream payload validation issue."
    else:
        causes = [
            RootCauseHypothesis(cause="Production configuration mismatch after deployment", confidence=0.81),
            RootCauseHypothesis(cause="Incorrect database endpoint configured for production environment", confidence=0.73),
            RootCauseHypothesis(cause="Service startup completed with outdated environment variables", confidence=0.45),
        ]
        actions = [
            "Compare production environment variables against approved release configuration",
            "Verify database host and connectivity from the affected service",
            "Confirm whether deployment propagated the latest configuration values",
        ]
        summary = "Catalog synchronization is failing due to a likely production configuration mismatch."

    ticket_summary = (
        f"{incident.incident_id} | {incident.service} | {incident.environment} | "
        f"{summary} Primary hypothesis: {causes[0].cause}."
    )

    return IncidentResponse(
        summary=summary,
        observable_signals=observable_signals,
        possible_root_causes=causes,
        recommended_actions=actions,
        ticket_summary=ticket_summary,
    )


@app.get("/")
def root() -> dict[str, str]:
    return {
        "message": "Incident Reasoning Agent is running.",
        "prompt_loaded": "yes" if PROMPT_FILE.exists() else "no",
    }


@app.get("/prompt")
def prompt_preview() -> dict[str, str]:
    return {"prompt": load_prompt()}


@app.post("/incident", response_model=IncidentResponse)
def investigate_incident(incident: IncidentRequest) -> IncidentResponse:
    service_map = {
        "checkout-service": DATA_DIR / "sample_logs_checkout.json",
        "order-orchestrator": DATA_DIR / "sample_logs_payload.json",
        "catalog-sync": DATA_DIR / "sample_logs_config.json",
    }

    log_file = service_map.get(incident.service)
    if not log_file:
        raise HTTPException(status_code=404, detail="No mock logs mapped for this service")

    log_data = load_json(log_file)
    response = mock_reasoning_engine(incident, log_data)

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    output_path = OUTPUT_DIR / f"ticket_{incident.incident_id}.json"
    output_path.write_text(response.model_dump_json(indent=2), encoding="utf-8")

    return response


@app.get("/samples")
def list_samples() -> dict[str, list[str]]:
    return {
        "incidents": sorted([path.name for path in DATA_DIR.glob("sample_incident_*.json")]),
        "logs": sorted([path.name for path in DATA_DIR.glob("sample_logs_*.json")]),
    }
