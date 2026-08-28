"""
Unit tests for OmniClaim AI Strands Tools.
"""
import json
import pytest

from backend.tools.flight_telemetry import check_flight_status
from backend.tools.metar_weather import evaluate_weather_bluff
from backend.tools.distance_matrix import calculate_compensation_entitlement
from backend.tools.carrier_form_filler import generate_prefilled_claim_package
from backend.tools.receipt_vision_parser import parse_receipt_or_boarding_pass

def test_parse_receipt_or_boarding_pass():
    raw_ocr = """BOARDING PASS
PASSENGER NAME: Alex Morgan
FLIGHT: LH401
PNR: PNR-LH992
SEAT: 12A GATE: B22
AIRPORT RESTAURANT RECEIPT: Total EUR 45.00
"""
    raw_res = parse_receipt_or_boarding_pass(document_text=raw_ocr, filename="test_pass.jpg")
    data = json.loads(raw_res)

    assert data["status"] == "SUCCESS"
    extracted = data["vision_ocr_extracted"]
    assert extracted["flight_number"] == "LH401"
    assert extracted["pnr_code"] == "PNR-LH992"
    assert extracted["passenger_name"] == "Alex Morgan"
    assert extracted["incurred_expense_receipt_eur"] == 45.00

def test_check_flight_status():
    raw_res = check_flight_status(flight_number="LH401")
    data = json.loads(raw_res)

    assert data["status"] == "SUCCESS"
    assert data["flight"]["flight_number"] == "LH401"
    assert data["flight"]["delay_minutes"] == 255
    assert data["eligibility_precheck"]["qualifies_for_eu261_threshold"] is True

def test_evaluate_weather_bluff_disproved():
    raw_res = evaluate_weather_bluff(
        airport_icao="EDDF",
        airline_excuse="Severe Thunderstorm Weather Delay"
    )
    data = json.loads(raw_res)

    assert data["status"] == "SUCCESS"
    assert data["bluff_analysis"]["verdict"] == "BLUFF_DISPROVED"
    assert data["bluff_analysis"]["airline_liable"] is True
    assert data["metar_evidence"]["departure_success_rate_pct"] > 85.0

def test_calculate_compensation_entitlement_transatlantic():
    raw_res = calculate_compensation_entitlement(
        origin_icao="EDDF",
        destination_icao="KJFK",
        delay_minutes=255,
        receipts_amount_eur=0.0
    )
    data = json.loads(raw_res)

    assert data["status"] == "SUCCESS"
    assert data["route"]["geodesic_distance_km"] > 3500
    assert data["payout_breakdown"]["statutory_cash_compensation_eur"] == 600
    assert data["payout_breakdown"]["total_maximum_claim_value_eur"] == 600.0

def test_calculate_compensation_entitlement_shorthaul_with_expenses():
    raw_res = calculate_compensation_entitlement(
        origin_icao="EGSS",
        destination_icao="LEBL",
        delay_minutes=220,
        receipts_amount_eur=65.0
    )
    data = json.loads(raw_res)

    assert data["status"] == "SUCCESS"
    assert data["route"]["geodesic_distance_km"] < 1500
    assert data["payout_breakdown"]["statutory_cash_compensation_eur"] == 250
    assert data["payout_breakdown"]["duty_of_care_expenses_reimbursement_eur"] == 65.0
    assert data["payout_breakdown"]["total_maximum_claim_value_eur"] == 315.0

def test_generate_prefilled_claim_package():
    raw_res = generate_prefilled_claim_package(
        passenger_name="Alex Morgan",
        pnr_code="PNR-LH992",
        flight_number="LH401",
        carrier_name="Lufthansa German Airlines",
        compensation_amount_eur=665,
        evidence_summary="METAR weather confirmed VFR clear skies."
    )
    data = json.loads(raw_res)

    assert data["status"] == "SUCCESS"
    assert data["compensation_eur"] == 665
    assert "Alex Morgan" in data["drafted_legal_letter"]["body"]
    assert "EU261" in data["drafted_legal_letter"]["subject"]
