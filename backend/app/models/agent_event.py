from sqlalchemy import Column, String, DateTime
from sqlalchemy.dialects.sqlite import JSON
from sqlalchemy.sql import func
from app.db import Base

class AgentEvent(Base):
    __tablename__ = "agent_events"

    event_id = Column(String, primary_key=True, index=True)
    session_id = Column(String, index=True)
    agent_name = Column(String)
    event_type = Column(String)

    input_snapshot = Column(JSON)
    output_snapshot = Column(JSON)

    timestamp = Column(DateTime(timezone=True), server_default=func.now())
