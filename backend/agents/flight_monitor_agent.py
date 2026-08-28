"""
FlightMonitorAgent - Monitors flight telemetry and departure/arrival delays.
"""
import json
import logging
from typing import Dict, Any

from backend.tools.flight_telemetry import check_flight_status

logger = logging.getLogger("OmniClaim.FlightMonitorAgent")

class FlightMonitorAgent:
    """
    Strands Agent responsible for monitoring flight schedules and identifying 3+ hour delays.
    """
    def __init__(self, model_provider=None):
        self.model_provider = model_provider
        self.agent_name = "FlightMonitorAgent"

    def run(self, flight_number: str, flight_date: str = "2026-08-22") -> Dict[str, Any]:
        logger.info(f"[{self.agent_name}] Checking flight status for {flight_number} on {flight_date}")

        raw_result = check_flight_status(flight_number=flight_number, flight_date=flight_date)
        data = json.loads(raw_result)

        fl = data["flight"]
        delay_mins = fl["delay_minutes"]
        qualifies = data["eligibility_precheck"]["qualifies_for_eu261_threshold"]

        reasoning = (
            f"Flight {fl['flight_number']} ({fl['carrier']}) from {fl['origin_iata']} to {fl['destination_iata']} "
            f"was delayed by {delay_mins} minutes ({round(delay_mins/60.0, 1)} hours). "
            f"EU261 3-hour minimum threshold met: {qualifies}."
        )

        return {
            "agent": self.agent_name,
            "status": "COMPLETED",
            "reasoning": reasoning,
            "data": data
        }
