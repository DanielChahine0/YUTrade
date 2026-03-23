// Assigned to: Mai Komar
// Phase: 2 (F2.4)

import React, { useState, useEffect, useRef } from "react"
import { useParams, useNavigate } from "react-router-dom"
import { getListing } from "../api/listings"
import { getMyRating, createRating, updateRating, deleteRating, getSellerRatings } from "../api/ratings"
import { useAuth } from "../hooks/useAuth"
import { Listing, MyRatingOut, SellerRatingsOut } from "../types"
import { formatPrice, formatDate } from "../utils/validators"
import StarRating from "../components/StarRating"

const API_URL = process.env.REACT_APP_API_URL || "http://localhost:8000"

export default function ListingDetailPage() {
  const { id } = useParams<{ id: string }>()
  const navigate = useNavigate()
  const { user } = useAuth()
  const [listing, setListing] = useState<Listing | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState("")
  const [imgIdx, setImgIdx] = useState(0)
  const [lightboxOpen, setLightboxOpen] = useState(false)
  const [myRating, setMyRating] = useState<MyRatingOut | null>(null)
  const [sellerRatings, setSellerRatings] = useState<SellerRatingsOut | null>(null)
  const [selectedScore, setSelectedScore] = useState(0)
  const [comment, setComment] = useState("")
  const [editMode, setEditMode] = useState(false)
  const [ratingError, setRatingError] = useState("")
  const [ratingSubmitting, setRatingSubmitting] = useState(false)


  useEffect(() => {
    if (!id) return
    getListing(parseInt(id))
      .then(setListing)
      .catch(() => setError("Listing not found"))
      .finally(() => setLoading(false))
  }, [id])

  useEffect(() => {
    if (!listing) return
    getSellerRatings(listing.seller_id)
      .then(setSellerRatings)
      .catch(() => {})
  }, [listing?.seller_id])  // eslint-disable-line react-hooks/exhaustive-deps

  useEffect(() => {
    if (!listing || !user || user.id === listing.seller_id) return
    getMyRating(listing.id).then(data => {
      setMyRating(data)
      if (data.rating) {
        setSelectedScore(data.rating.score)
        setComment(data.rating.comment ?? "")
      }
    }).catch(() => {})
  }, [listing?.id, user?.id])  // eslint-disable-line react-hooks/exhaustive-deps

  useEffect(() => {
    if (!lightboxOpen) return
    const handleKey = (e: KeyboardEvent) => {
      if (e.key === "Escape") setLightboxOpen(false)
      if (e.key === "ArrowRight") setImgIdx(i => i + 1)
      if (e.key === "ArrowLeft") setImgIdx(i => Math.max(i - 1, 0))
    }
    window.addEventListener("keydown", handleKey)
    return () => window.removeEventListener("keydown", handleKey)
  }, [lightboxOpen])

  if (loading) {
    return (
      <div className="app-content" style={{ textAlign: "center", paddingTop: 48, color: "#aaa" }}>
        Loading...
      </div>
    )
  }

  if (error || !listing) {
    return (
      <div className="app-content" style={{ textAlign: "center", paddingTop: 48 }}>
        <p style={{ color: "#888" }}>{error || "Listing not found"}</p>
        <button
          className="btn-outline"
          style={{ width: "auto", marginTop: 16 }}
          onClick={() => navigate("/browse")}
        >
          Back to Browse
        </button>
      </div>
    )
  }

  const handleSubmitRating = async () => {
    if (selectedScore === 0) { setRatingError("Please select a star rating"); return }
    setRatingSubmitting(true); setRatingError("")
    try {
      await createRating(listing!.id, { score: selectedScore, comment: comment || undefined })
      const updated = await getMyRating(listing!.id)
      setMyRating(updated); setEditMode(false)
    } catch (e: any) { setRatingError(e.response?.data?.detail ?? "Failed to submit rating") }
    finally { setRatingSubmitting(false) }
  }

  const handleUpdateRating = async () => {
    setRatingSubmitting(true); setRatingError("")
    try {
      await updateRating(listing!.id, { score: selectedScore, comment: comment })
      const updated = await getMyRating(listing!.id)
      setMyRating(updated); setEditMode(false)
    } catch (e: any) { setRatingError(e.response?.data?.detail ?? "Failed to update rating") }
    finally { setRatingSubmitting(false) }
  }

  const handleDeleteRating = async () => {
    if (!window.confirm("Delete your rating?")) return
    try {
      await deleteRating(listing!.id)
      setMyRating({ rating: null, can_rate: true }); setSelectedScore(0); setComment("")
    } catch (e: any) { setRatingError(e.response?.data?.detail ?? "Failed to delete rating") }
  }

  const images = [...listing.images].sort((a, b) => a.position - b.position)
  const currentImg = images[imgIdx]
  const isSeller = user?.id === listing.seller_id

  return (
    <div className="app-content">
      <button className="detail-back-btn" onClick={() => navigate(-1)}>
        ← Back
      </button>

      <div className="detail-layout">

        {/* Left: Image + Thumbnails */}
        <div className="detail-left">
          <div
            className="detail-main-img"
            style={{ cursor: currentImg ? "zoom-in" : "default" }}
            onClick={() => currentImg && setLightboxOpen(true)}
          >
            {currentImg ? (
              <img src={`${API_URL}/${currentImg.file_path}`} alt={listing.title} />
            ) : (
              <span className="detail-no-img">No Image</span>
            )}
          </div>

          {images.length > 1 && (
            <div className="detail-thumbnails">
              {images.map((img, i) => (
                <div
                  key={i}
                  className={`detail-thumbnail${i === imgIdx ? " active" : ""}`}
                  onClick={() => setImgIdx(i)}
                >
                  <img src={`${API_URL}/${img.file_path}`} alt={`${listing.title} ${i + 1}`} />
                </div>
              ))}
            </div>
          )}
        </div>

        {/* Right: Details + Seller */}
        <div className="detail-right">

          {/* Details card */}
          <div className="detail-info-card">
            <h1 className="detail-info-title">{listing.title}</h1>
            <div className="detail-info-price">{formatPrice(listing.price)}</div>

            <div className="detail-info-label">Description</div>
            <p className="detail-info-desc">{listing.description || "No description provided."}</p>

            <div className="detail-info-row">
              <span className="detail-info-label" style={{ marginBottom: 0 }}>Category</span>
              <span className="detail-info-value">{listing.category || "General"}</span>
            </div>

            <div className="detail-info-timestamp">Listed {formatDate(listing.created_at)}</div>
          </div>

          {/* Seller card */}
          <div className="detail-seller-card">
            <div className="detail-seller-info">
              <div className="detail-seller-avatar">
                {listing.seller.name.charAt(0).toUpperCase()}
              </div>
              <div>
                <div className="detail-seller-name">{listing.seller.name}</div>
                {sellerRatings && sellerRatings.total_count > 0 && (
                  <div style={{ display: "flex", alignItems: "center", gap: 4, marginTop: 2 }}>
                    <StarRating rating={sellerRatings.average_score ?? 0} size={12} />
                    <span style={{ fontSize: 12, color: "#555" }}>
                      {sellerRatings.average_score?.toFixed(1)} ({sellerRatings.total_count})
                    </span>
                  </div>
                )}
              </div>
            </div>

            <button
              className="btn-red-sm"
              onClick={() => navigate(`/seller/${listing.seller_id}`)}
            >
              View Seller Profile
            </button>

            <button
              className="btn-red-sm"
              style={{ background: "#1a1a1a" }}
              onClick={() => navigate(`/messages?listingId=${listing.id}`)}
            >
              {isSeller ? "View Messages" : "Message Seller"}
            </button>

            {user && !isSeller && (
              <div className="rating-section">
                {!myRating ? null
                  : !myRating.rating && !myRating.can_rate ? (
                    <p style={{ fontSize: 12, color: "#aaa", margin: 0 }}>
                      Message the seller to unlock ratings
                    </p>
                  ) : myRating.rating && !editMode ? (
                    <>
                      <div className="rating-section-title">Your Rating</div>
                      <StarRating rating={myRating.rating.score} />
                      {myRating.rating.comment && (
                        <p style={{ fontSize: 12, color: "#555", margin: "4px 0 8px" }}>
                          {myRating.rating.comment}
                        </p>
                      )}
                      <div className="rating-submit-row">
                        <button
                          className="btn-outline"
                          style={{ width: "auto", fontSize: 12 }}
                          onClick={() => {
                            setEditMode(true)
                            setSelectedScore(myRating.rating!.score)
                            setComment(myRating.rating!.comment ?? "")
                          }}
                        >
                          Edit
                        </button>
                        <button
                          className="btn-outline"
                          style={{ width: "auto", fontSize: 12, color: "#E31837" }}
                          onClick={handleDeleteRating}
                        >
                          Delete
                        </button>
                      </div>
                    </>
                  ) : (myRating.can_rate || editMode) ? (
                    <>
                      <div className="rating-section-title">
                        {editMode ? "Edit Rating" : "Rate this Seller"}
                      </div>
                      <StarRating rating={selectedScore} onSelect={setSelectedScore} />
                      <textarea
                        className="rating-comment-input"
                        placeholder="Comment (optional)"
                        value={comment}
                        onChange={e => setComment(e.target.value)}
                      />
                      {ratingError && (
                        <p style={{ color: "#E31837", fontSize: 12, margin: "4px 0" }}>
                          {ratingError}
                        </p>
                      )}
                      <div className="rating-submit-row">
                        {editMode && (
                          <button
                            className="btn-outline"
                            style={{ width: "auto", fontSize: 12 }}
                            onClick={() => setEditMode(false)}
                          >
                            Cancel
                          </button>
                        )}
                        <button
                          className="btn-red-sm"
                          disabled={ratingSubmitting}
                          onClick={editMode ? handleUpdateRating : handleSubmitRating}
                        >
                          {ratingSubmitting ? "Saving..." : "Submit"}
                        </button>
                      </div>
                    </>
                  ) : null}
              </div>
            )}
          </div>

        </div>
      </div>

      {/* Lightbox */}
      {lightboxOpen && currentImg && (
        <div className="lightbox-overlay" onClick={() => setLightboxOpen(false)}>
          <button className="lightbox-close" onClick={() => setLightboxOpen(false)}>
            ×
          </button>
 
          {imgIdx > 0 && (
            <button
              className="lightbox-arrow lightbox-arrow-left"
              onClick={(e) => { e.stopPropagation(); setImgIdx(i => i - 1) }}
            >
              ‹
            </button>
          )}
 
          <img
            className="lightbox-img"
            src={`${API_URL}/${currentImg.file_path}`}
            alt={listing.title}
            onClick={(e) => e.stopPropagation()}
          />
 
          {imgIdx < images.length - 1 && (
            <button
              className="lightbox-arrow lightbox-arrow-right"
              onClick={(e) => { e.stopPropagation(); setImgIdx(i => i + 1) }}
            >
              ›
            </button>
          )}
 
          {images.length > 1 && (
            <div className="lightbox-counter">
              {imgIdx + 1} / {images.length}
            </div>
          )}
        </div>
      )}
    </div>
  )
}