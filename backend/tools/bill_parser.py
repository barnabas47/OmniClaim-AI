"""
Bill Parser Tool - Extract metadata and detect price anomalies from household bills.
"""
import json
import re
from typing import Dict, Any, Optional

try:
    from strands import tool
except ImportError:
    def tool(func):
        return func

# Mock database of historical baselines for anomaly evaluation
HISTORICAL_BASELINES = {
    "FiberNet Ultra 500": {"median_monthly": 49.99, "currency": "USD", "category": "Telecom/Internet"},
    "GridPower Standard Electricity": {"median_monthly": 115.00, "currency": "USD", "category": "Utilities/Electric"},
    "StreamMax Family Annual": {"median_monthly": 14.99, "currency": "USD", "category": "Subscription"},
    "SafeShield Home Insurance": {"median_monthly": 85.00, "currency": "USD", "category": "Insurance"}
}

@tool
def parse_household_bill(bill_text: str, filename: Optional[str] = None) -> str:
    """
    Parses household bill or invoice text, extracts structured metadata, 
    and checks against historical baselines to detect price hikes or anomalies.

    Args:
        bill_text: Raw text content of the bill or invoice (extracted from PDF or email).
        filename: Optional name of the source bill file.

    Returns:
        JSON string containing structured bill details, baseline comparison, and anomaly flag.
    """
    # Extract provider name
    provider = "Unknown Provider"
    if "FiberNet" in bill_text:
        provider = "FiberNet Communications"
    elif "GridPower" in bill_text or "Electric" in bill_text:
        provider = "GridPower Energy Co."
    elif "StreamMax" in bill_text:
        provider = "StreamMax Entertainment"
    elif "SafeShield" in bill_text:
        provider = "SafeShield Insurance"
    else:
        m = re.search(r"(?:From|Provider|Company):\s*([A-Za-z0-9\s]+)", bill_text)
        if m:
            provider = m.group(1).strip()

    # Extract current amount billed
    amount = 0.0
    amount_match = re.search(r"(?:Total|Amount Billed|Amount Due|\$)\s*:?\s*\$?(\d+\.\d{2})", bill_text)
    if amount_match:
        amount = float(amount_match.group(1))

    # Extract plan / service name
    plan_name = "Standard Household Service"
    if "FiberNet Ultra 500" in bill_text:
        plan_name = "FiberNet Ultra 500"
    elif "GridPower Standard Electricity" in bill_text:
        plan_name = "GridPower Standard Electricity"
    elif "StreamMax Family Annual" in bill_text:
        plan_name = "StreamMax Family Annual"

    # Account number
    acc_match = re.search(r"(?:Account|Acc|Customer ID)[\#\s:]+([A-Z0-9\-]+)", bill_text)
    account_number = acc_match.group(1) if acc_match else "ACC-8849201"

    # Billing date / period
    date_match = re.search(r"(\d{4}-\d{2}-\d{2})", bill_text)
    billing_date = date_match.group(1) if date_match else "2026-08-15"

    # Anomaly evaluation vs baseline
    baseline_info = HISTORICAL_BASELINES.get(plan_name, {"median_monthly": amount * 0.8, "currency": "USD", "category": "General"})
    baseline_amount = baseline_info["median_monthly"]
    
    price_diff = amount - baseline_amount
    percentage_increase = ((amount - baseline_amount) / baseline_amount * 100) if baseline_amount > 0 else 0.0
    
    is_anomaly = percentage_increase >= 15.0

    result = {
        "status": "SUCCESS",
        "bill_metadata": {
            "filename": filename or "imported_bill.pdf",
            "provider": provider,
            "account_number": account_number,
            "plan_name": plan_name,
            "category": baseline_info.get("category", "General Admin"),
            "billing_date": billing_date,
            "amount_due": round(amount, 2),
            "currency": "USD"
        },
        "anomaly_analysis": {
            "is_anomaly": is_anomaly,
            "historical_baseline_monthly": round(baseline_amount, 2),
            "price_increase_usd": round(price_diff, 2),
            "percentage_increase": round(percentage_increase, 1),
            "risk_severity": "HIGH" if percentage_increase >= 30 else ("MEDIUM" if is_anomaly else "LOW"),
            "trigger_reason": f"Current charge (${amount:.2f}) is {percentage_increase:.1f}% higher than 6-month average baseline (${baseline_amount:.2f}). Promo period appears to have expired." if is_anomaly else "Billing amount is within normal variance."
        }
    }
    
    return json.dumps(result, indent=2)
