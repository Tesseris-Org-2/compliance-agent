import json
import logging
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage
from langchain_openai import ChatOpenAI
from state import AgentState, RiskReport
from tools.validate import validate_data

logger = logging.getLogger(__name__)

from agents.llm import get_gemini_agent

# Remove old get_risk_agent definition - we'll use the central one

def risk_node(state: AgentState):
    """
    The Risk Agent audits on-chain token supply against off-chain reserves.
    """
    logger.info("---| RISK AGENT ACTIVATED |---")
    state["current_agent"] = "Risk Agent"
    
    asset_id = state.get("asset_id")
    if not asset_id:
        error_msg = "No asset_id provided in state for risk check."
        logger.error(error_msg)
        state["risk_report"] = {"status": "FAIL", "metrics": {}, "flags": [error_msg]}
        return state

    # 1. Fetch data using the validator tool
    risk_data_str = validate_data(asset_id)
    risk_data = json.loads(risk_data_str)
    
    if "error" in risk_data:
        state["risk_report"] = {"status": "FAIL", "metrics": {}, "flags": [risk_data["error"]]}
        return state
        
    # 2. Use LLM to analyze the risk profile
    system_prompt = """You are an expert quantitative risk auditor for asset-backed tokens.
    Analyze the provided collateralization ratio and reserves data.
    Determine if the tokenized bond is financially healthy based on these rules:
    - The collateralization ratio (off-chain reserves / on-chain supply) must be >= 1.0.
    - Status can be "PASS", "FAIL", or "WARNING".
    
    Return a JSON response matching the following schema:
    {
      "status": "PASS" or "FAIL" or "WARNING",
      "flags": ["list", "of", "risk", "concerns", "if", "any"]
    }
    """
    
    human_prompt = f"Here is the proof of reserve data for {asset_id}:\\n{json.dumps(risk_data, indent=2)}"
    
    messages = [
        SystemMessage(content=system_prompt),
        HumanMessage(content=human_prompt)
    ]
    
    try:
        llm = get_gemini_agent()
        if not llm:
            raise ValueError("No LLM initialized")
        response = llm.invoke(messages, response_format={"type": "json_object"})
        result = json.loads(response.content)
        
        report: RiskReport = {
            "status": result.get("status", "FAIL"),
            "metrics": {
                "collateral_ratio": risk_data.get("collateralization_ratio", 0),
                "on_chain_supply": risk_data.get("on_chain_supply", 0),
                "off_chain_reserves": risk_data.get("off_chain_reserves", 0)
            },
            "flags": result.get("flags", [])
        }
        
        state["risk_report"] = report
        state["messages"].append(AIMessage(content=f"Risk audit completed. Status: {report['status']}"))
        logger.info(f"Risk audit for {asset_id} completed with status: {report['status']}")
        
    except Exception as e:
        logger.error(f"Error during LLM risk analysis: {str(e)}")
        state["risk_report"] = {
             "status": "FAIL", 
             "metrics": {}, 
             "flags": [f"System Error: {str(e)}"]
        }
        
    return state
