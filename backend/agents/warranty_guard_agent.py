"""
WarrantyGuardAgent - Tracks trial expirations and device warranty deadlines.
"""
import json
import logging
from typing import Dict, Any

from backend.tools.warranty_checker import track_contract_expirations

logger = logging.getLogger("AegisAdmin.WarrantyGuardAgent")

class WarrantyGuardAgent:
    """
    Strands Agent responsible for monitoring trial expirations, device warranties,
    and contract promo periods to prevent unexpected auto-renewals.
    """
    def __init__(self, model_provider=None):
        self.model_provider = model_provider
        self.agent_name = "WarrantyGuardAgent"

    def run(self, days_ahead: int = 30) -> Dict[str, Any]:
        """
        Executes expiration audit.
        """
        logger.info(f"[{self.agent_name}] Auditing upcoming expirations ({days_ahead} days lookahead)")

        raw_result = track_contract_expirations(days_ahead=days_ahead)
        data = json.loads(raw_result)

        count = data.get("total_expirations_found", 0)
        items = data.get("items", [])

        high_risk_count = sum(1 for item in items if item.get("urgency") == "HIGH")

        reasoning = (
            f"Audited household contracts. Found {count} expiring item(s) in next {days_ahead} days. "
            f"High-urgency auto-renewals requiring action: {high_risk_count}."
        )

        return {
            "agent": self.agent_name,
            "status": "COMPLETED",
            "reasoning": reasoning,
            "data": data
        }
