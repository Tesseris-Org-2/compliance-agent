import logging
import argparse
from typing import Annotated, Literal
from langgraph.graph import StateGraph, START, END

# Import the state and agent nodes
from state import AgentState
from agents.compliance import compliance_node
from agents.risk import risk_node
from agents.reporting import reporting_node

# Configure simple logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def build_graph() -> StateGraph:
    """
    Constructs the LangGraph StateGraph combining the three compliance agents.
    """
    # Initialize the graph with the typed schema
    workflow = StateGraph(AgentState)
    
    # 1. Add nodes (the agents)
    workflow.add_node("compliance", compliance_node)
    workflow.add_node("risk", risk_node)
    workflow.add_node("reporting", reporting_node)
    
    # 2. Define edges (Control Flow)
    # The workflow goes: START -> compliance -> risk -> reporting -> END
    workflow.add_edge(START, "compliance")
    workflow.add_edge("compliance", "risk")
    workflow.add_edge("risk", "reporting")
    workflow.add_edge("reporting", END)
    
    # Optional: compile with a checkpointer if you needed to persist state
    app = workflow.compile()
    return app

def run_compliance_check(issuer_id: str, asset_id: str):
    logger.info(f"Starting compliance check run for Issuer: {issuer_id} | Asset: {asset_id}")
    
    app = build_graph()
    
    # Define the starting state
    initial_state = {
        "messages": [],
        "issuer_id": issuer_id,
        "asset_id": asset_id,
        "compliance_report": None,
        "risk_report": None,
        "final_attestation": None,
        "workflow_status": "IN_PROGRESS",
        "current_agent": "system"
    }
    
    try:
        # Execute the graph
        final_state = app.invoke(initial_state)
        
        logger.info("---| FINAL ATTESTATION |---")
        if final_state.get('final_attestation'):
             attestation = final_state['final_attestation']
             # Pretty print the final payload
             import json
             print(json.dumps(attestation, indent=2))
        else:
             logger.error("No attestation generated.")

        logger.info(f"Final Workflow Status: {final_state.get('workflow_status')}")
    except Exception as e:
         logger.error(f"Error executing graph: {e}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Run Compliance Multi-Agent System")
    parser.add_argument("--issuer", type=str, default="issuer_a123", help="Issuer ID (e.g., issuer_a123 or issuer_b456)")
    parser.add_argument("--asset", type=str, default="bond_usd_123", help="Asset ID (e.g., bond_usd_123 or bond_eur_456)")
    
    args = parser.parse_args()
    run_compliance_check(args.issuer, args.asset)
