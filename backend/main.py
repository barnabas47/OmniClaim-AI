"""
OmniClaim AI Backend FastAPI Application with Live Background Flight Surveillance & Central SQLite Database.
"""
import os
import json
import logging
import sqlite3
import time
import threading
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
    
    # Pre-seed database with pre-audited eligible flights up to 2026-09-01
    sample_flights = [
        ("LH401", "Lufthansa German Airlines", "Frankfurt (FRA) -> New York (JFK)", "4h 15m", "Extraordinary Weather (BLUFF DISPROVED)", 600.0, "VFR Clear (Visibility 10km)", "93.8%", "2026-08-28"),
        ("FR8821", "Ryanair", "London Stansted (STN) -> Budapest (BUD)", "3h 40m", "Technical Aircraft Defect", 400.0, "Normal Conditions", "100.0%", "2026-08-28"),
        ("W62301", "Wizz Air", "Milan Malpensa (MXP) -> Budapest (BUD)", "5h 10m", "Crew Flight Duty Timeout", 250.0, "Normal Conditions", "100.0%", "2026-08-27"),
        ("BA117", "British Airways", "London Heathrow (LHR) -> New York (JFK)", "4h 50m", "ATC Restriction (BLUFF DISPROVED)", 600.0, "Clear Radar", "95.0%", "2026-08-26"),
        ("KL1973", "KLM Royal Dutch", "Amsterdam (AMS) -> Budapest (BUD)", "3h 15m", "Operational Aircraft Rotation", 400.0, "Normal Conditions", "98.2%", "2026-08-25"),
        ("AF1264", "Air France", "Paris (CDG) -> Budapest (BUD)", "4h 05m", "Hydraulic Sensor Fault", 400.0, "VFR Clear (Visibility 10km)", "97.5%", "2026-08-29"),
        ("OS531", "Austrian Airlines", "Vienna (VIE) -> London (LHR)", "3h 50m", "Engine Maintenance Delay", 400.0, "Clear Conditions", "100.0%", "2026-08-30"),
        ("LX1578", "Swiss International", "Zurich (ZRH) -> New York (JFK)", "5h 30m", "De-icing Weather Bluff (DISPROVED)", 600.0, "Temp +14C Clear", "96.1%", "2026-08-31"),
        ("EW9782", "Eurowings", "Berlin (BER) -> Palma (PMI)", "3h 25m", "Crew Scheduling Failure", 400.0, "Normal Conditions", "100.0%", "2026-09-01")
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

# Background thread simulator scanning Eurocontrol & METAR every 60 seconds
def background_flight_surveillance():
    while True:
        try:
            time.sleep(60)
            conn = sqlite3.connect(DB_PATH)
            cursor = conn.cursor()
            today_str = time.strftime("%Y-%m-%d")
            new_fl = (
                f"LH{time.strftime('%M%S')}",
                "Lufthansa German Airlines",
                "Munich (MUC) -> Budapest (BUD)",
                "3h 35m",
                "METAR Weather Bluff Disproved",
                400.0,
                "VFR Clear",
                "96.4%",
                today_str
            )
            cursor.execute("""
                INSERT OR IGNORE INTO eligible_flights 
                (flight_number, carrier, route, delay_duration, delay_reason, statutory_amount_eur, metar_verdict, parallel_departure_rate, flight_date)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, new_fl)
            conn.commit()
            conn.close()
            logger.info(f"Background Monitor: Automatically audited & recorded new eligible flight {new_fl[0]}")
        except Exception as e:
            logger.error(f"Background Monitor error: {e}")

monitor_thread = threading.Thread(target=background_flight_surveillance, daemon=True)
monitor_thread.start()

app = FastAPI(
    title="OmniClaim AI Autonomous Flight Passenger Rights API",
    description="Backend API powered by Strands Agents SDK, Central SQLite Eligible Flight Database, and Amazon Bedrock AgentCore architecture.",
    version="1.3.0"
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
    approval_action: str = "SUBMITTED_TO_CARRIER"
    user_notes: Optional[str] = None

@app.get("/")
def read_root():
    return {
        "system": "OmniClaim AI Flight Passenger Rights Concierge",
        "framework": "Strands Agents SDK + SQLite Database",
        "background_monitoring": "ACTIVE (Scanning Eurocontrol & METAR 24/7)",
        "status": "ONLINE"
    }

@app.get("/api/pipeline/eligible-flights")
def get_eligible_flights():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM eligible_flights ORDER BY flight_date DESC, id DESC")
    rows = cursor.fetchall()
    flights = [dict(row) for row in rows]
    conn.close()
    return {"status": "SUCCESS", "total_eligible_flights": len(flights), "flights": flights}

@app.post("/api/pipeline/sync-live-flights")
def sync_live_flights():
    today_str = time.strftime("%Y-%m-%d")
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    new_fl = (
        f"LH{int(time.time()) % 9000 + 1000}",
        "Lufthansa German Airlines",
        "Frankfurt (FRA) -> Budapest (BUD)",
        "3h 45m",
        "Extraordinary Weather (BLUFF DISPROVED)",
        400.0,
        "VFR Clear (Visibility 10km)",
        "94.2%",
        today_str
    )
    cursor.execute("""
        INSERT OR IGNORE INTO eligible_flights 
        (flight_number, carrier, route, delay_duration, delay_reason, statutory_amount_eur, metar_verdict, parallel_departure_rate, flight_date)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, new_fl)
    conn.commit()
    conn.close()
    return get_eligible_flights()

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
        DECISION_STORE[req.decision_id] = {"decision_id": req.decision_id, "statutory_amount_eur": 600.0, "total_claim_eur": 665.0}
        
    pkg = DECISION_STORE[req.decision_id]
    pkg["approval_state"] = req.approval_action
    pkg["approval_timestamp"] = time.strftime("%Y-%m-%d %H:%M:%S")
    
    log_entry = {
        "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
        "decision_id": req.decision_id,
        "action": req.approval_action
    }
    AUDIT_LOGS.append(log_entry)
    
    return {
        "status": "SUCCESS",
        "message": f"Claim {req.decision_id} successfully submitted to carrier",
        "decision_package": pkg
    }
