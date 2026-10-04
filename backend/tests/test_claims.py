import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.database import SessionLocal
from app.models import Claim, Review

client = TestClient(app)


@pytest.fixture(autouse=True)
def clean_test_data():
    db = SessionLocal()

    db.query(Review).delete()
    db.query(Claim).delete()

    db.commit()
    db.close()


def claim_data(**overrides):
    data = {
        "claimant": "Test User",
        "date": "2026-09-20",
        "category": "Travel",
        "amount": 2500,
        "currency": "INR",
        "description": "Flight ticket for client meeting",
        "receipt_available": True,
    }

    data.update(overrides)
    return data


def create_claim(**overrides):
    return client.post("/claims", json=claim_data(**overrides))


# ---------------------------------------------------------
# CLAIM CREATION
# ---------------------------------------------------------

def test_get_claims():
    response = client.get("/claims")

    assert response.status_code == 200
    assert isinstance(response.json(), list)


def test_create_claim():
    response = create_claim(
        claimant="Alice Test",
        description="Flight ticket for business meeting",
    )

    assert response.status_code == 200

    data = response.json()

    assert data["claimant"] == "Alice Test"
    assert data["amount"] == 2500
    assert data["currency"] == "INR"


def test_required_claimant():
    response = create_claim(claimant="")

    assert response.status_code == 422


def test_required_description():
    response = create_claim(description="")

    assert response.status_code == 422


def test_negative_amount():
    response = create_claim(amount=-500)

    assert response.status_code == 422


def test_zero_amount():
    response = create_claim(amount=0)

    assert response.status_code == 422


# ---------------------------------------------------------
# VALIDATION
# ---------------------------------------------------------

def test_missing_receipt_is_allowed_but_flagged():
    response = create_claim(
        claimant="No Receipt User",
        receipt_available=False,
        description="Taxi from airport to office",
    )

    assert response.status_code == 200

    claim_id = response.json()["id"]

    review = client.get(f"/claims/{claim_id}")

    assert review.status_code == 200

    validation = review.json()["validation"]

    assert any(
        "receipt" in issue.lower()
        for issue in validation["issues"] + validation["warnings"]
    )


def test_duplicate_claim_is_rejected():
    data = claim_data(
        claimant="Duplicate User",
        date="2026-09-21",
        category="Transportation",
        amount=1800,
        currency="INR",
        description="Taxi from airport to office",
    )

    first = client.post("/claims", json=data)

    assert first.status_code == 200

    second = client.post("/claims", json=data)

    assert second.status_code == 400
    assert "duplicate" in second.json()["detail"].lower()


def test_different_amount_is_not_duplicate():
    data = claim_data(
        claimant="Different Claim User",
        date="2026-09-22",
        category="Travel",
        amount=3000,
        description="Flight ticket",
    )

    first = client.post("/claims", json=data)

    assert first.status_code == 200

    second = client.post(
        "/claims",
        json={
            **data,
            "amount": 3500,
        },
    )

    assert second.status_code == 200


def test_different_date_is_not_duplicate():
    data = claim_data(
        claimant="Different Date User",
        date="2026-09-23",
        category="Travel",
        amount=3000,
        description="Flight ticket",
    )

    first = client.post("/claims", json=data)

    assert first.status_code == 200

    second = client.post(
        "/claims",
        json={
            **data,
            "date": "2026-09-24",
        },
    )

    assert second.status_code == 200


def test_claim_detail():
    response = create_claim(
        claimant="Detail Test User",
        description="Hotel stay for conference",
    )

    assert response.status_code == 200

    claim_id = response.json()["id"]

    response = client.get(f"/claims/{claim_id}")

    assert response.status_code == 200

    data = response.json()

    assert data["claim"]["id"] == claim_id
    assert "validation" in data
    assert "reviews" in data
    assert "policy" in data


def test_non_existing_claim():
    response = client.get("/claims/999999")

    assert response.status_code == 404


def test_meal_limit_is_detected():
    response = create_claim(
        claimant="Limit Test User",
        category="Business Meals",
        amount=12500,
        description="Dinner with client",
    )

    assert response.status_code == 200

    claim_id = response.json()["id"]

    review = client.get(f"/claims/{claim_id}")

    assert review.status_code == 200

    validation = review.json()["validation"]

    assert any(
        "limit" in issue.lower()
        for issue in validation["issues"] + validation["warnings"]
    )


