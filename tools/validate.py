import json
from typing import Dict, Any

# Mock Database of on-chain / off-chain balances
MOCK_COLLATERAL = {
    "bond_usd_123": {
        "on_chain_supply": {"value": 10000000.0, "currency": "USD"},
        "off_chain_reserves": {"value": 10500000.0, "currency": "USD"},
        "reserve_bank": "Global Standard Bank"
    },
    "bond_eur_456": {
         "on_chain_supply": {"value": 5000000.0, "currency": "EUR"},
         "off_chain_reserves": {"value": 4900000.0, "currency": "EUR"}, # Undercollateralized
         "reserve_bank": "Euro Trust Bank"
    }
}

def validate_data(asset_id: str) -> str:
    """
    Validates the on-chain supply of a tokenized bond against its off-chain cash reserves.
    
    Args:
        asset_id: The identifier for the tokenized asset (e.g., 'bond_usd_123')
        
    Returns:
        JSON string containing the risk data and collateralization ratio or an error message.
    """
    data = MOCK_COLLATERAL.get(asset_id)
    if data:
         on_chain = data["on_chain_supply"]["value"]
         off_chain = data["off_chain_reserves"]["value"]
         
         # Calculate ratio
         ratio = off_chain / on_chain if on_chain > 0 else 0
         
         result = {
              "asset_id": asset_id,
              "on_chain_supply": on_chain,
              "off_chain_reserves": off_chain,
              "collateralization_ratio": round(ratio, 4),
              "health": "healthy" if ratio >= 1.0 else "undercollateralized"
         }
         return json.dumps(result)
    else:
        return json.dumps({"error": f"No collateral data found for asset {asset_id}"})
