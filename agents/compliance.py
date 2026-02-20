import json
import logging
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage
from langchain_openai import ChatOpenAI
from state import AgentState, ComplianceReport
from tools.monitor import monitor_disclosures

logger = logging.getLogger(__name__)

from agents.llm import get_gemini_agent

# Remove old get_compliance_agent definition completely - we'll just use the new one inline

def compliance_node(state: AgentState):
    """
    The Compliance Agent monitors issuer disclosures and checks them against rules.
    """
    logger.info("---| COMPLIANCE AGENT ACTIVATED |---")
    state["current_agent"] = "Compliance Agent"
    
    issuer_id = state.get("issuer_id")
    if not issuer_id:
        error_msg = "No issuer_id provided in state for compliance check."
        logger.error(error_msg)
        state["compliance_report"] = {"status": "FAIL", "findings": [error_msg], "documents_reviewed": []}
        return state

    # 1. Fetch data using the tool
    disclosure_data_str = monitor_disclosures(issuer_id)
    disclosure_data = json.loads(disclosure_data_str)
    
    if "error" in disclosure_data:
        state["compliance_report"] = {"status": "FAIL", "findings": [disclosure_data["error"]], "documents_reviewed": []}
        return state
        
    # 2. Use LLM to analyze compliance
    system_prompt = """You are an expert financial compliance officer auditing tokenized bond issuers.
    Analyze the provided issuer disclosure data.
    Determine if the issuer is compliant based on these rules:
    - Status must be 'active'
    - KYC/AML expiry must be in the future (relative to 2026)
    - Financial audit status must be 'passed'
    
    Return a JSON response matching the following schema:
    {
      "status": "PASS" or "FAIL",
      "findings": ["list", "of", "reasons", "for", "status"]
    }
    """
    
    human_prompt = f"Here is the disclosure data for {issuer_id}:\\n{json.dumps(disclosure_data, indent=2)}"
    
    messages = [
        SystemMessage(content=system_prompt),
        HumanMessage(content=human_prompt)
    ]
    
    try:
        llm = get_gemini_agent()
        if not llm:
            raise ValueError("No LLM initialized")
        # Enforcing JSON output
        response = llm.invoke(messages, response_format={"type": "json_object"})
        result = json.loads(response.content)
        
        report: ComplianceReport = {
            "status": result.get("status", "FAIL"),
            "findings": result.get("findings", ["Failed to parse findings"]),
            "documents_reviewed": ["Periodic Issuer Disclosure", "Audit Notes"]
        }
        
        state["compliance_report"] = report
        
        # Add to message history
        state["messages"].append(AIMessage(content=f"Compliance check completed. Status: {report['status']}"))
        logger.info(f"Compliance check for {issuer_id} completed with status: {report['status']}")
        
    except Exception as e:
        logger.error(f"Error during LLM compliance analysis: {str(e)}")
        state["compliance_report"] = {
             "status": "FAIL", 
             "findings": [f"System Error: {str(e)}"], 
             "documents_reviewed": []
        }
        
    return state
