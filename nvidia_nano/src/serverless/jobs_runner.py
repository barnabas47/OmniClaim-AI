import time
import logging
from typing import List, Dict, Any
from src.agents.omniclaim_agent import OmniClaimAgent

logger = logging.getLogger("NebiusServerlessJobs")

class NebiusServerlessJobRunner:
    """
    Simulates / Interfaces with Nebius Serverless Jobs for asynchronous batch processing.
    Ideal for large-scale claim auditing, synthetic data generation, or policy evaluation.
    """

    def __init__(self):
        self.agent = OmniClaimAgent()

    def run_batch_claims_job(self, claims_batch: List[Dict[str, Any]]) -> Dict[str, Any]:
        logger.info(f"Submitting Nebius Serverless Job: Batch of {len(claims_batch)} items.")
        start_time = time.time()
        
        results = []
        for claim in claims_batch:
            res = self.agent.process_claim(claim)
            results.append(res)
            
        elapsed = round(time.time() - start_time, 3)
        logger.info(f"Nebius Serverless Job completed in {elapsed}s.")
        
        return {
            "job_id": f"nebius-job-{int(time.time())}",
            "status": "COMPLETED",
            "processed_items_count": len(claims_batch),
            "execution_time_seconds": elapsed,
            "results": results
        }
