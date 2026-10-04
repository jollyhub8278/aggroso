from sqlalchemy.orm import Session
from ..models import Policy


def get_policy(db: Session, category: str):
    return db.query(Policy).filter(Policy.category == category).first()


def retrieve_policy_sections(db: Session, category: str, description: str):
    policy = get_policy(db, category)
    if policy:
        return [policy]

    terms = set(description.lower().split())
    policies = db.query(Policy).all()
    scored = []
    for item in policies:
        score = sum(1 for word in item.content.lower().split() if word in terms)
        scored.append((score, item))
    scored.sort(key=lambda x: x[0], reverse=True)
    return [item for score, item in scored[:2] if score > 0]
