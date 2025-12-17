from pydantic import BaseModel
from typing import Optional


class LoanInput(BaseModel):
    # Common fields from the dataset; optional to allow partial inputs
    income: Optional[float] = None
    employment_length: Optional[str] = None
    purpose: Optional[str] = None
    term: Optional[str] = None
    credit_score: Optional[float] = None
    monthly_debt: Optional[float] = None
    years_of_credit_history: Optional[float] = None


class ClassificationResponse(BaseModel):
    loan_status: str
    probability: Optional[float]


class RegressionResponse(BaseModel):
    predicted_value: float


class ClusterResponse(BaseModel):
    cluster: int
