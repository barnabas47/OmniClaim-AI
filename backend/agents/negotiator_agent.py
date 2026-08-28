"""
NegotiatorAgent - Pre-fills switching forms and drafts dispute letters for Human-in-the-Loop gate.
"""
import json
import logging
from typing import Dict, Any

from backend.tools.form_filler import generate_prefilled_action_package

logger = logging.getLogger("AegisAdmin.NegotiatorAgent")

class NegotiatorAgent:
    """
    Strands Agent responsible for preparing actionable dispute letters and 
    pre-filling official service transfer applications ready for human 1-click authorization.
    """
    def __init__(self, model_provider=None):
        self.model_provider = model_provider
        self.agent_name = "NegotiatorAgent"

    def run(
        self,
        customer_name: str,
        account_number: str,
        current_provider: str,
        target_provider: str,
        target_plan: str,
        current_rate: float,
        new_rate: float,
        action_type: str = "SWITCH_PROVIDER"
    ) -> Dict[str, Any]:
        """
        Executes pre-filing package generation.
        """
        logger.info(f"[{self.agent_name}] Pre-filling action package for {action_type} ({current_provider} -> {target_provider})")

        raw_result = generate_prefilled_action_package(
            customer_name=customer_name,
            account_number=account_number,
            current_provider=current_provider,
            target_provider=target_provider,
            target_plan=target_plan,
            current_rate=current_rate,
            new_rate=new_rate,
            action_type=action_type
        )
        data = json.loads(raw_result)

        form_title = data.get("summary", {}).get("form_title", "Action Form")
        savings = data.get("summary", {}).get("projected_annual_savings", 0.0)

        reasoning = (
            f"Pre-filled '{form_title}' and drafted dispute letter. "
            f"Package ready for HITL approval. Estimated annual value: ${savings:.2f}."
        )

        return {
            "agent": self.agent_name,
            "status": "READY_FOR_HUMAN_APPROVAL",
            "reasoning": reasoning,
            "data": data
        }
