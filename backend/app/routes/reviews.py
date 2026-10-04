from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from ..database import get_db
from ..models import Claim, Review
from ..schemas import ReviewCreate, ReviewOut

router = APIRouter(prefix="/reviews", tags=["reviews"])


@router.post("/{claim_id}", response_model=ReviewOut)
def create_review(claim_id: int, data: ReviewCreate, db: Session = Depends(get_db)):
    claim = db.get(Claim, claim_id)
    if not claim:
        raise HTTPException(404, "Claim not found")

    allowed = {"approve", "reject", "clarification", "override"}
    if data.action not in allowed:
        raise HTTPException(400, f"Action must be one of: {', '.join(sorted(allowed))}")
    if data.action == "override" and not data.reason:
        raise HTTPException(400, "Override requires a reason")

    review = Review(claim_id=claim_id, **data.model_dump())
    db.add(review)
    db.commit()
    db.refresh(review)
    return review