def test_future_date_is_detected():
    response = create_claim(
        claimant="Future Date User",
        date="2030-01-01",
        description="Future travel booking",
    )

    assert response.status_code == 200

    claim_id = response.json()["id"]

    review = client.get(f"/claims/{claim_id}")

    assert review.status_code == 200

    validation = review.json()["validation"]

    assert any(
        "date" in issue.lower()
        for issue in validation["issues"] + validation["warnings"]
    )


# ---------------------------------------------------------
# AI AND POLICY
# ---------------------------------------------------------

def test_ai_review_fields_are_present():
    response = create_claim(
        claimant="AI Test User",
        category="Other",
        description="Team dinner after product launch",
    )

    assert response.status_code == 200

    data = response.json()

    assert "ai_category" in data
    assert "ai_confidence" in data
    assert "ai_status" in data
    assert "ai_reason" in data


def test_policy_is_returned_for_claim():
    response = create_claim(
        claimant="Policy Test User",
        category="Business Meals",
        description="Dinner with customer",
    )

    assert response.status_code == 200

    claim_id = response.json()["id"]

    review = client.get(f"/claims/{claim_id}")

    assert review.status_code == 200

    assert review.json()["policy"] is not None


# ---------------------------------------------------------
# REVIEW ACTIONS
# ---------------------------------------------------------

def test_approve_review():
    response = create_claim(
        claimant="Approve Test User",
        description="Train ticket for office visit",
    )

    assert response.status_code == 200

    claim_id = response.json()["id"]

    review = client.post(
        f"/reviews/{claim_id}",
        json={
            "action": "approve",
            "reason": None,
            "reviewer": "Test Reviewer",
        },
    )

    assert review.status_code in [200, 201]

    data = review.json()

    assert data["action"] == "approve"
    assert data["reviewer"] == "Test Reviewer"


def test_reject_review():
    response = create_claim(
        claimant="Reject Test User",
        description="Personal shopping expense",
    )

    assert response.status_code == 200

    claim_id = response.json()["id"]

    review = client.post(
        f"/reviews/{claim_id}",
        json={
            "action": "reject",
            "reason": "The expense is not business related.",
            "reviewer": "Test Reviewer",
        },
    )

    assert review.status_code in [200, 201]

    data = review.json()

    assert data["action"] == "reject"
    assert data["reason"] == "The expense is not business related."


def test_clarification_review():
    response = create_claim(
        claimant="Clarification Test User",
        description="Dinner with client",
    )

    assert response.status_code == 200

    claim_id = response.json()["id"]

    review = client.post(
        f"/reviews/{claim_id}",
        json={
            "action": "clarification",
            "reason": "Please provide the names of the attendees.",
            "reviewer": "Test Reviewer",
        },
    )

    assert review.status_code in [200, 201]

    data = review.json()

    assert data["action"] == "clarification"


def test_override_review():
    response = create_claim(
        claimant="Override Test User",
        category="Other",
        description="Dinner after product launch",
    )

    assert response.status_code == 200

    claim_id = response.json()["id"]

    review = client.post(
        f"/reviews/{claim_id}",
        json={
            "action": "override",
            "reason": "The description confirms that this is a business meal.",
            "reviewer": "Test Reviewer",
        },
    )

    assert review.status_code in [200, 201]

    data = review.json()

    assert data["action"] == "override"
    assert data["reason"] is not None


def test_review_history_is_returned():
    response = create_claim(
        claimant="History Test User",
        description="Hotel stay for conference",
    )

    assert response.status_code == 200

    claim_id = response.json()["id"]

    review = client.post(
        f"/reviews/{claim_id}",
        json={
            "action": "approve",
            "reason": "Policy requirements satisfied.",
            "reviewer": "Test Reviewer",
        },
    )

    assert review.status_code in [200, 201]

    response = client.get(f"/claims/{claim_id}")

    assert response.status_code == 200

    reviews = response.json()["reviews"]

    assert len(reviews) >= 1
    assert reviews[-1]["action"] == "approve"