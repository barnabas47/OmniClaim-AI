"""
Market Search Tool - Research competitor rates and compute switching vs retention savings.
"""
import json
from typing import Optional

try:
    from strands import tool
except ImportError:
    def tool(func):
        return func

# Benchmark competitor offerings database
COMPETITOR_DATABASE = {
    "Telecom/Internet": [
        {
            "provider": "FiberNet Communications",
            "plan": "Loyalty Retention Discount Plan (500 Mbps)",
            "monthly_rate": 54.99,
            "contract_type": "12-month lock",
            "setup_fee": 0.00,
            "is_retention_offer": True,
            "features": ["500 Mbps Symmetric Fiber", "Free Wi-Fi 6 Gateway", "No termination fee"]
        },
        {
            "provider": "Apex Gigaband",
            "plan": "Ultra Fiber 600",
            "monthly_rate": 44.99,
            "contract_type": "No contract",
            "setup_fee": 0.00,
            "is_retention_offer": False,
            "features": ["600 Mbps Download/Upload", "Free mesh router", "$100 Visa Card Bonus"]
        },
        {
            "provider": "Veloce Fiber",
            "plan": "GigaHome Starter",
            "monthly_rate": 49.00,
            "contract_type": "24-month rate guarantee",
            "setup_fee": 25.00,
            "is_retention_offer": False,
            "features": ["500 Mbps Fiber", "Unlimited data", "Free installation"]
        }
    ],
    "Utilities/Electric": [
        {
            "provider": "EcoGreen Energy",
            "plan": "100% Wind Fixed 12M",
            "monthly_rate": 89.00,
            "contract_type": "12-month fixed rate",
            "setup_fee": 0.00,
            "is_retention_offer": False,
            "features": ["100% renewable power", "Zero early termination fee", "Free smart thermostat"]
        },
        {
            "provider": "GridPower Energy Co.",
            "plan": "EcoSaver Preferred Tariff",
            "monthly_rate": 95.00,
            "contract_type": "Month-to-month",
            "setup_fee": 0.00,
            "is_retention_offer": True,
            "features": ["Existing customer discount", "Off-peak EV charging rate"]
        }
    ]
}

@tool
def search_market_competitor_rates(category: str, current_provider: str, current_monthly_rate: float) -> str:
    """
    Searches available market competitor rates and current provider retention plans.
    Calculates estimated monthly and annual savings compared to the current rate.

    Args:
        category: Service category (e.g. 'Telecom/Internet' or 'Utilities/Electric').
        current_provider: Name of the current service provider.
        current_monthly_rate: The elevated monthly cost currently being paid.

    Returns:
        JSON string containing available competitive alternatives, retention packages, and savings calculations.
    """
    cat_key = "Telecom/Internet" if "Internet" in category or "Telecom" in category else ("Utilities/Electric" if "Electric" in category or "Utility" in category or "Power" in category else "Telecom/Internet")
    
    options = COMPETITOR_DATABASE.get(cat_key, COMPETITOR_DATABASE["Telecom/Internet"])
    
    analyzed_options = []
    best_option = None
    max_annual_savings = -1.0

    for opt in options:
        monthly_savings = current_monthly_rate - opt["monthly_rate"]
        annual_savings = monthly_savings * 12.0
        
        opt_data = {
            "provider": opt["provider"],
            "plan": opt["plan"],
            "monthly_rate": opt["monthly_rate"],
            "is_retention_offer": opt["is_retention_offer"],
            "contract_type": opt["contract_type"],
            "features": opt["features"],
            "monthly_savings": round(monthly_savings, 2),
            "annual_savings": round(annual_savings, 2),
            "percentage_saved": round((monthly_savings / current_monthly_rate) * 100, 1) if current_monthly_rate > 0 else 0
        }
        analyzed_options.append(opt_data)

        if annual_savings > max_annual_savings:
            max_annual_savings = annual_savings
            best_option = opt_data

    result = {
        "status": "SUCCESS",
        "query": {
            "category": cat_key,
            "current_provider": current_provider,
            "current_rate": current_monthly_rate
        },
        "market_options": analyzed_options,
        "recommendation": {
            "best_option_provider": best_option["provider"] if best_option else "Apex Gigaband",
            "best_option_plan": best_option["plan"] if best_option else "Ultra Fiber 600",
            "recommended_monthly_rate": best_option["monthly_rate"] if best_option else 44.99,
            "estimated_annual_savings": round(max_annual_savings, 2),
            "summary": f"Switching to {best_option['provider']} ({best_option['plan']}) will save ${max_annual_savings:.2f}/year (${best_option['monthly_savings']:.2f}/month), representing a {best_option['percentage_saved']}% reduction."
        }
    }
    
    return json.dumps(result, indent=2)
