import { useEffect, useState } from "react";
import {
  AlertTriangle,
  CheckCircle2,
  Clock3,
  FileText,
  Search,
  XCircle,
  IndianRupee,
} from "lucide-react";

import {
  createClaim,
  createReview,
  getClaim,
  getClaims,
} from "./api";


function statusLabel(status) {
  return (status || "pending").replaceAll("_", " ");
}


function App() {
  const [claims, setClaims] = useState([]);
  const [selected, setSelected] = useState(null);
  const [search, setSearch] = useState("");
  const [message, setMessage] = useState("");
  const [reasonOpen, setReasonOpen] = useState(false);
  const [reason, setReason] = useState("");
  const [newClaimOpen, setNewClaimOpen] = useState(false);
  const [savingClaim, setSavingClaim] = useState(false);

  const [newClaim, setNewClaim] = useState({
    claimant: "",
    date: new Date().toISOString().slice(0, 10),
    category: "Business Meals",
    amount: "",
    currency: "INR",
    description: "",
    receipt_available: true,
  });


  async function loadClaims() {
    try {
      const data = await getClaims();
      setClaims(data);
    } catch (err) {
      setMessage(err.message);
    }
  }


  async function openClaim(id) {
    try {
      const data = await getClaim(id);
      setSelected(data);
      setMessage("");
      setReasonOpen(false);
      setReason("");
    } catch (err) {
      setMessage(err.message);
    }
  }


  useEffect(() => {
    loadClaims();
  }, []);


  const filtered = claims.filter((claim) =>
    `${claim.claimant} ${claim.category} ${claim.description}`
      .toLowerCase()
      .includes(search.toLowerCase())
  );


  // -----------------------------
  // Dashboard statistics
  // -----------------------------

  const totalClaims = claims.length;

  const totalAmount = claims.reduce(
    (sum, claim) => sum + Number(claim.amount || 0),
    0
  );

  const approved = claims.filter(
    (claim) =>
      claim.review_status === "approve" ||
      (!claim.review_status && claim.ai_status === "compliant")
  ).length;

  const rejected = claims.filter(
    (claim) => claim.review_status === "reject"
  ).length;

  const clarification = claims.filter(
    (claim) => claim.review_status === "clarification"
  ).length;

  const pending = claims.filter(
    (claim) => !claim.review_status
  ).length;

  const reviewCount = claims.filter(
    (claim) =>
      !["approve", "reject", "clarification"].includes(
        claim.review_status
      ) &&
      ["needs_review", "uncertain", "needs_clarification"].includes(
        claim.ai_status
      )
  ).length;


  async function review(action, reviewReason = null) {
    try {
      await createReview(selected.claim.id, {
        action,
        reason: reviewReason,
        reviewer: "Reviewer",
      });

      setMessage(
        `Claim ${
          action === "clarification"
            ? "clarification"
            : action
        } submitted successfully.`
      );

      await openClaim(selected.claim.id);
      await loadClaims();

    } catch (err) {
      setMessage(err.message);
    }
  }


  async function handleCreateClaim(e) {
    e.preventDefault();

    if (
      !newClaim.claimant.trim() ||
      !newClaim.amount ||
      !newClaim.description.trim()
    ) {
      setMessage("Please fill in all required fields.");
      return;
    }

    try {
      setSavingClaim(true);

      const created = await createClaim({
        ...newClaim,
        claimant: newClaim.claimant.trim(),
        amount: Number(newClaim.amount),
        description: newClaim.description.trim(),
      });

      await loadClaims();

      setNewClaimOpen(false);

      setNewClaim({
        claimant: "",
        date: new Date().toISOString().slice(0, 10),
        category: "Business Meals",
        amount: "",
        currency: "INR",
        description: "",
        receipt_available: true,
      });

      await openClaim(created.id);

    } catch (err) {
      setMessage(err.message);
    } finally {
      setSavingClaim(false);
    }
  }


  function updateNewClaim(field, value) {
    setNewClaim((prev) => ({
      ...prev,
      [field]: value,
    }));
  }


  function formatAmount(amount) {
    return Number(amount || 0).toLocaleString("en-IN");
  }


  return (
    <div className="app">

      {/* Header */}
      <header className="topbar">
        <div>
          <h1>Expense Review</h1>
          <p>
            AI-assisted policy review for employee expense claims
          </p>
        </div>

        <button
          className="new-button"
          onClick={() => {
            setMessage("");
            setNewClaimOpen(true);
          }}
        >
          + New Claim
        </button>
      </header>


      <main>

        {/* Dashboard statistics */}
        <section className="stats">

          <Stat
            icon={<FileText />}
            title="Total Claims"
            value={totalClaims}
          />

          <Stat
            icon={<IndianRupee />}
            title="Total Amount"
            value={`₹${formatAmount(totalAmount)}`}
          />

          <Stat
            icon={<Clock3 />}
            title="Pending Review"
            value={pending}
          />

          <Stat
            icon={<CheckCircle2 />}
            title="Approved"
            value={approved}
          />

          <Stat
            icon={<AlertTriangle />}
            title="Needs Attention"
            value={reviewCount}
          />

          <Stat
            icon={<XCircle />}
            title="Rejected"
            value={rejected}
          />

        </section>


        {/* Claims table */}
        <section className="panel">

          <div className="panel-head">

            <div>
              <h2>Claims</h2>
              <span>{filtered.length} claims found</span>
            </div>

            <div className="search">
              <Search size={17} />

              <input
                value={search}
                onChange={(e) => setSearch(e.target.value)}
                placeholder="Search claims..."
              />
            </div>

          </div>


          <div className="table-wrap">

            <table>

              <thead>
                <tr>
                  <th>Claimant</th>
                  <th>Category</th>
                  <th>Amount</th>
                  <th>Receipt</th>
                  <th>AI Status</th>
                  <th></th>
                </tr>
              </thead>


              <tbody>

                {filtered.length === 0 ? (
                  <tr>
                    <td colSpan="6" className="empty-state">
                      No claims found.
                    </td>
                  </tr>
                ) : (
                  filtered.map((claim) => (
                    <tr
                      key={claim.id}
                      onClick={() => openClaim(claim.id)}
                    >

                      <td>
                        <strong>{claim.claimant}</strong>
                        <small>{claim.description}</small>
                      </td>

                      <td>{claim.category}</td>

                      <td>
                        {claim.currency}{" "}
                        {formatAmount(claim.amount)}
                      </td>

                      <td>
                        {claim.receipt_available
                          ? "Yes"
                          : "No"}
                      </td>

                      <td>
                        <span
                          className={`badge ${
                            claim.review_status ||
                            claim.ai_status ||
                            "pending"
                          }`}
                        >
                          {statusLabel(
                            claim.review_status ||
                              claim.ai_status
                          )}
                        </span>
                      </td>

                      <td className="arrow">→</td>

                    </tr>
                  ))
                )}

              </tbody>

            </table>

          </div>

        </section>


        {/* Review drawer */}
        {selected && (
          <ReviewPanel
            data={selected}
            onReview={review}
            message={message}
            onClose={() => setSelected(null)}
            reasonOpen={reasonOpen}
            setReasonOpen={setReasonOpen}
            reason={reason}
            setReason={setReason}
          />
        )}


        {/* New claim modal */}
        {newClaimOpen && (

          <div className="overlay">

            <div className="new-claim-modal">

              <div className="drawer-head">

                <div>
                  <span className="eyebrow">
                    New Expense
                  </span>

                  <h2>Create Claim</h2>
                </div>

                <button
                  className="icon-btn"
                  onClick={() => setNewClaimOpen(false)}
                >
                  <XCircle />
                </button>

              </div>


              <form onSubmit={handleCreateClaim}>

                <div className="form-grid">

                  <label>
                    Claimant *
                    <input
                      value={newClaim.claimant}
                      onChange={(e) =>
                        updateNewClaim(
                          "claimant",
                          e.target.value
                        )
                      }
                      placeholder="Employee name"
                    />
                  </label>


                  <label>
                    Date *
                    <input
                      type="date"
                      value={newClaim.date}
                      onChange={(e) =>
                        updateNewClaim(
                          "date",
                          e.target.value
                        )
                      }
                    />
                  </label>


                  <label>
                    Category *
                    <select
                      value={newClaim.category}
                      onChange={(e) =>
                        updateNewClaim(
                          "category",
                          e.target.value
                        )
                      }
                    >
                      <option>Business Meals</option>
                      <option>Travel</option>
                      <option>Transportation</option>
                      <option>Accommodation</option>
                      <option>Miscellaneous</option>
                    </select>
                  </label>


                  <label>
                    Amount *
                    <input
                      type="number"
                      min="0"
                      step="0.01"
                      value={newClaim.amount}
                      onChange={(e) =>
                        updateNewClaim(
                          "amount",
                          e.target.value
                        )
                      }
                      placeholder="0.00"
                    />
                  </label>


                  <label>
                    Currency *
                    <select
                      value={newClaim.currency}
                      onChange={(e) =>
                        updateNewClaim(
                          "currency",
                          e.target.value
                        )
                      }
                    >
                      <option>INR</option>
                      <option>USD</option>
                      <option>EUR</option>
                      <option>GBP</option>
                    </select>
                  </label>


                  <label>
                    Receipt Available *
                    <select
                      value={String(
                        newClaim.receipt_available
                      )}
                      onChange={(e) =>
                        updateNewClaim(
                          "receipt_available",
                          e.target.value === "true"
                        )
                      }
                    >
                      <option value="true">
                        Yes
                      </option>

                      <option value="false">
                        No
                      </option>
                    </select>
                  </label>

                </div>


                <label className="full-field">
                  Description *

                  <textarea
                    value={newClaim.description}
                    onChange={(e) =>
                      updateNewClaim(
                        "description",
                        e.target.value
                      )
                    }
                    placeholder="Describe the expense and business purpose..."
                  />
                </label>


                {message && (
                  <div className="message">
                    {message}
                  </div>
                )}


                <div className="reason-actions">

                  <button
                    type="button"
                    onClick={() =>
                      setNewClaimOpen(false)
                    }
                  >
                    Cancel
                  </button>

                  <button
                    type="submit"
                    className="approve"
                    disabled={savingClaim}
                  >
                    {savingClaim
                      ? "Creating..."
                      : "Create Claim"}
                  </button>

                </div>

              </form>

            </div>

          </div>

        )}

      </main>

    </div>
  );
}


