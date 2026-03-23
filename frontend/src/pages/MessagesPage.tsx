// Assigned to: Harnaindeep Kaur
// Phase: 3 (F3.4)
//
// TODO: Page showing all message conversations (protected).
//
// Layout:
//   - Page title: "Messages"
//   - List of conversation threads, grouped by listing
//   - Each thread shows:
//       - Listing title and thumbnail
//       - Other person's name
//       - Last message preview (truncated)
//       - Timestamp of last message
//   - Clicking a thread navigates to /listings/{id} (with message section visible)
//   - Empty state: "No messages yet"
//
// Behavior:
//   1. On mount, fetch all listings where the user has sent or received messages
//      (This may require a dedicated endpoint or fetching from multiple listing threads)
//   2. Display threads sorted by most recent message first
//   3. Show loading spinner while fetching
//   4. Handle errors gracefully
//
// Note: The exact API approach for getting "all threads" may need coordination
// with Raj's backend implementation. Options:
//   a) A new GET /messages endpoint that returns all threads for the current user
//   b) Client-side aggregation from multiple listing message endpoints
//   Discuss with Raj to decide the best approach.
// Edited by : Mai Komar

import React, { useState, useEffect } from "react"
import { useLocation, useNavigate } from "react-router-dom"
import { formatDate } from "../utils/validators"
import MessageThread from "../components/MessageThread"
import { useAuth } from "../hooks/useAuth"
import { getListing, getListings } from "../api/listings"
import { getAllThreads } from "../api/messages"

const MessagesPage: React.FC = () => {
  const [threads, setThreads] = useState<any[]>([])
  const [loadingThreads, setLoadingThreads] = useState(true)
  const [activeListing, setActiveListing] = useState<any>(null)
  const [loadingActive, setLoadingActive] = useState(false)

  const location = useLocation()
  const navigate = useNavigate()
  const { user } = useAuth()
  const listingId = new URLSearchParams(location.search).get("listingId")

  // Load the active conversation from URL param
  useEffect(() => {
    if (!listingId) {
      setActiveListing(null)
      return
    }
    setLoadingActive(true)
    getListing(parseInt(listingId))
      .then(setActiveListing)
      .finally(() => setLoadingActive(false))
  }, [listingId])

  useEffect(() => {
  if (!user) {
    setLoadingThreads(false)
    return
  }
  getAllThreads()
    .then((data) => setThreads(data.threads || []))
    .catch((err) => console.error("Failed to load inbox", err))
    .finally(() => setLoadingThreads(false))
}, [user])
  const handleBack = () => {
    navigate("/messages")
  }

  const handleThreadClick = (threadListingId: number) => {
    navigate(`/messages?listingId=${threadListingId}`)
  }

  // — Active conversation view —
  if (listingId) {
    return (
      <div className="app-content">
        <button className="detail-back-btn" onClick={handleBack}>
          ← Back to Messages
        </button>

        {loadingActive ? (
          <p style={{ color: "#aaa", textAlign: "center", paddingTop: 48 }}>Loading...</p>
        ) : activeListing && user ? (
          <>
            <div style={{ marginBottom: 16 }}>
              <h1 className="all-listings-title" style={{ margin: 0 }}>
                {activeListing.title}
              </h1>
              <p style={{ fontSize: 13, color: "#888", marginTop: 4 }}>
                Seller: {activeListing.seller?.name}
              </p>
            </div>
            <MessageThread
              listingId={activeListing.id}
              sellerId={activeListing.seller_id}
              currentUserId={user.id}
            />
          </>
        ) : (
          <p style={{ color: "#888", textAlign: "center", paddingTop: 48 }}>
            Listing not found.
          </p>
        )}
      </div>
    )
  }

  // — Thread list view —
  return (
    <div className="app-content">
      <div style={{
        marginBottom: 32,
        paddingBottom: 16,
        borderBottom: "1px solid #eee",
      }}>
        <h1 className="all-listings-title" style={{ margin: 0 }}>Your Messages</h1>
        <p style={{ color: "#666", fontSize: 14, marginTop: 4 }}>
          Manage your conversations with buyers and sellers here.
        </p>
      </div>

      {loadingThreads ? (
        <p style={{ textAlign: "center", color: "#aaa", paddingTop: 48 }}>
          Loading your messages...
        </p>
      ) : threads.length === 0 ? (
        <div className="listings-table-wrap" style={{
          padding: "80px 20px",
          textAlign: "center",
          background: "var(--yu-white)",
          border: "1px solid var(--border-color)",
          borderRadius: "var(--radius-lg)",
        }}>
          <div style={{ fontSize: 48, marginBottom: 16 }}>💬</div>
          <h3 style={{ marginBottom: 8 }}>No messages yet</h3>
          <p style={{ color: "#888", maxWidth: 450, margin: "0 auto" }}>
            When you contact a seller or someone messages about your listing,
            the conversation will appear here.
          </p>
        </div>
      ) : (
        <div style={{
          background: "#fff",
          borderRadius: 16,
          boxShadow: "0 2px 16px rgba(0,0,0,0.08)",
          overflow: "hidden",
        }}>
          {threads.map((thread, i) => (
            <div
              key={thread.listing_id}
              onClick={() => handleThreadClick(thread.listing_id)}
              style={{
                display: "flex",
                justifyContent: "space-between",
                alignItems: "center",
                padding: "16px 20px",
                borderBottom: i < threads.length - 1 ? "1px solid #f0f0f0" : "none",
                cursor: "pointer",
                transition: "background 0.15s",
              }}
              onMouseEnter={(e) => (e.currentTarget.style.background = "#fafafa")}
              onMouseLeave={(e) => (e.currentTarget.style.background = "#fff")}
            >
              <div style={{ display: "flex", alignItems: "center", gap: 14 }}>
                {/* Avatar */}
               <div className="detail-seller-avatar">
                {thread.other_user_name?.charAt(0).toUpperCase()}
              </div>
                <div>
                  <div style={{ fontWeight: 700, fontSize: 14, color: "#1a1a1a" }}>
                    {thread.other_user_name}
                  </div>
                  <div style={{ fontSize: 13, color: "#888", marginTop: 1 }}>
                    {thread.listing_title}
                  </div>
                  <div style={{
                    fontSize: 13,
                    color: "#aaa",
                    marginTop: 2,
                    maxWidth: 340,
                    overflow: "hidden",
                    textOverflow: "ellipsis",
                    whiteSpace: "nowrap",
                  }}>
                    {thread.last_message}
                  </div>
                </div>
              </div>
              <div style={{ fontSize: 12, color: "#bbb", flexShrink: 0, marginLeft: 16 }}>
                {formatDate(thread.last_message_at)}
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  )
}

export default MessagesPage