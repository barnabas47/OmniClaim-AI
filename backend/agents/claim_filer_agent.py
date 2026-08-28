"""
ClaimFilerAgent - Pre-fills official carrier claim forms and drafts legal demand letters for HITL gate.
"""
import json
import logging
from typing import Dict, Any

from backend.tools.carrier_form_filler import generate_prefilled_claim_package

logger = logging.getLogger("OmniClaim.ClaimFilerAgent")

class ClaimFilerAgent:
    """
    Strands Agent responsible for generating pre-filled carrier claim forms 
    and drafting legally binding EU261 demand letters ready for 1-click human approval.
    """
    def __init__(self, model_provider=None):
        self.model_provider = model_provider
        self.agent_name = "ClaimFilerAgent"

    def run(
        self,
        passenger_name: str,
        pnr_code: str,
        flight_number: str,
        carrier_name: str,
        compensation_amount_eur: int,
        evidence_summary: str
    ) -> Dict[str, Any]:
        logger.info(f"[{self.agent_name}] Pre-filling claim package for {passenger_name} ({carrier_name} - €{compensation_amount_eur})")

        raw_result = generate_prefilled_claim_package(
            passenger_name=passenger_name,
            pnr_code=pnr_code,
            flight_number=flight_number,
            carrier_name=carrier_name,
            compensation_amount_eur=compensation_amount_eur,
            evidence_summary=evidence_summary
        )
        data = json.loads(raw_result)

        title = data["prefilled_form"]["title"]

        reasoning = (
            f"Pre-filled '{title}' for passenger {passenger_name}. "
            f"Attached METAR weather disproval report and drafted legal demand letter. "
            f"Package ready for HITL approval (Entitlement: €{compensation_amount_eur})."
        )

        return {
            "agent": self.agent_name,
            "status": "READY_FOR_HUMAN_APPROVAL",
            "reasoning": reasoning,
            "data": data
        }
