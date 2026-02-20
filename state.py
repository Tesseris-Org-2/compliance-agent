from typing import TypedDict, Annotated, List, Any
import operator
from langchain_core.messages import BaseMessage

class ComplianceReport(TypedDict):
    status: str  # e.g., "PASS", "FAIL"
    findings: List[str]
    documents_reviewed: List[str]

class RiskReport(TypedDict):
    status: str  # e.g., "PASS", "FAIL", "WARNING"
    metrics: dict[str, Any]  # e.g., {"collateral_ratio": 1.05, "on_chain_supply": 10000}
    flags: List[str]

class Attestation(TypedDict):
    signature: str
    payload: dict[str, Any]
    timestamp: str

class AgentState(TypedDict):
    messages: Annotated[List[BaseMessage], operator.add]
    issuer_id: str
    asset_id: str
    # Results from agents
    compliance_report: ComplianceReport | None
    risk_report: RiskReport | None
    final_attestation: Attestation | None
    
    # Control flags
    workflow_status: str # "IN_PROGRESS", "COMPLETED", "FAILED"
    current_agent: str
