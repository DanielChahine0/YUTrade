// Assigned to: Harnaindeep Kaur
// Phase: 3 (F3.4)
// Edited by : Mai Komar

import React, { useState, useEffect } from "react"
import { useLocation, useNavigate } from "react-router-dom"
import { formatDate } from "../utils/validators"
import MessageThread from "../components/MessageThread"
import { useAuth } from "../hooks/useAuth"
import { getListing } from "../api/listings"
import { getAllThreads } from "../api/messages"

const API_URL = process.env.REACT_APP_API_URL || "http://localhost:8000"

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
      .then(async (data) => {
        const threads = data.threads || []
        const threadsWithNames = await Promise.all(
          threads.map(async (thread: any) => {
            const listing = await getListing(thread.listing_id)
            return {
              ...thread,
              other_user_name: listing.seller.name,
              listing_image: listing.images?.[0]?.file_path
                ? `${API_URL}/${listing.images[0].file_path}`
                : null,
            }
          })
        )
        setThreads(threadsWithNames)
      })
      .catch((err) => console.error("Failed to load inbox", err))
      .finally(() => setLoadingThreads(false))
  }, [user])

  const handleBack = () => {
    navigate("/messages")
  }

  const handleThreadClick = (threadListingId: number) => {
    navigate(`/messages?listingId=${threadListingId}`)
  }

  // Active conversation view
  if (listingId) {
    return (
      <div className="app-content">
        <button className="detail-back-btn" onClick={handleBack}>
          ← Back to Messages
        </button>

        {loadingActive ? (
          <div className="loading-state">Loading...</div>
        ) : activeListing && user ? (
          <>
            <div style={{ marginBottom: 20 }}>
              <h1 className="all-listings-title" style={{ margin: 0, borderBottom: "none", paddingBottom: 0 }}>
                {activeListing.title}
              </h1>
              <p style={{ fontSize: 14, color: "var(--text-secondary)", marginTop: 4 }}>
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
          <div className="loading-state">Listing not found.</div>
        )}
      </div>
    )
  }

  // Thread list view
  return (
    <div className="app-content">
      <div style={{ marginBottom: 32 }}>
        <h1 className="all-listings-title" style={{ margin: 0, borderBottom: "none", paddingBottom: 0 }}>
          Your Messages
        </h1>
        <p style={{ color: "var(--text-secondary)", fontSize: 15, marginTop: 6 }}>
          Manage your conversations with buyers and sellers here.
        </p>
      </div>

      {loadingThreads ? (
        <div className="loading-state">Loading your messages...</div>
      ) : threads.length === 0 ? (
        <div className="empty-state">
          <div className="empty-state-icon">💬</div>
          <div className="empty-state-title">No messages yet</div>
          <p className="empty-state-text">
            When you contact a seller or someone messages about your listing,
            the conversation will appear here.
          </p>
        </div>
      ) : (
        <div className="messages-list-container">
          {threads.map((thread, i) => (
            <div
              key={thread.listing_id}
              className={`message-thread-row${thread.unread_count > 0 ? " unread" : ""}`}
              onClick={() => handleThreadClick(thread.listing_id)}
            >
              <div style={{ display: "flex", alignItems: "center", gap: 14, flex: 1, minWidth: 0 }}>
                {thread.listing_image ? (
                  <img
                    src={thread.listing_image}
                    alt={thread.listing_title}
                    className="thread-avatar"
                  />
                ) : (
                  <div className="thread-avatar" style={{
                    display: "flex",
                    alignItems: "center",
                    justifyContent: "center",
                    color: "var(--gray-300)",
                    fontSize: 20,
                  }}>
                    🖼️
                  </div>
                )}
                <div className="thread-info">
                  <div className="thread-top-line">
                    <span className="thread-title">{thread.other_user_name}</span>
                  </div>
                  <div style={{ fontSize: 13, color: "var(--text-secondary)", marginBottom: 2 }}>
                    {thread.listing_title}
                  </div>
                  <div className="thread-preview-text">
                    {thread.last_message}
                  </div>
                </div>
              </div>
              <div style={{ display: "flex", flexDirection: "column", alignItems: "flex-end", flexShrink: 0, marginLeft: 16, gap: 6 }}>
                <span className="thread-date">
                  {formatDate(thread.last_message_at)}
                </span>
                {thread.unread_count > 0 && (
                  <span style={{
                    background: "var(--yu-red)",
                    color: "#fff",
                    borderRadius: "var(--radius-pill)",
                    padding: "2px 8px",
                    fontSize: 11,
                    fontFamily: "var(--font-display)",
                    fontWeight: 700,
                    minWidth: 20,
                    textAlign: "center",
                  }}>
                    {thread.unread_count}
                  </span>
                )}
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  )
}

export default MessagesPage
