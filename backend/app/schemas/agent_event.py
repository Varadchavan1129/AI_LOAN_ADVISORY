from pydantic import BaseModel
from typing import Dict, Any

class AgentEventCreate(BaseModel):
    session_id: str
    agent_name: str
    event_type: str
    input_snapshot: Dict[str, Any]
    output_snapshot: Dict[str, Any]
