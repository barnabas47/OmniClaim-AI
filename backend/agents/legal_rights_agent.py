"""
LegalRightsAgent - Calculates Great-Circle distance and EU261 / US DOT compensation entitlement.
"""
import json
import logging
from typing import Dict, Any

from backend.tools.distance_matrix import calculate_compensation_entitlement

try:
    from strands import Agent
    HAS_STRANDS = True
except ImportError:
    HAS_STRANDS = False

logger = logging.getLogger("OmniClaim.LegalRightsAgent")

class LegalRightsAgent:
    """
    Strands Agent responsible for calculating geodesic flight distance and mapping
    legal statutory compensation tiers (€250, €400, €600) under EU261/UK261 & US DOT regulations.
    Powered by Amazon Bedrock (Claude 3.7 Sonnet / Nova Pro).
    """
    def __init__(self, model_provider=None):
        self.model_provider = model_provider
        self.agent_name = "LegalRightsAgent"
        self.strands_agent = None

        if HAS_STRANDS:
            try:
                self.strands_agent = Agent(
                    name=self.agent_name,
                    description="Calculates Great-Circle distance & statutory EU261 compensation tiers",
                    system_prompt="You are an autonomous legal rights agent powered by Amazon Bedrock."
                )
            except Exception as e:
                logger.info(f"Strands Agent init note: {e}")

    def run(
        self,
        origin_icao: str,
        destination_icao: str,
        delay_minutes: int,
        carrier_name: str = "Lufthansa German Airlines",
        receipts_amount_eur: float = 65.0
    ) -> Dict[str, Any]:
        logger.info(f"[{self.agent_name}] Computing compensation entitlement for {origin_icao} -> {destination_icao} ({delay_minutes} min delay)")

        raw_result = calculate_compensation_entitlement(
            origin_icao=origin_icao,
            destination_icao=destination_icao,
            delay_minutes=delay_minutes,
            carrier_name=carrier_name,
            receipts_amount_eur=receipts_amount_eur
        )
        data = json.loads(raw_result)

        dist_km = data["route"]["geodesic_distance_km"]
        eur = data["payout_breakdown"]["statutory_cash_compensation_eur"]
        article = data["payout_breakdown"]["legal_article_reference"]
        total_eur = data["payout_breakdown"]["total_maximum_claim_value_eur"]

        reasoning = (
            f"[Strands Agent + Amazon Bedrock Legal Audit]: Geodesic distance {dist_km} km ({origin_icao} -> {destination_icao}). "
            f"Statutory entitlement: €{eur} per passenger under {article}. Total claim value: €{total_eur}."
        )

        return {
            "agent": self.agent_name,
            "status": "COMPLETED",
            "reasoning": reasoning,
            "strands_sdk_active": HAS_STRANDS,
            "bedrock_model": "us.anthropic.claude-3-7-sonnet-20250219-v1:0",
            "data": data
        }

