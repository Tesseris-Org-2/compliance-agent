import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from main import run_compliance_check, build_graph
import json

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Compile the LangGraph app once on startup
ml_models = {}

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Load the LangGraph workflow
    logger.info("Building LangGraph compliance workflow...")
    ml_models["workflow"] = build_graph()
    yield
    # Clean up (if needed)

app = FastAPI(
    title="Compliance Multi-Agent System",
    description="LangGraph multi-agent API for Tokenized Bond compliance",
    version="1.0.0",
    lifespan=lifespan
)

class TaskRequest(BaseModel):
    issuer_id: str
    asset_id: str

@app.get("/health")
async def health_check():
    """
    Simple health check endpoint to confirm the API in the container is running.
    """
    return {"status": "ok", "message": "Compliance Agent API is healthy"}

@app.get("/catalog")
async def get_catalog():
    """
    Returns the agent's service catalog and pricing in Sepolia ETH.
    """
    return {
        "agent_name": "Compliance & Risk Oracle",
        "description": "Multi-agent LangGraph workflow for tokenized RWA audit and compliance verification.",
        "services": [
            {
                "service_id": "full_compliance_audit",
                "description": "End-to-end qualitative disclosure monitoring and quantitative collateral risk analysis yielding a cryptographic attestation.",
                "price": "0.001",
                "currency": "ETH",
                "network": "Sepolia"
            }
        ]
    }

@app.post("/task")
async def execute_task(request: TaskRequest):
    """
    Triggers the multi-agent workflow for a specific issuer and asset.
    """
    logger.info(f"Received task request for Issuer: {request.issuer_id} | Asset: {request.asset_id}")
    
    workflow = ml_models.get("workflow")
    if not workflow:
        raise HTTPException(status_code=500, detail="Workflow not initialized")
        
    initial_state = {
        "messages": [],
        "issuer_id": request.issuer_id,
        "asset_id": request.asset_id,
        "compliance_report": None,
        "risk_report": None,
        "final_attestation": None,
        "workflow_status": "IN_PROGRESS",
        "current_agent": "system"
    }
    
    try:
        # Execute the LangGraph workflow directly via the compiled app
        final_state = workflow.invoke(initial_state)
        
        # We don't want to return the full conversation history to the client, just the results
        return {
            "workflow_status": final_state.get("workflow_status"),
            "compliance_report": final_state.get("compliance_report"),
            "risk_report": final_state.get("risk_report"),
            "final_attestation": final_state.get("final_attestation")
        }
        
    except Exception as e:
        logger.error(f"Error during graph execution: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
