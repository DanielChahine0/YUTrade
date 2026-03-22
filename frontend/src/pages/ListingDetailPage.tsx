// Assigned to: Mai Komar
// Phase: 2 (F2.4)

import React, { useState, useEffect } from "react"
import { useParams, useNavigate } from "react-router-dom"
import { getListing } from "../api/listings"
import { useAuth } from "../hooks/useAuth"
import { Listing } from "../types"
import { formatPrice, formatDate } from "../utils/validators"

const API_URL = process.env.REACT_APP_API_URL || "http://localhost:8000"

function StarRating({ rating, max = 5 }: { rating: number; max?: number }) {
  return (
    <div className="star-row">
      {Array.from({ length: max }).map((_, i) => {
        const filled = i < Math.floor(rating)
        const half = !filled && i < rating
        return (
          <span key={i} className={filled ? "star-icon" : half ? "star-icon-half" : "star-icon-empty"}>
            ★
          </span>
        )
      })}
    </div>
  )
}

export default function ListingDetailPage() {
  const { id } = useParams<{ id: string }>()
  const navigate = useNavigate()
  const { user } = useAuth()
  const [listing, setListing] = useState<Listing | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState("")
  const [imgIdx, setImgIdx] = useState(0)

  useEffect(() => {
    if (!id) return
    getListing(parseInt(id))
      .then(setListing)
      .catch(() => setError("Listing not found"))
      .finally(() => setLoading(false))
  }, [id])

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
        <button className="btn-outline" style={{ width: "auto", marginTop: 16 }} onClick={() => navigate("/browse")}>
          Back to Browse
        </button>
      </div>
    )
  }

  const images = [...listing.images].sort((a, b) => a.position - b.position)
  const currentImg = images[imgIdx]
  const isSeller = user?.id === listing.seller_id

  return (
    <div className="app-content">

      <button className="detail-back-btn" onClick={() => navigate(-1)}>← Back</button>

      <div className="detail-layout">

        {/* Left: Image + Thumbnails */}
        <div className="detail-left">
          <div className="detail-main-img">
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
                <div className="detail-seller-rating">
                  <StarRating rating={4.0} />
                  <span style={{ fontSize: 12, color: "#888", marginLeft: 4 }}>4.0 Rating</span>
                </div>
              </div>
            </div>
            <button
              className="btn-red-sm"
              onClick={() => navigate(`/seller/${listing.seller_id}`)}
            >
              View Seller Profile
            </button>
            {!isSeller && (
              <button
                className="btn-red-sm"
                style={{ background: "#1a1a1a" }}
                onClick={() => navigate("/messages")}
              >
                Message Seller
              </button>
            )}
          </div>

        </div>
      </div>
    </div>
  )
}