from pydantic import BaseModel
from typing import Optional

class EligibilityResult(BaseModel):
    decision: str  # approved / rejected / conditional
    dti_ratio: float
    eligibility_score: float
    risk_probability: float
    reason: Optional[str] = None
