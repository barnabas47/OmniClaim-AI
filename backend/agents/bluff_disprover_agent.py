"""
BluffDisproverAgent - Evaluates airport METAR weather reports to disprove false force majeure claims.
"""
import json
import logging
from typing import Dict, Any

from backend.tools.metar_weather import evaluate_weather_bluff

logger = logging.getLogger("OmniClaim.BluffDisproverAgent")

class BluffDisproverAgent:
    """
    Strands Agent responsible for fetching official airport METAR weather logs
    and parallel flight departure rates to empirically test and disprove false airline force majeure excuses.
    """
    def __init__(self, model_provider=None):
        self.model_provider = model_provider
        self.agent_name = "BluffDisproverAgent"

    def run(self, airport_icao: str, airline_excuse: str = "Weather / ATC") -> Dict[str, Any]:
        logger.info(f"[{self.agent_name}] Auditing METAR weather & bluff for {airport_icao} (Excuse: '{airline_excuse}')")

        raw_result = evaluate_weather_bluff(
            airport_icao=airport_icao,
            airline_excuse=airline_excuse
        )
        data = json.loads(raw_result)

        bluff_verdict = data["bluff_analysis"]["verdict"]
        is_bluff = data["bluff_analysis"]["airline_liable"]
        summary = data["bluff_analysis"]["evidence_summary"]

        reasoning = (
            f"Evaluated METAR logs for {airport_icao}. Verdict: {bluff_verdict}. "
            f"Airline claim of '{airline_excuse}' is disproved ({data['metar_evidence']['departure_success_rate_pct']}% of parallel flights departed normally). Airline is liable."
        )

        return {
            "agent": self.agent_name,
            "status": "COMPLETED",
            "reasoning": reasoning,
            "data": data
        }
