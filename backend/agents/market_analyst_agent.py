"""
MarketAnalystAgent - Researches competitor plans and retention packages.
"""
import json
import logging
from typing import Dict, Any

from backend.tools.market_search import search_market_competitor_rates

logger = logging.getLogger("AegisAdmin.MarketAnalystAgent")

class MarketAnalystAgent:
    """
    Strands Agent responsible for researching utility/telecom market benchmarks,
    identifying competitor offers, and calculating annual ROI of switching.
    """
    def __init__(self, model_provider=None):
        self.model_provider = model_provider
        self.agent_name = "MarketAnalystAgent"

    def run(self, category: str, current_provider: str, current_monthly_rate: float) -> Dict[str, Any]:
        """
        Executes market benchmark search and savings calculation.
        """
        logger.info(f"[{self.agent_name}] Researching market rates for {category} ({current_provider} @ ${current_monthly_rate:.2f}/mo)")

        raw_result = search_market_competitor_rates(
            category=category,
            current_provider=current_provider,
            current_monthly_rate=current_monthly_rate
        )
        data = json.loads(raw_result)

        rec = data.get("recommendation", {})
        annual_savings = rec.get("estimated_annual_savings", 0.0)
        best_provider = rec.get("best_option_provider", "Competitor")

        reasoning = (
            f"Evaluated market rate options for {category}. Best alternative is {best_provider} "
            f"at ${rec.get('recommended_monthly_rate', 0.0):.2f}/mo. Potential annual savings: ${annual_savings:.2f}."
        )

        return {
            "agent": self.agent_name,
            "status": "COMPLETED",
            "reasoning": reasoning,
            "data": data
        }
