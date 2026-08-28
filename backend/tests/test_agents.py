"""
Unit tests for OmniClaim AI Strands Multi-Agent Orchestration.
"""
import pytest
from backend.agents.concierge_orchestrator import OmniClaimOrchestrator

def test_omniclaim_orchestrator_transatlantic_delay_pipeline():
    orchestrator = OmniClaimOrchestrator()
    result = orchestrator.process_flight_compensation_pipeline(
        flight_number="LH401",
        passenger_name="Alex Morgan",
        pnr_code="PNR-LH992",
        receipts_amount_eur=65.0
    )

    assert result["pipeline_status"] == "SURFACED_FOR_HUMAN_DECISION"
    assert result["requires_human_action"] is True
    assert "decision_package" in result

    dec = result["decision_package"]
    assert dec["compensation"]["statutory_amount_eur"] == 600
    assert dec["compensation"]["duty_of_care_expenses_eur"] == 65.0
    assert dec["compensation"]["amount_eur"] == 665.0
    assert dec["disproval_evidence"]["verdict"] == "BLUFF_DISPROVED"
    assert len(result["telemetry"]) >= 4

def test_omniclaim_orchestrator_shorthaul_delay_pipeline():
    orchestrator = OmniClaimOrchestrator()
    result = orchestrator.process_flight_compensation_pipeline(
        flight_number="FR8821",
        passenger_name="Alex Morgan",
        pnr_code="PNR-FR331",
        receipts_amount_eur=0.0
    )

    assert result["pipeline_status"] == "SURFACED_FOR_HUMAN_DECISION"
    assert result["requires_human_action"] is True

    dec = result["decision_package"]
    assert dec["compensation"]["statutory_amount_eur"] == 250
    assert dec["compensation"]["amount_eur"] == 250.0
    assert dec["flight_info"]["carrier"] == "Ryanair DAC"
