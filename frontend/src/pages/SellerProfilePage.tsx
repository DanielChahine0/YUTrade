// Phase: 2 (F2.5)
// Seller profile view — shows seller info and all their listings.

import React, { useState, useEffect } from "react"
import { useParams, useNavigate } from "react-router-dom"
import { getListings } from "../api/listings"
import { getSellerRatings } from "../api/ratings"
import { Listing, SellerRatingsOut } from "../types"
import { formatPrice, formatDate } from "../utils/validators" // Consistent Plugs
import { useAuth } from "../hooks/useAuth"
import StarRating from "../components/StarRating"

const API_URL = process.env.REACT_APP_API_URL || "http://localhost:8000"

export default function SellerProfilePage() {
  const { id } = useParams<{ id: string }>()
  const navigate = useNavigate()
  const [listings, setListings] = useState<Listing[]>([])
  const [loading, setLoading] = useState(true)
  const { user } = useAuth()
  const [sellerRatings, setSellerRatings] = useState<SellerRatingsOut | null>(null)

  useEffect(() => {
    if (!id) return
    getSellerRatings(parseInt(id))
      .then(setSellerRatings)
      .catch(() => setSellerRatings({ ratings: [], average_score: null, total_count: 0 }))
  }, [id])

  useEffect(() => {
    if (!id) return

    getListings({})
      .then((data) => {
        const all: Listing[] = data.listings || []
        setListings(all.filter((l) => l.seller_id === parseInt(id)))
      })
      .catch(() => {})
      .finally(() => setLoading(false))
  }, [id])

  return (
    <div className="app-content">
      {/* Profile Header */}
      <div className="seller-profile-top">
        <div className="seller-avatar">
          <span style={{ fontSize: 36, color: "#bbb" }}>👤</span>
        </div>
        <div className="seller-info-col">
          <h1 className="detail-title" style={{ margin: 0 }}>{sellerRatings?.seller?.name || "York Student"}</h1>

          <div className="seller-rating-row" style={{ display: 'flex', alignItems: 'center', gap: 8, margin: '8px 0' }}>
            <span className="detail-label" style={{ marginBottom: 0 }}>Rating</span>
            <div className="rating-summary">
              {sellerRatings && sellerRatings.total_count > 0 ? (
                <>
                  <span className="rating-summary-score">{sellerRatings.average_score?.toFixed(1)}</span>
                  <StarRating rating={sellerRatings.average_score ?? 0} />
                  <span className="rating-summary-count">
                    ({sellerRatings.total_count} review{sellerRatings.total_count !== 1 ? "s" : ""})
                  </span>
                </>
              ) : (
                <span style={{ color: "#aaa", fontSize: 13 }}>No reviews yet</span>
              )}
            </div>
          </div>

          <div className="detail-label">
            Active since: {sellerRatings?.seller?.created_at ? formatDate(sellerRatings.seller.created_at) : "—"}
          </div>

         <button
          className="btn-red"
          style={{ width: "auto", marginTop: 12 }}
          onClick={() => navigate("/messages")}
        >
          {user?.id === parseInt(id!) ? "View Messages" : "Message Seller"}
        </button>
        </div>
      </div>

      <hr style={{ border: 'none', borderTop: '1px solid #eee', margin: '32px 0' }} />

      {/* Seller's Inventory */}
      <h2 className="auth-title" style={{ textAlign: 'left', fontSize: 18, marginBottom: 16 }}>
        All Seller Listings
      </h2>

      {loading ? (
        <p style={{ textAlign: "center", color: "#aaa", paddingTop: 24 }}>Loading...</p>
      ) : listings.length === 0 ? (
        <p style={{ textAlign: "center", color: "#aaa", paddingTop: 24 }}>
          No active listings found for this seller.
        </p>
      ) : (
        <div className="listings-table-wrap">
          <table className="listings-table">
            <thead>
              <tr>
                <th>Item</th>
                <th>Title</th>
                <th>Price</th>
                <th>Category</th>
                <th>Status</th>
                <th style={{ textAlign: 'right' }}>Action</th>
              </tr>
            </thead>
            <tbody>
              {listings.map((listing) => {
                const firstImg = [...listing.images].sort(
                  (a, b) => a.position - b.position
                )[0]
                return (
                  <tr key={listing.id}>
                    <td>
                      <div className="listing-thumb">
                        {firstImg ? (
                          <img
                            src={`${API_URL}/${firstImg.file_path}`}
                            alt={listing.title}
                          />
                        ) : (
                          <span style={{ color: "#ccc", fontSize: 12 }}>No Image</span>
                        )}
                      </div>
                    </td>
                    <td style={{ fontWeight: 600 }}>{listing.title}</td>

                    {/* Consistent formatPrice Plug */}
                    <td style={{ fontWeight: 700, color: '#E31837' }}>
                      {formatPrice(listing.price)}
                    </td>

                    <td>{listing.category || "—"}</td>
                    <td>
                      <span
                        className={`status-pill ${
                          listing.status === "active"
                            ? "status-pill-active"
                            : listing.status === "sold"
                            ? "status-pill-sold"
                            : "status-pill-inactive"
                        }`}
                      >
                        {listing.status === "active" ? "Active" : listing.status === "sold" ? "Sold" : "Closed"}
                      </span>
                    </td>
                    <td style={{ textAlign: 'right' }}>
                      <button
                        className="btn-table-action"
                        onClick={() => navigate(`/listings/${listing.id}`)}
                      >
                        View
                      </button>
                    </td>
                  </tr>
                )
              })}
            </tbody>
          </table>
        </div>
      )}

      {/* Reviews */}
      <div className="reviews-section">
        <div className="reviews-section-title">Reviews</div>
        {!sellerRatings || sellerRatings.total_count === 0 ? (
          <p style={{ color: "#aaa", fontSize: 13 }}>No reviews yet</p>
        ) : (
          sellerRatings.ratings.map(r => (
            <div key={r.id} className="review-card">
              <div className="review-card-header">
                <span className="review-card-rater">{r.rater.name}</span>
                <span className="review-card-date">{formatDate(r.created_at)}</span>
              </div>
              <StarRating rating={r.score} />
              {r.comment
                ? <p className="review-card-comment">{r.comment}</p>
                : <p style={{ fontSize: 13, color: "#bbb", fontStyle: "italic" }}>No comment</p>
              }
            </div>
          ))
        )}
      </div>
    </div>
  )
}
