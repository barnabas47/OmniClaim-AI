"""
Form Filler & Letter Generator Tool - Pre-fills switching applications and dispute letters for HITL approval.
"""
import json
from typing import Dict, Any

try:
    from strands import tool
except ImportError:
    def tool(func):
        return func

@tool
def generate_prefilled_action_package(
    customer_name: str,
    account_number: str,
    current_provider: str,
    target_provider: str,
    target_plan: str,
    current_rate: float,
    new_rate: float,
    action_type: str = "SWITCH_PROVIDER"
) -> str:
    """
    Drafts formal price-match dispute letters and pre-fills official service transfer/cancellation forms.

    Args:
        customer_name: Full name of the subscriber.
        account_number: Current subscriber account number.
        current_provider: Name of current service provider.
        target_provider: Name of target new provider or retention division.
        target_plan: Title of target plan.
        current_rate: Current elevated monthly rate ($).
        new_rate: Target monthly rate ($).
        action_type: Either 'SWITCH_PROVIDER' or 'DISPUTE_RETENTION'.

    Returns:
        JSON string containing the pre-filled form fields and the drafted formal letter text.
    """
    annual_savings = (current_rate - new_rate) * 12.0

    if action_type == "DISPUTE_RETENTION":
        letter_subject = f"Urgent: Rate Review Request & Contract Retention Inquiry - Acc #{account_number}"
        letter_body = f"""Date: August 22, 2026

To the Customer Retention & Billing Department of {current_provider},

I am writing regarding my service account #{account_number}. I recently noticed that my monthly bill has increased from ${new_rate:.2f} to ${current_rate:.2f}/month.

As a loyal customer, I value your service, but competing providers in my area (including {target_provider}) are currently offering equivalent 500Mbps+ speeds for ${new_rate:.2f}/month with guaranteed rate locks and no contract lock-in.

Before completing my account transfer to {target_provider}, I would like to request that my account be matched to your current promotional/retention rate of ${new_rate:.2f}/month. 

Please review this request at your earliest convenience. If a rate match cannot be accommodated, please accept this letter as formal authorization to initiate service cancellation at the end of the current billing cycle.

Sincerely,
{customer_name}
Account Holder, #{account_number}
"""
        form_title = f"{current_provider} Retention & Rate Lock Request Form"
        fields = {
            "Form_Type": "Retention_Rate_Adjustment",
            "Account_Holder": customer_name,
            "Account_Number": account_number,
            "Current_Monthly_Fee": f"${current_rate:.2f}",
            "Requested_Matched_Rate": f"${new_rate:.2f}",
            "Target_Competitor_Benchmark": f"{target_provider} ({target_plan})",
            "Authorization_Status": "PENDING_HUMAN_APPROVAL"
        }
    else:
        letter_subject = f"Official Notice of Cancellation & Service Transfer - Acc #{account_number}"
        letter_body = f"""Date: August 22, 2026

To Customer Support at {current_provider},

Please be advised that I am exercising my right to terminate service for account #{account_number} effective at the end of the current billing cycle. 

I am transitioning my primary household service to {target_provider} under their {target_plan} plan. Please issue a final itemized closing invoice to the address on file and confirm that no un-authorized auto-debits will occur following the cancellation date.

Thank you for your assistance.

Sincerely,
{customer_name}
Account Holder, #{account_number}
"""
        form_title = f"{target_provider} Fast-Track Customer Onboarding & Transfer Application"
        fields = {
            "Application_ID": "APP-2026-99201",
            "Applicant_Name": customer_name,
            "Previous_Provider": current_provider,
            "Previous_Account_Number": account_number,
            "Selected_New_Plan": target_plan,
            "New_Monthly_Rate": f"${new_rate:.2f}/month",
            "Estimated_Annual_Savings": f"${annual_savings:.2f}/year",
            "Number_Portability_Requested": True,
            "Installation_Date": "2026-09-01 (Flexible)",
            "Terms_Accepted": "PRE_CHECKED_BY_AGENT",
            "Human_Signature_Status": "REQUIRES_1CLICK_APPROVAL"
        }

    action_package = {
        "status": "SUCCESS",
        "action_type": action_type,
        "summary": {
            "form_title": form_title,
            "target_provider": target_provider,
            "projected_annual_savings": round(annual_savings, 2),
            "human_action_required": "Review pre-filled document and click 'Approve & Transmit'."
        },
        "prefilled_form": {
            "title": form_title,
            "fields": fields
        },
        "drafted_letter": {
            "subject": letter_subject,
            "body": letter_body
        }
    }

    return json.dumps(action_package, indent=2)
