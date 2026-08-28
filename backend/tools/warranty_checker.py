"""
Warranty & Contract Expiry Checker Tool - Monitors warranties, trial periods, and contract locks.
"""
import json
from datetime import datetime, timedelta

try:
    from strands import tool
except ImportError:
    def tool(func):
        return func

# Mock database of active household contracts and warranties
MOCK_CONTRACTS = [
    {
        "item_id": "CTR-101",
        "title": "CloudStorage Pro 2TB Annual",
        "category": "Software Subscription",
        "provider": "CloudVault Inc.",
        "monthly_cost": 9.99,
        "expiry_date": "2026-08-28",
        "auto_renews": True,
        "notice_days_required": 3
    },
    {
        "item_id": "CTR-102",
        "title": "Smart OLED TV 65 Inch Extended Warranty",
        "category": "Device Warranty",
        "provider": "TechGuard Care",
        "monthly_cost": 0.00,
        "expiry_date": "2026-09-10",
        "auto_renews": False,
        "notice_days_required": 0
    },
    {
        "item_id": "CTR-103",
        "title": "FiberNet 12-Month Promo Lock",
        "category": "Telecom Contract",
        "provider": "FiberNet Communications",
        "monthly_cost": 49.99,
        "expiry_date": "2026-08-31",
        "auto_renews": True,
        "notice_days_required": 14
    }
]

@tool
def track_contract_expirations(days_ahead: int = 30) -> str:
    """
    Checks all tracked household warranties, free trial periods, and contract expirations.
    Identifies items expiring within the specified time window.

    Args:
        days_ahead: Number of days into the future to scan for expirations. Default is 30 days.

    Returns:
        JSON string listing upcoming expirations, risk assessments, and recommended proactive actions.
    """
    today = datetime.strptime("2026-08-22", "%Y-%m-%d")
    cutoff_date = today + timedelta(days=days_ahead)

    expiring_items = []
    
    for item in MOCK_CONTRACTS:
        exp_dt = datetime.strptime(item["expiry_date"], "%Y-%m-%d")
        days_remaining = (exp_dt - today).days

        if 0 <= days_remaining <= days_ahead:
            recommendation = "No action required (will expire cleanly)."
            if item["auto_renews"]:
                recommendation = f"Submit cancellation or renegotiate rate before {item['expiry_date']} to prevent auto-renewal price hike."

            expiring_items.append({
                "item_id": item["item_id"],
                "title": item["title"],
                "category": item["category"],
                "provider": item["provider"],
                "expiry_date": item["expiry_date"],
                "days_remaining": days_remaining,
                "auto_renews": item["auto_renews"],
                "recommendation": recommendation,
                "urgency": "HIGH" if days_remaining <= 7 and item["auto_renews"] else "MEDIUM"
            })

    result = {
        "status": "SUCCESS",
        "scan_date": "2026-08-22",
        "days_window": days_ahead,
        "total_expirations_found": len(expiring_items),
        "items": expiring_items
    }

    return json.dumps(result, indent=2)
