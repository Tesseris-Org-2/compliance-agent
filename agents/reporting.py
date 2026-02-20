import logging
from langchain_core.messages import AIMessage
from state import AgentState, Attestation
from tools.attest import generate_attestation
import json

logger = logging.getLogger(__name__)

def reporting_node(state: AgentState):
    """
    The Reporting Agent collects the states of Compliance and Risk,
    creates a combined payload, and generates a cryptographic attestation.
    """
    logger.info("---| REPORTING AGENT ACTIVATED |---")
    state["current_agent"] = "Reporting Agent"
    
    compliance_report = state.get("compliance_report")
    risk_report = state.get("risk_report")
    
    if not compliance_report or not risk_report:
        logger.error("Missing reports from earlier stages. Cannot generate attestation.")
        state["workflow_status"] = "FAILED"
        return state
        
    c_status = compliance_report.get("status") == "PASS"
    r_status = risk_report.get("status") == "PASS"
    
    data_payload = {
        "issuer": state.get("issuer_id"),
        "asset": state.get("asset_id"),
        "compliance": compliance_report,
        "risk": risk_report
    }
    
    # Generate the attestation using the oracle tool
    attestation_str = generate_attestation(c_status, r_status, data_payload)
    attestation_data = json.loads(attestation_str)
    
    attestation: Attestation = {
        "signature": attestation_data["signature"],
        "payload": attestation_data["payload"],
        "timestamp": attestation_data["timestamp"]
    }
    
    state["final_attestation"] = attestation
    
    final_status = "COMPLETED" if (c_status and r_status) else "FAILED (Compliance/Risk Breach)"
    state["workflow_status"] = final_status
    
    state["messages"].append(AIMessage(content=f"Attestation generated. Workflow Status: {final_status}"))
    logger.info(f"Reporting completed. Attestation Signature: {attestation['signature']}")
    
    return state
