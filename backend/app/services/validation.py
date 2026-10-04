from datetime import date
from sqlalchemy.orm import Session
from ..models import Claim, Policy


def find_duplicates(db: Session, claim: Claim):
    return db.query(Claim).filter(
        Claim.id != claim.id,
        Claim.claimant == claim.claimant,
        Claim.date == claim.date,
        Claim.amount == claim.amount,
        Claim.currency == claim.currency,
        Claim.category == claim.category,
        Claim.description == claim.description,
    ).all()


def validate_claim(db: Session, claim: Claim):
    issues = []
    warnings = []

    if not claim.claimant.strip():
        issues.append("Claimant is required")
    if not claim.category.strip():
        issues.append("Category is required")
    if not claim.description.strip():
        issues.append("Description is required")
    if claim.amount <= 0:
        issues.append("Amount must be greater than zero")
    if claim.date > date.today():
        issues.append("Claim date cannot be in the future")
    if not claim.receipt_available:
        warnings.append("Receipt is missing")

    policy = db.query(Policy).filter(Policy.category == claim.category).first()
    if policy and policy.limit is not None and claim.currency == policy.currency and claim.amount > policy.limit:
        issues.append(f"Amount exceeds the {policy.currency} {policy.limit:,.0f} category limit")

    duplicates = find_duplicates(db, claim)
    if duplicates:
        issues.append("Possible duplicate claim found")

    return {"issues": issues, "warnings": warnings, "duplicate_ids": [x.id for x in duplicates]}
