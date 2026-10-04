import json
import os
from openai import OpenAI
from sqlalchemy.orm import Session
from .policy import retrieve_policy_sections


def simple_classification(description: str):
    text = description.lower()
    if any(word in text for word in ["hotel", "stay", "accommodation"]):
        return "Accommodation", 0.78
    if any(word in text for word in ["flight", "airfare", "train", "bus"]):
        return "Travel", 0.78
    if any(word in text for word in ["uber", "taxi", "cab", "metro", "parking"]):
        return "Transportation", 0.76
    if any(word in text for word in ["lunch", "dinner", "restaurant", "meal", "client"]):
        return "Business Meals", 0.74
    return "Miscellaneous", 0.45


def review_with_ai(db: Session, claim):
    policies = retrieve_policy_sections(db, claim.category, claim.description)
    policy_text = "\n\n".join(
        f"[{p.category}] {p.title}\n{p.content}" for p in policies
    )

    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        category, confidence = simple_classification(claim.description)
        policy = policies[0] if policies else None
        reason = "No OpenAI API key configured. A lightweight local classification was used."
        if policy:
            reason += f" Relevant policy: {policy.title}."
        missing = []
        if category == "Business Meals" and "attendee" not in claim.description.lower():
            missing.append("Business purpose and attendees")
        return {
            "category": category,
            "confidence": confidence,
            "status": "uncertain" if confidence < 0.6 else "needs_review",
            "reason": reason,
            "missing_information": missing,
            "evidence": [{"section": p.title, "quote": p.content} for p in policies],
        }

    client = OpenAI(api_key=api_key)
    prompt = f"""
You review employee expense claims against company policy.
Return JSON only with keys: category, confidence, status, reason, missing_information, evidence.
status must be one of compliant, needs_clarification, needs_review, uncertain.
confidence must be 0 to 1.
If classification is uncertain, explicitly say so.
Evidence must be a list of objects with section and quote. Only quote from the supplied policy.

Claim:
claimant={claim.claimant}
date={claim.date}
category={claim.category}
amount={claim.amount} {claim.currency}
description={claim.description}
receipt_available={claim.receipt_available}

Policy:
{policy_text}
"""
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        response_format={"type": "json_object"},
        messages=[
            {"role": "system", "content": "You are a precise expense policy reviewer."},
            {"role": "user", "content": prompt},
        ],
        temperature=0,
    )
    return json.loads(response.choices[0].message.content)
