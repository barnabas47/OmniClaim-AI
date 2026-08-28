"""
OmniClaim AI Backend FastAPI Application.
Exposes REST APIs for Strands Agents SDK execution, METAR weather bluff disprovals, Multimodal OCR Vision upload, HITL approvals, and telemetry.
"""
import os
import json
import logging
import time
from typing import Dict, Any, Optional
from fastapi import FastAPI, HTTPException, Body, File, UploadFile, Form
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from backend.agents.concierge_orchestrator import OmniClaimOrchestrator
from backend.tools.receipt_vision_parser import parse_receipt_or_boarding_pass

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(name)s: %(message)s")
logger = logging.getLogger("OmniClaim.API")

app = FastAPI(
    title="OmniClaim AI Autonomous Flight Passenger Rights API",
    description="Backend API powered by Strands Agents SDK, Multimodal OCR Vision Ingestion, and Amazon Bedrock AgentCore architecture.",
    version="1.1.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

orchestrator = OmniClaimOrchestrator()

DECISION_STORE: Dict[str, Dict[str, Any]] = {}
AUDIT_LOGS: list = []

class FlightProcessRequest(BaseModel):
    flight_number: str
    passenger_name: Optional[str] = "Alex Morgan"
    pnr_code: Optional[str] = "PNR-89210"
    flight_date: Optional[str] = "2026-08-22"
    receipts_amount_eur: Optional[float] = 65.0

class DocumentUploadRequest(BaseModel):
    raw_ocr_text: str
    filename: Optional[str] = "boarding_pass_photo.jpg"

class DecisionApprovalRequest(BaseModel):
    decision_id: str
    approval_action: str = "APPROVED"
    user_notes: Optional[str] = None

@app.get("/")
def read_root():
    return {
        "system": "OmniClaim AI Flight Passenger Rights Concierge",
        "framework": "Strands Agents SDK + Vision OCR Parser",
        "aws_deployment": "Amazon Bedrock AgentCore Architecture",
        "status": "ONLINE"
    }

@app.get("/api/health")
def health_check():
    return {
        "status": "HEALTHY",
        "agentcore_ready": True,
        "active_agents": ["FlightMonitorAgent", "BluffDisproverAgent", "LegalRightsAgent", "ClaimFilerAgent"],
        "vision_ocr_engine": "OPERATIONAL",
        "strands_sdk": "OPERATIONAL"
    }

@app.get("/api/sample-flights")
def get_sample_flights():
    return [
        {
            "id": "sample-flight-1",
            "flight_number": "LH401",
            "carrier": "Lufthansa German Airlines",
            "route": "Frankfurt (FRA) -> New York JFK (JFK)",
            "delay": "4h 15m (255 mins)",
            "airline_excuse": "Severe Weather & ATC Restriction",
            "expected_verdict": "BLUFF DISPROVED via Frankfurt METAR VFR clear weather logs. Total Claim: €665.00 (€600 statutory + €65 meal receipt).",
            "pnr_code": "PNR-LH992"
        },
        {
            "id": "sample-flight-2",
            "flight_number": "FR8821",
            "carrier": "Ryanair DAC",
            "route": "London Stansted (STN) -> Barcelona (BCN)",
            "delay": "3h 40m (220 mins)",
            "airline_excuse": "Operational Crew Rest Overtime",
            "expected_verdict": "Operational fault admitted. Total Claim: €315.00 (€250 statutory + €65 meal receipt).",
            "pnr_code": "PNR-FR331"
        },
        {
            "id": "sample-flight-3",
            "flight_number": "W62310",
            "carrier": "Wizz Air Hungary",
            "route": "Budapest (BUD) -> London Luton (LTN)",
            "delay": "4h 20m (260 mins)",
            "airline_excuse": "Technical Aircraft Defect",
            "expected_verdict": "Technical defect is carrier responsibility. Total Claim: €465.00 (€400 statutory + €65 meal receipt).",
            "pnr_code": "PNR-WZ401"
        }
    ]

@app.post("/api/pipeline/process-flight")
def process_flight(req: FlightProcessRequest):
    try:
        result = orchestrator.process_flight_compensation_pipeline(
            flight_number=req.flight_number,
            passenger_name=req.passenger_name,
            pnr_code=req.pnr_code,
            flight_date=req.flight_date,
            receipts_amount_eur=req.receipts_amount_eur or 65.0
        )

        if result.get("requires_human_action") and "decision_package" in result:
            dec = result["decision_package"]
            DECISION_STORE[dec["decision_id"]] = dec

        AUDIT_LOGS.append({
            "event": "FLIGHT_PROCESSED",
            "flight_number": req.flight_number,
            "pipeline_status": result.get("pipeline_status"),
            "summary": result.get("summary")
        })

        return result
    except Exception as e:
        logger.error(f"Error processing flight pipeline: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/pipeline/upload-document")
def upload_and_process_document(req: DocumentUploadRequest):
    """
    Multimodal Vision Ingestion Endpoint:
    Parses uploaded boarding pass / receipt text via Vision OCR, extracts metadata,
    and automatically executes the Strands multi-agent pipeline!
    """
    try:
        raw_vision_json = parse_receipt_or_boarding_pass(
            document_text=req.raw_ocr_text,
            filename=req.filename or "uploaded_ticket.jpg"
        )
        vision_data = json.loads(raw_vision_json)["vision_ocr_extracted"]

        result = orchestrator.process_flight_compensation_pipeline(
            flight_number=vision_data["flight_number"],
            passenger_name=vision_data["passenger_name"],
            pnr_code=vision_data["pnr_code"],
            receipts_amount_eur=vision_data["incurred_expense_receipt_eur"]
        )

        if result.get("requires_human_action") and "decision_package" in result:
            dec = result["decision_package"]
            DECISION_STORE[dec["decision_id"]] = dec

        result["vision_ocr_extraction"] = vision_data

        AUDIT_LOGS.append({
            "event": "VISION_DOCUMENT_PROCESSED",
            "filename": req.filename,
            "extracted_flight": vision_data["flight_number"],
            "pipeline_status": result.get("pipeline_status")
        })

        return result
    except Exception as e:
        logger.error(f"Error processing vision upload: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/decisions")
def get_pending_decisions():
    return list(DECISION_STORE.values())

@app.post("/api/pipeline/approve-decision")
def approve_decision(req: DecisionApprovalRequest):
    if req.decision_id not in DECISION_STORE:
        raise HTTPException(status_code=404, detail=f"Decision ID '{req.decision_id}' not found.")

    dec = DECISION_STORE[req.decision_id]
    dec["approval_state"] = req.approval_action
    dec["user_notes"] = req.user_notes
    dec["action_executed_at"] = time.strftime("%Y-%m-%d %H:%M:%S")

    AUDIT_LOGS.append({
        "event": f"DECISION_{req.approval_action}",
        "decision_id": req.decision_id,
        "flight_number": dec.get("flight_info", {}).get("flight_number"),
        "compensation_eur": dec.get("compensation", {}).get("amount_eur")
    })

    return {
        "status": "SUCCESS",
        "message": f"Action '{req.approval_action}' executed successfully for Decision {req.decision_id}.",
        "updated_decision": dec
    }

@app.get("/api/audit-logs")
def get_audit_logs():
    return AUDIT_LOGS

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
