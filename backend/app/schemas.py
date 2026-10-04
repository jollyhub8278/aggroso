from datetime import date, datetime
from pydantic import BaseModel, ConfigDict, Field


class ClaimCreate(BaseModel):
    claimant: str = Field(min_length=1)
    date: date
    category: str = Field(min_length=1)
    amount: float = Field(gt=0)
    currency: str = Field(min_length=1, max_length=10)
    description: str = Field(min_length=1)
    receipt_available: bool


class ReviewCreate(BaseModel):
    action: str
    reason: str | None = None
    reviewer: str = "Reviewer"


class ClaimOut(ClaimCreate):
    model_config = ConfigDict(from_attributes=True)
    id: int
    ai_category: str | None = None
    ai_confidence: float | None = None
    ai_status: str | None = None
    review_status: str | None = None
    ai_reason: str | None = None
    missing_information: str | None = None
    created_at: datetime


class ReviewOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    claim_id: int
    action: str
    reason: str | None
    reviewer: str
    created_at: datetime
