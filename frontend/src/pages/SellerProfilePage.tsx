// Phase: 2 (F2.5)
// Seller profile view — shows seller info and all their listings.

import React, { useState, useEffect } from "react"
import { useParams, useNavigate } from "react-router-dom"
import { getListings } from "../api/listings"
import { Listing } from "../types"
import { formatPrice, formatDate } from "../utils/validators" // Consistent Plugs

const API_URL = process.env.REACT_APP_API_URL || "http://localhost:8000"

function StarRating({ rating, max = 5 }: { rating: number; max?: number }) {
  return (
    <div className="star-row">
      {Array.from({ length: max }).map((_, i) => {
        const filled = i < Math.floor(rating)
        const half = !filled && i < rating
        return (
          <span
            key={i}
            className={filled ? "star-icon" : half ? "star-icon-half" : "star-icon-empty"}
          >
            ★
          </span>
        )
      })}
    </div>
  )
}

export default function SellerProfilePage() {
  const { id } = useParams<{ id: string }>()
  const navigate = useNavigate()
  const [listings, setListings] = useState<Listing[]>([])
  const [loading, setLoading] = useState(true)
  const [sellerName, setSellerName] = useState("")
  const [memberSince, setMemberSince] = useState("")

  useEffect(() => {
    if (!id) return

    getListings({})
      .then((data) => {
        const all: Listing[] = data.listings || []
        const sellerId = parseInt(id)
        const sellerListings = all.filter((l) => l.seller_id === sellerId)

        setListings(sellerListings)

        if (sellerListings.length > 0) {
          setSellerName(sellerListings[0].seller.name)
          setMemberSince(sellerListings[0].seller.created_at)
        }
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
          <h1 className="detail-title" style={{ margin: 0 }}>{sellerName || "York Student"}</h1>

          <div className="seller-rating-row" style={{ display: 'flex', alignItems: 'center', gap: 8, margin: '8px 0' }}>
            <span className="detail-label" style={{ marginBottom: 0 }}>Rating</span>
            <StarRating rating={4} />
          </div>

          <div className="detail-label">
            Active since: {memberSince ? formatDate(memberSince) : "—"}
          </div>

          <button
            className="btn-red"
            style={{ width: "auto", marginTop: 12 }}
            onClick={() => navigate("/messages")}
          >
            Message Seller
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
    </div>
  )
}
