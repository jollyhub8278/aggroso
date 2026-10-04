import json
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from ..database import get_db
from ..models import Claim
from ..schemas import ClaimCreate, ClaimOut
from ..services.ai_review import review_with_ai
from ..services.policy import get_policy
from ..services.validation import validate_claim

router = APIRouter(prefix="/claims", tags=["claims"])


@router.get("", response_model=list[ClaimOut])
def list_claims(db: Session = Depends(get_db)):
    claims = db.query(Claim).order_by(Claim.id.desc()).all()
    result = []

    for claim in claims:
        latest_review = claim.reviews[-1] if claim.reviews else None
        item = ClaimOut.model_validate(claim).model_dump()
        item["review_status"] = latest_review.action if latest_review else None
        result.append(item)

    return result


@router.get("/{claim_id}")
def get_claim(claim_id: int, db: Session = Depends(get_db)):
    claim = db.get(Claim, claim_id)
    if not claim:
        raise HTTPException(404, "Claim not found")
    return {
        "claim": claim,
        "validation": validate_claim(db, claim),
        "reviews": claim.reviews,
        "review_status": claim.reviews[-1].action if claim.reviews else None,
        "policy": get_policy(db, claim.category),
    }


@router.post("", response_model=ClaimOut)
def create_claim(data: ClaimCreate, db: Session = Depends(get_db)):
    claim = Claim(**data.model_dump())
    db.add(claim)
    db.commit()
    db.refresh(claim)

    result = review_with_ai(db, claim)
    claim.ai_category = result.get("category")
    claim.ai_confidence = result.get("confidence")
    claim.ai_status = result.get("status")
    claim.ai_reason = result.get("reason")
    claim.missing_information = json.dumps(result.get("missing_information", []))
    db.commit()
    db.refresh(claim)
    return claim


@router.post("/{claim_id}/review")
def add_review(claim_id: int, data, db: Session = Depends(get_db)):
    claim = db.get(Claim, claim_id)
    if not claim:
        raise HTTPException(404, "Claim not found")
    return {"message": "Use the /reviews endpoint"}
