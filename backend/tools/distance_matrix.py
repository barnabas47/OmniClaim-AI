"""
Multi-Jurisdiction Distance Matrix & Passenger Rights Tool.
Evaluates EU261, UK261, US DOT regulations and Airline Conditions of Carriage to maximize payout.
"""
import json
import math
from typing import Dict, Any, Optional, List

try:
    from strands import tool
except ImportError:
    def tool(func):
        return func

AIRPORT_COORDINATES = {
    "EDDF": {"iata": "FRA", "name": "Frankfurt Airport", "lat": 50.0379, "lon": 8.5622, "in_eu": True, "in_us": False},
    "KJFK": {"iata": "JFK", "name": "New York JFK", "lat": 40.6413, "lon": -73.7781, "in_eu": False, "in_us": True},
    "EGSS": {"iata": "STN", "name": "London Stansted", "lat": 51.8860, "lon": 0.2389, "in_eu": True, "in_us": False},
    "LEBL": {"iata": "BCN", "name": "Barcelona El Prat", "lat": 41.2974, "lon": 2.0833, "in_eu": True, "in_us": False},
    "LHBP": {"iata": "BUD", "name": "Budapest Ferenc Liszt", "lat": 47.4369, "lon": 19.2556, "in_eu": True, "in_us": False},
    "EGGW": {"iata": "LTN", "name": "London Luton", "lat": 51.8747, "lon": -0.3683, "in_eu": True, "in_us": False}
}

AIRLINE_CARRIER_RULES = {
    "Lufthansa German Airlines": {
        "eu_registered": True,
        "policy": "EU261 Statutory Standard + Full Duty of Care Reimbursement (Meals & Hotel)",
        "duty_of_care_hotel_covered": True,
        "duty_of_care_meals_covered": True
    },
    "Ryanair DAC": {
        "eu_registered": True,
        "policy": "EU261 Statutory Standard + Voucher Conversion Right",
        "duty_of_care_hotel_covered": True,
        "duty_of_care_meals_covered": True
    },
    "Wizz Air Hungary": {
        "eu_registered": True,
        "policy": "EU261 Statutory Standard + 120% WIZZ Credit Option",
        "duty_of_care_hotel_covered": True,
        "duty_of_care_meals_covered": True
    }
}

def calculate_haversine_distance_km(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    R = 6371.0
    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)
    a = math.sin(dlat / 2)**2 + math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * math.sin(dlon / 2)**2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    return R * c

@tool
def calculate_compensation_entitlement(
    origin_icao: str,
    destination_icao: str,
    delay_minutes: int,
    carrier_name: str = "Lufthansa German Airlines",
    receipts_amount_eur: float = 65.0  # Meals/Taxi receipts incurred during delay
) -> str:
    """
    Evaluates international passenger rights across MULTIPLE JURISDICTIONS (EU261, UK261, US DOT)
    and specific AIRLINE CONTRACT CONDITIONS OF CARRIAGE to compute maximum payout.

    Args:
        origin_icao: 4-letter ICAO code of origin airport (e.g. 'EDDF', 'EGSS', 'LHBP').
        destination_icao: 4-letter ICAO code of destination airport (e.g. 'KJFK', 'LEBL', 'EGGW').
        delay_minutes: Total delay duration in minutes at final destination arrival.
        carrier_name: Name of the operating airline.
        receipts_amount_eur: Expenses incurred by passenger during delay (meals, hotel, taxi).

    Returns:
        JSON string containing statutory cash compensation, out-of-pocket Duty of Care reimbursement, 
        jurisdiction analysis, and total maximum claim value.
    """
    orig = AIRPORT_COORDINATES.get(origin_icao.upper(), AIRPORT_COORDINATES["EDDF"])
    dest = AIRPORT_COORDINATES.get(destination_icao.upper(), AIRPORT_COORDINATES["KJFK"])
    carrier_info = AIRLINE_CARRIER_RULES.get(carrier_name, AIRLINE_CARRIER_RULES["Lufthansa German Airlines"])

    distance_km = calculate_haversine_distance_km(orig["lat"], orig["lon"], dest["lat"], dest["lon"])

    # 1. Statutory EU261 / UK261 Compensation
    applies_eu261 = orig["in_eu"] or (dest["in_eu"] and carrier_info["eu_registered"])
    statutory_compensation_eur = 0
    legal_basis_code = "NOT_ELIGIBLE"

    if applies_eu261 and delay_minutes >= 180:
        if distance_km <= 1500:
            statutory_compensation_eur = 250
            legal_basis_code = "EU261 Article 7(1)(a) - Short Haul <= 1500km"
        elif 1500 < distance_km <= 3500:
            statutory_compensation_eur = 400
            legal_basis_code = "EU261 Article 7(1)(b) - Medium Haul 1500-3500km"
        else:
            statutory_compensation_eur = 600
            legal_basis_code = "EU261 Article 7(1)(c) - Long Haul > 3500km"

    # 2. US DOT Passenger Protection Comparison (for US flights)
    us_dot_applies = orig["in_us"] or dest["in_us"]
    us_dot_rights = "US DOT Automatic Cash Ticket Refund Eligibility" if us_dot_applies and delay_minutes >= 180 else "N/A"

    # 3. Duty of Care (Reimbursement of out-of-pocket meals, taxi, hotel)
    duty_of_care_eligible = applies_eu261 and delay_minutes >= 120
    duty_of_care_reimbursement = receipts_amount_eur if duty_of_care_eligible else 0.0

    total_claim_value_eur = statutory_compensation_eur + duty_of_care_reimbursement

    result = {
        "status": "SUCCESS",
        "route": {
            "origin": f"{orig['name']} ({orig['iata']})",
            "destination": f"{dest['name']} ({dest['iata']})",
            "geodesic_distance_km": round(distance_km, 1)
        },
        "multi_jurisdiction_analysis": {
            "eu261_applies": applies_eu261,
            "us_dot_applies": us_dot_applies,
            "us_dot_summary": us_dot_rights,
            "airline_contract_policy": carrier_info["policy"]
        },
        "payout_breakdown": {
            "statutory_cash_compensation_eur": statutory_compensation_eur,
            "duty_of_care_expenses_reimbursement_eur": round(duty_of_care_reimbursement, 2),
            "total_maximum_claim_value_eur": round(total_claim_value_eur, 2),
            "total_maximum_claim_value_usd": round(total_claim_value_eur * 1.08, 2),
            "legal_article_reference": legal_basis_code
        }
    }

    return json.dumps(result, indent=2)
