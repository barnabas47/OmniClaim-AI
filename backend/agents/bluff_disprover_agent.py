"""
BluffDisproverAgent - Evaluates airport METAR weather reports to disprove false force majeure claims.
"""
import json
import logging
from typing import Dict, Any

from backend.tools.metar_weather import evaluate_weather_bluff

try:
    from strands import Agent
    HAS_STRANDS = True
except ImportError:
    HAS_STRANDS = False

from backend.tools.metar_weather import evaluate_weather_bluff
from backend.agents.strands_bedrock_engine import StrandsBedrockEngine

logger = logging.getLogger("OmniClaim.BluffDisproverAgent")

class BluffDisproverAgent:
    """
    Strands Agent responsible for fetching official airport METAR weather logs
    and parallel flight departure rates to empirically test and disprove false airline force majeure excuses.
    Powered by Amazon Bedrock (Claude 3.7 Sonnet / Nova Pro).
    """
    def __init__(self, model_provider=None):
        self.model_provider = model_provider
        self.agent_name = "BluffDisproverAgent"
        self.bedrock_engine = StrandsBedrockEngine()
        self.strands_agent = None

        if HAS_STRANDS:
            try:
                self.strands_agent = Agent(
                    name=self.agent_name,
                    description="Evaluates NOAA METAR weather logs & parallel flight departure rates to disprove force majeure claims",
                    system_prompt="You are an autonomous weather & aviation audit agent powered by Amazon Bedrock."
                )
            except Exception as e:
                logger.info(f"Strands Agent init note: {e}")

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

        llm_reasoning = self.bedrock_engine.synthesize_bluff_disproval_reasoning(
            flight_number="LH401",
            origin_icao=airport_icao,
            metar_raw=data["live_noaa_metar"],
            airline_excuse=airline_excuse,
            departure_success_rate=data["metar_evidence"]["departure_success_rate_pct"]
        )

        return {
            "agent": self.agent_name,
            "status": "COMPLETED",
            "reasoning": llm_reasoning,
            "strands_sdk_active": HAS_STRANDS,
            "bedrock_model": "us.anthropic.claude-3-7-sonnet-20250219-v1:0",
            "data": data
        }

