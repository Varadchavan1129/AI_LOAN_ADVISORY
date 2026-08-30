"""
Pydantic schemas for the natural-language query endpoint (/chat/query).
"""

from pydantic import BaseModel
from typing import Any, Optional


class QueryRequest(BaseModel):
    message: str


class QueryResponse(BaseModel):
    """
    Unified response for all natural-language query types.

    type values:
      "emi"          – EMI calculation result
      "eligibility"  – Eligibility check result
      "max_loan"     – Maximum loan calculation
      "dti"          – Debt-to-income ratio result
      "general"      – General loan knowledge answer
      "missing_info" – Not enough info to answer; ask follow-up
      "error"        – Something went wrong
    """
    type:    str
    message: str
    data:    Optional[Any] = None
