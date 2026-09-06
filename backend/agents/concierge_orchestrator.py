"""
OmniClaimOrchestrator - Master Strands Multi-Agent Orchestrator for OmniClaim AI.
"""
import json
import logging
import time
from typing import Dict, Any, List, Optional

from backend.agents.flight_monitor_agent import FlightMonitorAgent
from backend.agents.bluff_disprover_agent import BluffDisproverAgent
from backend.agents.legal_rights_agent import LegalRightsAgent
from backend.agents.claim_filer_agent import ClaimFilerAgent

logger = logging.getLogger("OmniClaim.Orchestrator")

class OmniClaimOrchestrator:
    """
    Master Strands Agent Orchestrator for OmniClaim AI.
    Coordinates flight monitoring, METAR weather bluff disproval, geodesic distance math,
    legal entitlement mapping, pre-filled carrier form generation, and HITL decision cards.
    """
    def __init__(self, model_provider=None):
        self.model_provider = model_provider
        self.flight_agent = FlightMonitorAgent(model_provider=model_provider)
        self.bluff_agent = BluffDisproverAgent(model_provider=model_provider)
        self.legal_agent = LegalRightsAgent(model_provider=model_provider)
        self.filer_agent = ClaimFilerAgent(model_provider=model_provider)

    def process_flight_compensation_pipeline(
        self,
        flight_number: str,
        passenger_name: str = "",
        pnr_code: str = "",
        flight_date: str = "2026-08-22",
        receipts_amount_eur: float = 65.0
    ) -> Dict[str, Any]:
        start_time = time.time()
        telemetry_logs = []

        def log_step(agent_name: str, status: str, message: str, elapsed_ms: float):
            telemetry_logs.append({
                "timestamp": time.strftime("%H:%M:%S"),
                "agent": agent_name,
                "status": status,
                "message": message,
                "elapsed_ms": round(elapsed_ms, 2)
            })

        # Step 1: Flight Surveillance & Delay Pre-check
        t0 = time.time()
        flight_res = self.flight_agent.run(flight_number=flight_number, flight_date=flight_date)
        log_step(
            self.flight_agent.agent_name,
            "SUCCESS",
            flight_res["reasoning"],
            (time.time() - t0) * 1000
        )

        fl = flight_res["data"]["flight"]
        delay_mins = fl["delay_minutes"]
        qualifies = flight_res["data"]["eligibility_precheck"]["qualifies_for_eu261_threshold"]

        if not qualifies:
            total_duration = (time.time() - start_time) * 1000
            return {
                "pipeline_status": "COMPLETED_QUIET",
                "requires_human_action": False,
                "summary": f"Flight {fl['flight_number']} delay ({delay_mins} min) is under the 3-hour EU261 statutory threshold. Quiet audit logged.",
                "flight_monitor": flight_res,
                "telemetry": telemetry_logs,
                "total_duration_ms": round(total_duration, 2)
            }

        # Step 2: METAR Weather & Force Majeure Bluff Disprover
        t1 = time.time()
        bluff_res = self.bluff_agent.run(
            airport_icao=fl["origin_icao"],
            airline_excuse=fl["airline_claim_reason"]
        )
        log_step(
            self.bluff_agent.agent_name,
            "SUCCESS",
            bluff_res["reasoning"],
            (time.time() - t1) * 1000
        )

        bluff_data = bluff_res["data"]["bluff_analysis"]
        metar_data = bluff_res["data"]["metar_evidence"]

        # Step 3: Great-Circle Distance & Multi-Jurisdiction Compensation Calculation
        t2 = time.time()
        legal_res = self.legal_agent.run(
            origin_icao=fl["origin_icao"],
            destination_icao=fl["destination_icao"],
            delay_minutes=delay_mins,
            carrier_name=fl["carrier"],
            receipts_amount_eur=receipts_amount_eur
        )
        log_step(
            self.legal_agent.agent_name,
            "SUCCESS",
            legal_res["reasoning"],
            (time.time() - t2) * 1000
        )

        payout = legal_res["data"]["payout_breakdown"]
        comp_eur = payout["statutory_cash_compensation_eur"]
        total_eur = payout["total_maximum_claim_value_eur"]

        # Step 4: Pre-fill Carrier Claim Form & Legal Demand Letter
        t3 = time.time()
        filer_res = self.filer_agent.run(
            passenger_name=passenger_name,
            pnr_code=pnr_code,
            flight_number=fl["flight_number"],
            carrier_name=fl["carrier"],
            compensation_amount_eur=int(total_eur),
            evidence_summary=bluff_data["evidence_summary"]
        )
        log_step(
            self.filer_agent.agent_name,
            "READY_FOR_HITL",
            filer_res["reasoning"],
            (time.time() - t3) * 1000
        )

        total_duration = (time.time() - start_time) * 1000

        # Step 5: Build Decision Package for HITL UI
        decision_package = {
            "decision_id": f"CLM-{fl['flight_number']}-{int(time.time())}",
            "created_at": time.strftime("%Y-%m-%d %H:%M:%S"),
            "passenger_name": passenger_name,
            "pnr_code": pnr_code,
            "flight_info": {
                "flight_number": fl["flight_number"],
                "carrier": fl["carrier"],
                "route": f"{fl['origin_name']} ({fl['origin_iata']}) -> {fl['destination_name']} ({fl['destination_iata']})",
                "delay_duration": f"{delay_mins // 60}h {delay_mins % 60}m",
                "airline_excuse": fl["airline_claim_reason"],
                "flight_date": flight_date
            },
            "disproval_evidence": {
                "verdict": bluff_data["verdict"],
                "metar_category": metar_data["flight_category"],
                "parallel_success_rate": f"{metar_data['departure_success_rate_pct']}%",
                "summary": bluff_data["evidence_summary"]
            },
            "compensation": {
                "amount_eur": total_eur,
                "amount_usd": payout["total_maximum_claim_value_usd"],
                "statutory_amount_eur": comp_eur,
                "duty_of_care_expenses_eur": payout["duty_of_care_expenses_reimbursement_eur"],
                "legal_basis": payout["legal_article_reference"],
                "geodesic_distance_km": legal_res["data"]["route"]["geodesic_distance_km"]
            },
            "action_package": filer_res["data"],
            "approval_state": "PENDING_APPROVAL"
        }

        return {
            "pipeline_status": "SURFACED_FOR_HUMAN_DECISION",
            "requires_human_action": True,
            "summary": f"Flight {fl['flight_number']} delayed by {delay_mins//60}h {delay_mins%60}m. Disproved weather excuse via METAR. Pre-packaged €{total_eur} claim for 1-click approval.",
            "decision_package": decision_package,
            "flight_monitor": flight_res,
            "bluff_disprover": bluff_res,
            "legal_rights": legal_res,
            "claim_filer": filer_res,
            "telemetry": telemetry_logs,
            "total_duration_ms": round(total_duration, 2)
        }
