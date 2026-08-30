"""
OmniClaim AI Backend FastAPI Application with Central Eligible Flights Database.
Exposes REST APIs for Strands Agents SDK execution, METAR weather bluff disprovals, Multimodal OCR Vision upload, HITL approvals, and Central Database queries.
"""
import os
import json
import logging
import sqlite3
import time
from typing import Dict, Any, Optional, List
from fastapi import FastAPI, HTTPException, Body, File, UploadFile, Form
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from backend.agents.concierge_orchestrator import OmniClaimOrchestrator
from backend.tools.receipt_vision_parser import parse_receipt_or_boarding_pass

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(name)s: %(message)s")
logger = logging.getLogger("OmniClaim.API")

DB_PATH = os.path.join(os.path.dirname(__file__), "omniclaim.db")

def init_db():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS eligible_flights (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            flight_number TEXT UNIQUE,
            carrier TEXT,
            route TEXT,
            delay_duration TEXT,
            delay_reason TEXT,
            statutory_amount_eur REAL,
            metar_verdict TEXT,
            parallel_departure_rate TEXT,
            flight_date TEXT
        )
    """)
    
    # Pre-seed database with pre-audited eligible flights
    sample_flights = [
        ("LH401", "Lufthansa German Airlines", "Frankfurt (FRA) -> New York (JFK)", "4h 15m", "Extraordinary Weather (BLUFF DISPROVED)", 600.0, "VFR Clear (Visibility 10000m)", "93.8%", "2026-08-28"),
        ("FR8821", "Ryanair", "London Stansted (STN) -> Budapest (BUD)", "3h 40m", "Technical Aircraft Defect", 400.0, "Normal Conditions", "100.0%", "2026-08-28"),
        ("W62301", "Wizz Air", "Milan Malpensa (MXP) -> Budapest (BUD)", "5h 10m", "Crew Flight Duty Timeout", 250.0, "Normal Conditions", "100.0%", "2026-08-27"),
        ("BA117", "British Airways", "London Heathrow (LHR) -> New York (JFK)", "4h 50m", "ATC Restriction (BLUFF DISPROVED)", 600.0, "Clear Radar", "95.0%", "2026-08-26"),
        ("KL1973", "KLM Royal Dutch", "Amsterdam (AMS) -> Budapest (BUD)", "3h 15m", "Operational Aircraft Rotation", 400.0, "Normal Conditions", "98.2%", "2026-08-25")
    ]
    
    for fl in sample_flights:
        try:
            cursor.execute("""
                INSERT OR IGNORE INTO eligible_flights 
                (flight_number, carrier, route, delay_duration, delay_reason, statutory_amount_eur, metar_verdict, parallel_departure_rate, flight_date)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, fl)
        except Exception:
            pass
            
    conn.commit()
    conn.close()

init_db()

app = FastAPI(
    title="OmniClaim AI Autonomous Flight Passenger Rights API",
    description="Backend API powered by Strands Agents SDK, Central SQLite Eligible Flight Database, and Amazon Bedrock AgentCore architecture.",
    version="1.2.0"
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
        "framework": "Strands Agents SDK + SQLite Database",
        "aws_deployment": "Amazon Bedrock AgentCore Architecture",
        "status": "ONLINE"
    }

@app.get("/api/pipeline/eligible-flights")
def get_eligible_flights():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM eligible_flights ORDER BY id DESC")
    rows = cursor.fetchall()
    flights = [dict(row) for row in rows]
    conn.close()
    return {"status": "SUCCESS", "total_eligible_flights": len(flights), "flights": flights}

@app.get("/api/pipeline/flight-scenarios")
def get_flight_scenarios():
    return get_eligible_flights()

@app.post("/api/pipeline/select-flight")
def select_eligible_flight(flight_number: str = Body(..., embed=True), passenger_name: str = Body("Alex Morgan", embed=True)):
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM eligible_flights WHERE flight_number = ?", (flight_number,))
    row = cursor.fetchone()
    conn.close()

    if not row:
        raise HTTPException(status_code=404, detail="Flight not found in central database")

    fl = dict(row)
    decision_id = f"CLM-2026-{fl['flight_number']}-992"
    claim_package = {
        "decision_id": decision_id,
        "passenger_name": passenger_name,
        "pnr_code": "PNR-LH992",
        "flight_number": fl["flight_number"],
        "carrier": fl["carrier"],
        "route": fl["route"],
        "delay_duration": fl["delay_duration"],
        "delay_reason": fl["delay_reason"],
        "statutory_amount_eur": fl["statutory_amount_eur"],
        "receipts_amount_eur": 65.0,
        "total_claim_eur": fl["statutory_amount_eur"] + 65.0,
        "metar_verdict": fl["metar_verdict"],
        "parallel_departure_rate": fl["parallel_departure_rate"],
        "approval_state": "PENDING_APPROVAL"
    }
    DECISION_STORE[decision_id] = claim_package
    return {"status": "SUCCESS", "claim": claim_package}

@app.post("/api/pipeline/upload-document")
def upload_document(req: DocumentUploadRequest):
    extracted_text = req.raw_ocr_text
    parsed_info = parse_receipt_or_boarding_pass(extracted_text)
    
    flight_number = parsed_info.get("flight_number") or "LH401"
    res = orchestrator.process_flight_compensation_pipeline(
        flight_number=flight_number,
        passenger_name=parsed_info.get("passenger_name") or "Alex Morgan",
        pnr_code=parsed_info.get("pnr_code") or "PNR-LH992",
        flight_date="2026-08-22",
        receipts_amount_eur=parsed_info.get("receipt_amount_eur") or 65.0
    )
    
    decision_pkg = res["decision_package"]
    DECISION_STORE[decision_pkg["decision_id"]] = decision_pkg
    
    return {
        "status": "SUCCESS",
        "extracted_ocr": parsed_info,
        "decision_package": decision_pkg,
        "telemetry_logs": res["telemetry_logs"]
    }

@app.post("/api/pipeline/approve-decision")
def approve_decision(req: DecisionApprovalRequest):
    if req.decision_id not in DECISION_STORE:
        raise HTTPException(status_code=404, detail="Decision ID not found")
        
    pkg = DECISION_STORE[req.decision_id]
    pkg["approval_state"] = req.approval_action
    pkg["approval_timestamp"] = time.strftime("%Y-%m-%d %H:%M:%S")
    
    log_entry = {
        "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
        "decision_id": req.decision_id,
        "action": req.approval_action,
        "statutory_amount": pkg.get("statutory_amount_eur"),
        "total_claim": pkg.get("total_claim_eur") or (pkg.get("statutory_amount_eur", 600) + pkg.get("receipts_amount_eur", 65))
    }
    AUDIT_LOGS.append(log_entry)
    
    return {
        "status": "SUCCESS",
        "message": f"Claim {req.decision_id} successfully updated to {req.approval_action}",
        "decision_package": pkg
    }
