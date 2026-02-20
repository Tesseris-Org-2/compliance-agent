import json
from typing import Dict, Any

# Mock Database of Issuer Disclosures
MOCK_DISCLOSURES = {
    "issuer_a123": {
        "status": "active",
        "latest_filing_date": "2026-01-15",
        "kyc_aml_expiry": "2026-12-31",
        "financial_audit_status": "passed",
        "audit_notes": "No material weakness found. Cash reserves verified."
    },
    "issuer_b456": {
        "status": "active",
        "latest_filing_date": "2025-10-01",  # Overdue
        "kyc_aml_expiry": "2026-03-01",
        "financial_audit_status": "pending_review",
        "audit_notes": "Awaiting final Q4 figures."
    }
}

def monitor_disclosures(issuer_id: str) -> str:
    """
    Fetches the latest compliance disclosures for a given issuer.
    
    Args:
        issuer_id: The unique identifier for the bond issuer (e.g., 'issuer_a123')
        
    Returns:
        JSON string containing the issuer's compliance data or an error message.
    """
    
    record = MOCK_DISCLOSURES.get(issuer_id)
    if record:
        return json.dumps(record)
    else:
        return json.dumps({"error": f"No disclosure records found for issuer {issuer_id}"})