function Stat({ icon, title, value }) {
  return (
    <div className="stat">

      <div className="stat-icon">
        {icon}
      </div>

      <div>
        <span>{title}</span>
        <strong>{value}</strong>
      </div>

    </div>
  );
}


function ReviewPanel({
  data,
  onReview,
  message,
  onClose,
  reasonOpen,
  setReasonOpen,
  reason,
  setReason,
}) {

  const {
    claim,
    validation,
    reviews,
  } = data;

  let missing = [];

  try {
    missing = JSON.parse(
      claim.missing_information || "[]"
    );
  } catch {}


  return (

    <div className="overlay">

      <aside className="drawer">

        <div className="drawer-head">

          <div>
            <span className="eyebrow">
              Claim #{claim.id}
            </span>

            <h2>{claim.claimant}</h2>
          </div>

          <button
            className="icon-btn"
            onClick={onClose}
          >
            <XCircle />
          </button>

        </div>


        <div className="claim-grid">

          <Info
            label="Category"
            value={claim.category}
          />

          <Info
            label="Amount"
            value={`${claim.currency} ${Number(
              claim.amount
            ).toLocaleString("en-IN")}`}
          />

          <Info
            label="Date"
            value={claim.date}
          />

          <Info
            label="Receipt"
            value={
              claim.receipt_available
                ? "Available"
                : "Missing"
            }
          />

        </div>


        {/* AI classification */}
        <section className="review-section">

          <h3>AI Classification</h3>

          <div className="ai-card">

            <div>

              <strong>
                {claim.ai_category ||
                  "Not classified"}
              </strong>

              <span>
                {Math.round(
                  (claim.ai_confidence || 0) * 100
                )}
                % confidence
              </span>

            </div>

            <span
              className={`badge ${
                claim.ai_status || "pending"
              }`}
            >
              {statusLabel(claim.ai_status)}
            </span>

          </div>


          <p>
            {claim.ai_reason ||
              "No AI explanation available."}
          </p>


          {missing.length > 0 && (

            <div className="warning">

              <AlertTriangle size={17} />

              <div>
                <strong>
                  Missing information
                </strong>

                <p>
                  {missing.join(", ")}
                </p>
              </div>

            </div>

          )}

        </section>


        {/* Deterministic validation */}
        <section className="review-section">

          <h3>Deterministic Checks</h3>

          <CheckList
            validation={validation}
          />

        </section>


        {/* Policy evidence */}
        <section className="review-section">

          <h3>Policy Evidence</h3>

          <div className="evidence">

            <strong>
              {data.policy?.title ||
                `${claim.category} Policy`}
            </strong>

            <p>
              {data.policy?.content ||
                "No matching policy section was found."}
            </p>

            {data.policy?.limit != null && (
              <small>
                Configured limit:{" "}
                {data.policy.currency}{" "}
                {data.policy.limit.toLocaleString(
                  "en-IN"
                )}
              </small>
            )}

          </div>

        </section>


        {/* Review history */}
        <section className="review-section">

          <h3>Decision History</h3>

          {reviews.length === 0 ? (

            <p className="muted">
              No reviewer decisions yet.
            </p>

          ) : (

            reviews.map((review) => (

              <div
                className="history"
                key={review.id}
              >

                <strong>
                  {review.action}
                </strong>

                <span>
                  {review.reviewer} ·{" "}
                  {new Date(
                    review.created_at
                  ).toLocaleString()}
                </span>

                {review.reason && (
                  <p>{review.reason}</p>
                )}

              </div>

            ))

          )}

        </section>


        {message && (
          <div className="message">
            {message}
          </div>
        )}


        {/* Reviewer actions */}
        <div className="actions">

          <button
            onClick={() => onReview("approve")}
            className="approve"
          >
            Approve
          </button>

          <button
            onClick={() => onReview("reject")}
            className="reject"
          >
            Reject
          </button>

          <button
            onClick={() =>
              setReasonOpen(!reasonOpen)
            }
            className="clarify"
          >
            Request Clarification
          </button>

          <button
            onClick={() => {
              const value = window.prompt(
                "Why are you overriding the AI classification?"
              );

              if (value) {
                onReview("override", value);
              }
            }}
            className="clarify"
          >
            Override AI
          </button>

        </div>


        {reasonOpen && (

          <div className="reason-box">

            <label>
              Reason for clarification
            </label>

            <textarea
              value={reason}
              onChange={(e) =>
                setReason(e.target.value)
              }
              placeholder="Explain what information the claimant needs to provide..."
            />

            <div className="reason-actions">

              <button
                onClick={() => {
                  setReasonOpen(false);
                  setReason("");
                }}
              >
                Cancel
              </button>

              <button
                className="approve"
                disabled={!reason.trim()}
                onClick={() => {
                  onReview(
                    "clarification",
                    reason.trim()
                  );

                  setReasonOpen(false);
                  setReason("");
                }}
              >
                Submit Clarification
              </button>

            </div>

          </div>

        )}

      </aside>

    </div>
  );
}


function Info({ label, value }) {
  return (
    <div>
      <span>{label}</span>
      <strong>{value}</strong>
    </div>
  );
}


function CheckList({ validation }) {

  const items = [
    ...validation.issues.map((item) => ({
      ok: false,
      text: item,
    })),

    ...validation.warnings.map((item) => ({
      ok: false,
      text: item,
    })),
  ];


  if (!items.length) {
    return (
      <div className="check ok">
        <CheckCircle2 size={17} />
        All deterministic checks passed.
      </div>
    );
  }


  return (
    <div>

      {items.map((item, index) => (

        <div
          className="check"
          key={index}
        >
          <XCircle size={17} />
          {item.text}
        </div>

      ))}

    </div>
  );
}


export default App;