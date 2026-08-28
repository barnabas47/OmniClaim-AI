import json
import logging
from typing import Dict, Any
from src.nebius_client import NebiusTokenFactoryClient
from src.config import settings

logger = logging.getLogger("OmniClaimAgent")

class OmniClaimAgent:
    """
    Autonomous Insurance Claim Processing & Fraud Detection Copilot.
    Demonstrates Nemotron Multi-Model Routing:
      - Nemotron Nano: Fast document parsing, classification & initial routing.
      - Nemotron Ultra: Deep reasoning, complex fraud detection & legal validation.
    """

    def __init__(self, nebius_client: NebiusTokenFactoryClient = None):
        self.client = nebius_client or NebiusTokenFactoryClient()

    def process_claim(self, claim_data: Dict[str, Any]) -> Dict[str, Any]:
        logger.info(f"Processing claim ID: {claim_data.get('claim_id', 'UNKNOWN')}")
        
        # Step 1: Fast Parsing & Classification with Nemotron Nano
        nano_prompt = f"Extract key metadata and classify urgency for this insurance claim: {json.dumps(claim_data)}"
        nano_result = self.client.generate(
            prompt=nano_prompt,
            model=settings.MODEL_NANO,
            system_prompt="You are a fast document parser powered by NVIDIA Nemotron Nano on Nebius Token Factory."
        )
        
        # Step 2: Deep Fraud & Policy Validation with Nemotron Ultra
        ultra_prompt = f"""
        Perform deep reasoning and fraud risk assessment on this claim.
        Claim Data: {json.dumps(claim_data)}
        Pre-parsed summary: {nano_result}
        
        Evaluate:
        1. Fraud anomaly score (0.0 to 1.0)
        2. Policy compliance
        3. Final recommendation (APPROVE, FLAG_FOR_AUDIT, REJECT)
        """
        
        ultra_result = self.client.generate(
            prompt=ultra_prompt,
            model=settings.MODEL_ULTRA,
            system_prompt="You are an expert fraud investigator and claims reasoning agent powered by NVIDIA Nemotron Ultra."
        )
        
        return {
            "claim_id": claim_data.get("claim_id"),
            "fast_parse_model": settings.MODEL_NANO,
            "deep_reasoning_model": settings.MODEL_ULTRA,
            "nebius_infrastructure": "Nebius Token Factory + Nebius Serverless Endpoints",
            "fast_parse_output": nano_result,
            "fraud_analysis_output": ultra_result
        }
