import uuid
from app.db import SessionLocal
from app.models.agent_event import AgentEvent


def log_agent_event(
    session_id: str,
    agent_name: str,
    event_type: str,
    input_snapshot: dict,
    output_snapshot: dict
):
    """
    Persists agent-level events for auditability and analytics.
    """
    db = SessionLocal()
    try:
        event = AgentEvent(
            event_id=str(uuid.uuid4()),
            session_id=session_id,
            agent_name=agent_name,
            event_type=event_type,
            input_snapshot=input_snapshot,
            output_snapshot=output_snapshot
        )
        db.add(event)
        db.commit()
    finally:
        db.close()
