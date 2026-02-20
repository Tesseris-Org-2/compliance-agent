import json
import hashlib
from datetime import datetime, timezone
from typing import Dict, Any

def generate_attestation(compliance_passed: bool, risk_passed: bool, data: Dict[str, Any]) -> str:
    """
    Generates a cryptographic proxy attestation given the results of the compliance and risk agents.
    
    Args:
         compliance_passed: True if the compliance agent approved.
         risk_passed: True if the risk agent approved.
         data: The combined data payload from the two previous steps.
         
    Returns:
         JSON string representing the attestation payload and signature.
    """
    timestamp = datetime.now(timezone.utc).isoformat()
    
    payload = {
         "compliance_status": "PASS" if compliance_passed else "FAIL",
         "risk_status": "PASS" if risk_passed else "FAIL",
         "underlying_data": data,
         "timestamp": timestamp,
         "attestor_id": "oracle_node_77x"
    }
    
    # Mock signature generation (hashing the payload)
    payload_str = json.dumps(payload, sort_keys=True)
    signature = hashlib.sha256(payload_str.encode('utf-8')).hexdigest()
    
    attestation = {
        "signature": f"0x{signature}",
        "payload": payload,
        "timestamp": timestamp
    }
    
    return json.dumps(attestation)
