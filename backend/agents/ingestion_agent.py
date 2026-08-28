"""
IngestionAgent - Analyzes household bills and detects price anomalies.
"""
import json
import logging
from typing import Dict, Any

from backend.tools.bill_parser import parse_household_bill

logger = logging.getLogger("AegisAdmin.IngestionAgent")

class IngestionAgent:
    """
    Strands Agent responsible for ingesting household bills, extracting metadata,
    and assessing price variance against historical baselines.
    """
    def __init__(self, model_provider=None):
        self.model_provider = model_provider
        self.agent_name = "IngestionAgent"

    def run(self, bill_text: str, filename: str = "imported_bill.pdf") -> Dict[str, Any]:
        """
        Executes the ingestion and anomaly detection pipeline.
        """
        logger.info(f"[{self.agent_name}] Ingesting bill document: {filename}")
        
        # Execute tool reasoning
        raw_result = parse_household_bill(bill_text=bill_text, filename=filename)
        data = json.loads(raw_result)

        is_anomaly = data.get("anomaly_analysis", {}).get("is_anomaly", False)
        increase_pct = data.get("anomaly_analysis", {}).get("percentage_increase", 0.0)

        reasoning = (
            f"Parsed bill from {data['bill_metadata']['provider']} for ${data['bill_metadata']['amount_due']:.2f}. "
            f"Detected {increase_pct}% price increase over baseline. Flagged as anomaly: {is_anomaly}."
        )

        return {
            "agent": self.agent_name,
            "status": "COMPLETED",
            "reasoning": reasoning,
            "data": data
        }
