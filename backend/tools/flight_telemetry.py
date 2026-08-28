"""
Flight Telemetry Tool - Query flight status, scheduled vs actual departure, and delay duration.
"""
import json
import re
from typing import Dict, Any, Optional

try:
    from strands import tool
except ImportError:
    def tool(func):
        return func

# Database of sample flight telemetry
FLIGHT_DATABASE = {
    "LH401": {
        "flight_number": "LH401",
        "carrier": "Lufthansa German Airlines",
        "origin_iata": "FRA",
        "origin_icao": "EDDF",
        "origin_name": "Frankfurt Airport, Germany",
        "destination_iata": "JFK",
        "destination_icao": "KJFK",
        "destination_name": "John F. Kennedy Intl, NYC, USA",
        "scheduled_departure": "2026-08-21T10:15:00Z",
        "actual_departure": "2026-08-21T14:30:00Z",
        "scheduled_arrival": "2026-08-21T13:00:00Z",
        "actual_arrival": "2026-08-21T17:15:00Z",
        "delay_minutes": 255,  # 4h 15m delay
        "cancellation_status": "OPERATED_DELAYED",
        "airline_claim_reason": "Extraordinary Circumstances - Severe Thunderstorms & ATC Hold"
    },
    "FR8821": {
        "flight_number": "FR8821",
        "carrier": "Ryanair DAC",
        "origin_iata": "STN",
        "origin_icao": "EGSS",
        "origin_name": "London Stansted, UK",
        "destination_iata": "BCN",
        "destination_icao": "LEBL",
        "destination_name": "Barcelona El Prat, Spain",
        "scheduled_departure": "2026-08-22T06:30:00Z",
        "actual_departure": "2026-08-22T10:10:00Z",
        "scheduled_arrival": "2026-08-22T09:40:00Z",
        "actual_arrival": "2026-08-22T13:20:00Z",
        "delay_minutes": 220,  # 3h 40m delay
        "cancellation_status": "OPERATED_DELAYED",
        "airline_claim_reason": "Operational Crew Rest Overtime"
    },
    "W62310": {
        "flight_number": "W62310",
        "carrier": "Wizz Air Hungary",
        "origin_iata": "BUD",
        "origin_icao": "LHBP",
        "origin_name": "Budapest Ferenc Liszt, Hungary",
        "destination_iata": "LTN",
        "destination_icao": "EGGW",
        "destination_name": "London Luton, UK",
        "scheduled_departure": "2026-08-22T18:00:00Z",
        "actual_departure": "2026-08-22T22:30:00Z",
        "scheduled_arrival": "2026-08-22T19:35:00Z",
        "actual_arrival": "2026-08-22T23:55:00Z",
        "delay_minutes": 260,  # 4h 20m delay
        "cancellation_status": "OPERATED_DELAYED",
        "airline_claim_reason": "Technical Aircraft Defect"
    }
}

@tool
def check_flight_status(flight_number: str, flight_date: Optional[str] = None) -> str:
    """
    Queries flight status, scheduled vs actual timestamps, gate information, 
    and delay durations from global aviation telemetry feeds.

    Args:
        flight_number: Flight IATA code (e.g., 'LH401', 'FR8821', 'W62310').
        flight_date: Date of flight departure (YYYY-MM-DD).

    Returns:
        JSON string containing detailed flight status, delay minutes, and airline claim reason.
    """
    clean_fn = flight_number.replace(" ", "").upper()
    
    if clean_fn in FLIGHT_DATABASE:
        data = FLIGHT_DATABASE[clean_fn]
    else:
        # Generic fallback flight metadata
        data = {
            "flight_number": clean_fn,
            "carrier": "Commercial Carrier",
            "origin_iata": "FRA",
            "origin_icao": "EDDF",
            "origin_name": "Frankfurt Airport",
            "destination_iata": "JFK",
            "destination_icao": "KJFK",
            "destination_name": "New York JFK",
            "scheduled_departure": "2026-08-22T12:00:00Z",
            "actual_departure": "2026-08-22T16:00:00Z",
            "scheduled_arrival": "2026-08-22T15:00:00Z",
            "actual_arrival": "2026-08-22T19:00:00Z",
            "delay_minutes": 240,
            "cancellation_status": "OPERATED_DELAYED",
            "airline_claim_reason": "Unspecified Operational Delay"
        }

    is_eligible_delay = data["delay_minutes"] >= 180  # 3+ hours qualifies under EU261

    result = {
        "status": "SUCCESS",
        "flight": data,
        "eligibility_precheck": {
            "delay_minutes": data["delay_minutes"],
            "delay_hours": round(data["delay_minutes"] / 60.0, 2),
            "qualifies_for_eu261_threshold": is_eligible_delay,
            "summary": f"Flight {clean_fn} delayed by {data['delay_minutes']} minutes ({round(data['delay_minutes']/60.0, 1)} hours). Exceeds EU261 3-hour minimum threshold." if is_eligible_delay else "Delay is under 3 hours."
        }
    }

    return json.dumps(result, indent=2)
