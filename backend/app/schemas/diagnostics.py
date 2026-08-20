from pydantic import BaseModel
from typing import Optional, List


class FactorCorrelation(BaseModel):
    factor: str
    correlation_coefficient: Optional[float] = None
    p_value: Optional[float] = None
    sample_size: int
    insight_text: str


class DiagnosticResponse(BaseModel):
    city_id: int
    factors: List[FactorCorrelation]