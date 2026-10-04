const API_URL = "http://127.0.0.1:8000";

async function request(url, options = {}) {
  const response = await fetch(`${API_URL}${url}`, {
    headers: {
      "Content-Type": "application/json",
      ...(options.headers || {})
    },
    ...options
  });

  if (!response.ok) {
    let message = "Something went wrong";

    try {
      const data = await response.json();
      message = data.detail || message;
    } catch {}

    throw new Error(message);
  }

  return response.json();
}

export async function getClaims() {
  return request("/claims");
}

export async function getClaim(id) {
  return request(`/claims/${id}`);
}

export async function createClaim(claim) {
  return request("/claims", {
    method: "POST",
    body: JSON.stringify(claim)
  });
}

export async function createReview(claimId, review) {
  return request(`/reviews/${claimId}`, {
    method: "POST",
    body: JSON.stringify(review)
  });
}