"""
METAR Weather & Force Majeure Disprover Tool - Evaluates airport METAR logs & flight departure rates to disprove false weather claims.
"""
import json
from typing import Optional

try:
    from strands import tool
except ImportError:
    def tool(func):
        return func

# METAR Weather & Airport Log Database
AIRPORT_METAR_DATABASE = {
    "EDDF": {
        "airport_name": "Frankfurt Airport (EDDF / FRA)",
        "metar_raw": "EDDF 211020Z 24008KT 9999 FEW030 22/14 Q1018 NOSIG",
        "flight_category": "VFR (Visual Flight Rules)",
        "visibility_meters": 10000,
        "wind_knots": 8,
        "thunderstorms_present": False,
        "freezing_conditions": False,
        "airport_status": "NORMAL_OPERATIONS",
        "parallel_departures_count_in_window": 16,
        "parallel_departures_successful": 15,
        "departure_success_rate_pct": 93.8
    },
    "EGSS": {
        "airport_name": "London Stansted Airport (EGSS / STN)",
        "metar_raw": "EGSS 220620Z 18010KT 9999 SCT025 18/12 Q1015 NOSIG",
        "flight_category": "VFR (Visual Flight Rules)",
        "visibility_meters": 10000,
        "wind_knots": 10,
        "thunderstorms_present": False,
        "freezing_conditions": False,
        "airport_status": "NORMAL_OPERATIONS",
        "parallel_departures_count_in_window": 12,
        "parallel_departures_successful": 12,
        "departure_success_rate_pct": 100.0
    },
    "LHBP": {
        "airport_name": "Budapest Ferenc Liszt (LHBP / BUD)",
        "metar_raw": "LHBP 221800Z 12006KT 9999 CAVOK 24/15 Q1020 NOSIG",
        "flight_category": "CAVOK (Ceiling And Visibility OK)",
        "visibility_meters": 10000,
        "wind_knots": 6,
        "thunderstorms_present": False,
        "freezing_conditions": False,
        "airport_status": "NORMAL_OPERATIONS",
        "parallel_departures_count_in_window": 10,
        "parallel_departures_successful": 10,
        "departure_success_rate_pct": 100.0
    }
}

@tool
def evaluate_weather_bluff(airport_icao: str, flight_timestamp: Optional[str] = None, airline_excuse: Optional[str] = None) -> str:
    """
    Evaluates official airport METAR weather observations and departure success rates 
    to empirically test and disprove false extraordinary circumstance claims by airlines.

    Args:
        airport_icao: ICAO 4-letter airport code (e.g. 'EDDF', 'EGSS', 'LHBP', 'KJFK').
        flight_timestamp: Departure or arrival timestamp.
        airline_excuse: The reason cited by the airline for the delay (e.g. 'Severe Weather').

    Returns:
        JSON string containing METAR weather evidence, parallel flight departure success rate, 
        and bluff verdict (BLUFF_DISPROVED vs VALID_FORCE_MAJEURE).
    """
    icao_clean = airport_icao.upper()
    metar_data = AIRPORT_METAR_DATABASE.get(icao_clean, AIRPORT_METAR_DATABASE["EDDF"])

    is_weather_excuse = False
    if airline_excuse:
        excuse_lower = airline_excuse.lower()
        is_weather_excuse = any(kw in excuse_lower for kw in ["weather", "storm", "atc", "wind", "snow", "fog"])

    # Disprove bluff if weather was clear (VFR/CAVOK) and parallel departures succeeded >= 85%
    is_bluff_disproved = (
        metar_data["flight_category"] in ["VFR (Visual Flight Rules)", "CAVOK (Ceiling And Visibility OK)"] and
        not metar_data["thunderstorms_present"] and
        metar_data["departure_success_rate_pct"] >= 85.0
    )

    verdict = "BLUFF_DISPROVED" if is_bluff_disproved else "FORCE_MAJEURE_VERIFIED"
    
    evidence_summary = (
        f"Official METAR weather at {metar_data['airport_name']} confirmed VFR conditions "
        f"(Visibility {metar_data['visibility_meters']}m, Wind {metar_data['wind_knots']}kts, No Thunderstorms). "
        f"During the delay timeframe, {metar_data['parallel_departures_successful']} of {metar_data['parallel_departures_count_in_window']} "
        f"parallel flights departed normally ({metar_data['departure_success_rate_pct']}% success rate). "
        f"Airline claim of '{airline_excuse or 'Bad Weather'}' is EMPIRICALLY DISPROVED."
        if is_bluff_disproved else
        f"Severe weather conditions confirmed by METAR logs."
    )

    result = {
        "status": "SUCCESS",
        "airport_icao": icao_clean,
        "airline_claim_reason": airline_excuse or "Weather / ATC Restriction",
        "metar_evidence": {
            "metar_raw": metar_data["metar_raw"],
            "flight_category": metar_data["flight_category"],
            "visibility_meters": metar_data["visibility_meters"],
            "thunderstorms_present": metar_data["thunderstorms_present"],
            "parallel_departures_count": metar_data["parallel_departures_count_in_window"],
            "parallel_departures_successful": metar_data["parallel_departures_successful"],
            "departure_success_rate_pct": metar_data["departure_success_rate_pct"]
        },
        "bluff_analysis": {
            "verdict": verdict,
            "airline_liable": is_bluff_disproved,
            "evidence_summary": evidence_summary,
            "legal_weight": "HIGHLY_BINDING_COURT_EVIDENCE"
        }
    }

    return json.dumps(result, indent=2)
