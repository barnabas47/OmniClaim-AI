import pytest
from src.agents.omniclaim_agent import OmniClaimAgent
from src.agents.safecode_agent import SafeCodeAgent
from src.serverless.jobs_runner import NebiusServerlessJobRunner

def test_omniclaim_agent():
    agent = OmniClaimAgent()
    sample_claim = {
        "claim_id": "CLM-2026-99",
        "policy_holder": "John Doe",
        "amount": 1250.50,
        "description": "Windshield damage due to storm."
    }
    res = agent.process_claim(sample_claim)
    assert res["claim_id"] == "CLM-2026-99"
    assert "fast_parse_output" in res
    assert "fraud_analysis_output" in res

def test_safecode_agent():
    agent = SafeCodeAgent()
    snippet = "def query_db(user_input): return db.execute('SELECT * FROM users WHERE name=' + user_input)"
    vuln = "SQL Injection vulnerability"
    res = agent.audit_and_patch(snippet, vuln)
    assert res["sandbox_environment"] == "Nebius Token Factory Sandbox"
    assert "patch_result" in res

def test_serverless_jobs():
    runner = NebiusServerlessJobRunner()
    batch = [
        {"claim_id": "CLM-1", "amount": 100},
        {"claim_id": "CLM-2", "amount": 200}
    ]
    res = runner.run_batch_claims_job(batch)
    assert res["status"] == "COMPLETED"
    assert res["processed_items_count"] == 2
