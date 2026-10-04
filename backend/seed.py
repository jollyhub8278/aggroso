from datetime import date, timedelta

from app.database import Base, SessionLocal, engine
from app.models import Policy, Claim


Base.metadata.create_all(bind=engine)

db = SessionLocal()


# Seed policies
if db.query(Policy).count() == 0:
    policies = [
        Policy(
            category="Business Meals",
            title="Business Meals Policy",
            limit=10000,
            content="Business meals are allowed when there is a documented business purpose. Claims above INR 10,000 per claim require review. The receipt and attendee information should be available.",
        ),
        Policy(
            category="Travel",
            title="Travel Policy",
            limit=50000,
            content="Air, rail and bus travel for approved business trips is reimbursable. Claims should include the business purpose and receipt. Premium upgrades require prior approval.",
        ),
        Policy(
            category="Accommodation",
            title="Accommodation Policy",
            limit=12000,
            content="Hotel accommodation is reimbursable up to INR 12,000 per night. A receipt and business travel purpose are required.",
        ),
        Policy(
            category="Transportation",
            title="Local Transportation Policy",
            limit=5000,
            content="Reasonable taxi, rideshare, metro and parking expenses for business travel are reimbursable. A receipt should be provided when available.",
        ),
        Policy(
            category="Miscellaneous",
            title="Miscellaneous Expenses Policy",
            limit=3000,
            content="Other reasonable business expenses may be reimbursed up to INR 3,000 when supported by a receipt and business purpose.",
        ),
    ]

    db.add_all(policies)
    db.commit()


# Seed demo claims
samples = [
    Claim(
        claimant="Priya Sharma",
        date=date.today() - timedelta(days=2),
        category="Business Meals",
        amount=12500,
        currency="INR",
        description="Dinner with client ABC Corp",
        receipt_available=True,
        ai_category="Business Meals",
        ai_confidence=0.92,
        ai_status="needs_review",
        ai_reason="The claim is a business meal but exceeds the configured category limit.",
    ),
    Claim(
        claimant="Amit Verma",
        date=date.today() - timedelta(days=4),
        category="Transportation",
        amount=850,
        currency="INR",
        description="Uber from office to client meeting",
        receipt_available=False,
        ai_category="Transportation",
        ai_confidence=0.94,
        ai_status="needs_clarification",
        ai_reason="The description matches transportation policy, but the receipt is missing.",
    ),
    Claim(
        claimant="Rahul Mehta",
        date=date.today() - timedelta(days=7),
        category="Travel",
        amount=4200,
        currency="INR",
        description="Train ticket for approved client visit",
        receipt_available=True,
        ai_category="Travel",
        ai_confidence=0.96,
        ai_status="compliant",
        ai_reason="The claim matches the configured category policy and deterministic checks passed.",
    ),
]


# Only add demo claims that are not already present
for sample in samples:
    existing = db.query(Claim).filter(
        Claim.claimant == sample.claimant,
        Claim.date == sample.date,
        Claim.category == sample.category,
        Claim.amount == sample.amount,
        Claim.currency == sample.currency,
        Claim.description == sample.description,
    ).first()

    if not existing:
        db.add(sample)

db.commit()

db.close()

print("Seed complete")