// Assigned to: Mai Komar
// Phase: 2 (F2.4)

import React, { useState, useEffect } from "react"
import { useParams, useNavigate } from "react-router-dom"
import { getListing } from "../api/listings"
import { useAuth } from "../hooks/useAuth"
import { Listing } from "../types"
import { formatPrice, formatDate } from "../utils/validators"

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

  useEffect(() => {
    if (!id) return
    getListing(parseInt(id))
      .then(setListing)
      .catch(() => setError("Listing not found"))
      .finally(() => setLoading(false))
  }, [id])

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